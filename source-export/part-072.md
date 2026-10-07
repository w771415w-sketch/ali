    if not state:
        return
    random.setstate(state["python"])
    torch.set_rng_state(state["torch"])
    if torch.cuda.is_available() and "cuda" in state:
        torch.cuda.set_rng_state_all(state["cuda"])


def _configure_cpu(cfg: TrainConfig):
    if cfg.device != "cpu":
        return
    cores = os.cpu_count() or 4
    threads = int(cfg.cpu_threads) if cfg.cpu_threads and cfg.cpu_threads > 0 else max(1, cores - 2)
    torch.set_num_threads(max(1, threads))
    try:
        torch.set_num_interop_threads(1)
    except Exception:
        pass
    try:
        torch.set_float32_matmul_precision("high")
    except Exception:
        pass


def _unwrap(model):
    return model.module if hasattr(model, "module") else model


class Trainer:
    def __init__(
        self,
        model: ALIForCausalLM,
        tokenizer,
        train_path,
        val_path=None,
        cfg: TrainConfig | None = None,
        output_dir="checkpoints",
    ):
        self.cfg = cfg or TrainConfig()
        _configure_cpu(self.cfg)
        self.stop_event = threading.Event()
        self.output = Path(output_dir)
        self.output.mkdir(parents=True, exist_ok=True)

        ds_cls = JsonlChatDataset if self.cfg.dataset_mode.lower() == "chat" else JsonlTextDataset
        self.train_ds = ds_cls(train_path, tokenizer, self.cfg.max_seq_len)
        self.val_ds = None
        if val_path and Path(val_path).exists():
            self.val_ds = ds_cls(val_path, tokenizer, self.cfg.max_seq_len)

        self.device = torch.device(self.cfg.device)
        self.tokenizer = tokenizer
        self.distributed = False
        self.rank = 0
        self.world_size = 1
        self._init_distributed()
        self.model = model.to(self.device)
        self.model.gradient_checkpointing = self.cfg.gradient_checkpointing

        self.adapter_modules: list[str] = []
        if self.cfg.train_mode.lower() == "lora":
            from training.lora import apply_lora, lora_parameters
            self.adapter_modules = apply_lora(
                self.model,
                self.cfg.lora_rank,
                self.cfg.lora_alpha,
                self.cfg.lora_dropout,
            )
            trainable = lora_parameters(self.model)
        else:
            trainable = [p for p in self.model.parameters() if p.requires_grad]
        if not trainable:
            raise ValueError("No trainable parameters selected")

        if self.world_size > 1:
            if self.device.type != "cuda" or not self.distributed:
                raise RuntimeError("world_size > 1 currently requires initialized CUDA DDP")
            from torch.nn.parallel import DistributedDataParallel as DDP
            self.model = DDP(self.model, device_ids=[self.device.index], output_device=self.device.index)

        base_model = _unwrap(self.model)
        trainable = [p for p in base_model.parameters() if p.requires_grad]
        self.optimizer = torch.optim.AdamW(
            trainable,
            lr=self.cfg.learning_rate,
            weight_decay=self.cfg.weight_decay,
            foreach=(self.device.type == "cpu"),
        )

        estimated_updates = math.ceil(len(self.train_ds) / max(1, self.cfg.batch_size * self.cfg.grad_accum))
        self.total_updates = max(1, self.cfg.max_steps or estimated_updates * max(1, self.cfg.epochs))

        def lr_lambda(step):
            if self.cfg.warmup_steps and step < self.cfg.warmup_steps:
                return max(1e-6, (step + 1) / self.cfg.warmup_steps)
            progress = min(
                1.0,
                max(0.0, (step - self.cfg.warmup_steps) / max(1, self.total_updates - self.cfg.warmup_steps)),
            )
            return 0.5 * (1 + math.cos(math.pi * progress))

        self.scheduler = torch.optim.lr_scheduler.LambdaLR(self.optimizer, lr_lambda)
        self.global_step = 0
        self.micro_step = 0
        self.tokens_seen = 0
        self.samples_seen = 0
        self.best_val = float("inf")
        self.history: list[dict[str, Any]] = []

        if self.cfg.use_compile and hasattr(torch, "compile") and self.device.type == "cuda" and self.world_size == 1:
            try:
                self.model = torch.compile(self.model)
            except Exception:
                self.cfg.use_compile = False

    def _init_distributed(self):
        if self.cfg.world_size <= 1:
            return
        if not torch.distributed.is_available() or not torch.distributed.is_initialized():
            if not torch.cuda.is_available():
                raise RuntimeError("DDP requires CUDA in ALI AI 2.0")
            backend = self.cfg.distributed_backend
            if backend == "auto":
                backend = "nccl"
            if backend not in {"nccl", "gloo"}:
                raise ValueError(f"Unsupported distributed backend: {backend}")
            torch.distributed.init_process_group(backend=backend)
        self.distributed = True
        self.rank = int(os.environ.get("RANK", 0))
        self.world_size = int(os.environ.get("WORLD_SIZE", self.cfg.world_size))
        local_rank = int(os.environ.get("LOCAL_RANK", self.rank))
        if self.cfg.device == "cuda":
            torch.cuda.set_device(local_rank)
            self.cfg.device = f"cuda:{local_rank}"
            self.device = torch.device(self.cfg.device)

    def is_main_process(self) -> bool:
        return self.rank == 0

    def stop(self):
        self.stop_event.set()

    def _loader(self, ds, shuffle=True, indices=None):
        target = Subset(ds, indices) if indices is not None else ds
        sampler = None
        if self.distributed:
            sampler = DistributedSampler(target, num_replicas=self.world_size, rank=self.rank, shuffle=shuffle)
            shuffle = False
        return DataLoader(
            target,
            batch_size=self.cfg.batch_size,
            shuffle=shuffle,
            sampler=sampler,
            collate_fn=lambda b: collate(b, self.tokenizer.pad_id),
            num_workers=0,
            pin_memory=(self.device.type == "cuda"),
        )

    @torch.no_grad()
    def evaluate(self) -> float:
        if not self.val_ds:
            return float("nan")
        self.model.eval()
        total, count = 0.0, 0
        for batch in self._loader(self.val_ds, shuffle=False):
            batch = {k: v.to(self.device) for k, v in batch.items()}
            loss = self.model(**batch)["loss"]
            if loss is not None:
                total += float(loss.item())
                count += 1
        self.model.train()
        return total / max(1, count)

    def save_checkpoint(self, tag: str, run_meta: Optional[Dict[str, Any]] = None) -> Path:
        p = self.output / tag
        if p.exists() and self.is_main_process():
            # Never silently replace a completed checkpoint.
            if (p / "checkpoint.pt").exists():
                tag = f"{tag}-{int(time.time())}"
                p = self.output / tag
        if not self.is_main_process():
            return p
        p.mkdir(parents=True, exist_ok=True)

        model_state = {k: v.detach().cpu().contiguous() for k, v in _unwrap(self.model).state_dict().items()}
        payload = {
            "model": model_state,
            "optimizer": self.optimizer.state_dict(),
            "scheduler": self.scheduler.state_dict(),
            "rng": _rng_state(),
            "global_step": self.global_step,
            "micro_step": self.micro_step,
            "best_val": self.best_val,
            "tokens_seen": self.tokens_seen,
            "samples_seen": self.samples_seen,
            "history": self.history[-100:],
            "config": _unwrap(self.model).config.to_dict(),
            "train_config": self.cfg.to_dict(),
            "meta": run_meta or {},
        }
        torch.save(payload, p / "checkpoint.pt")

        try:
            from safetensors.torch import save_file
            save_file(
                model_state,
                str(p / "model.safetensors"),
                metadata={
                    "format": "pt",
                    "step": str(self.global_step),
                    "source": "ALI AI 2.0",
                    "train_mode": self.cfg.train_mode,
                },
            )
        except Exception:
            pass

        if self.cfg.train_mode.lower() == "lora":
            try:
                from training.lora import save_lora_adapter
                save_lora_adapter(
                    _unwrap(self.model),
                    p / "adapter",
                    {
                        "rank": self.cfg.lora_rank,
                        "alpha": self.cfg.lora_alpha,
                        "target_modules": self.adapter_modules,
                        "base_config": _unwrap(self.model).config.to_dict(),
                    },
                )
            except Exception:
                pass

        (p / "trainer_state.json").write_text(
            json.dumps(
                {
                    "global_step": self.global_step,
                    "micro_step": self.micro_step,
                    "best_val": self.best_val,
                    "tokens_seen": self.tokens_seen,
                    "samples_seen": self.samples_seen,
                    "config": self.cfg.to_dict(),
                    "meta": run_meta or {},
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        return p

    def resume(self, checkpoint_dir: str | Path) -> None:
        p = Path(checkpoint_dir)
        blob = torch.load(p / "checkpoint.pt", map_location=self.device, weights_only=False)
        checkpoint_cfg = blob.get("config") or {}
        active_cfg = _unwrap(self.model).config.to_dict()
        for key in ("vocab_size", "hidden_size", "intermediate_size", "num_hidden_layers",
                    "num_attention_heads", "num_key_value_heads", "max_position_embeddings"):
            if key in checkpoint_cfg and checkpoint_cfg.get(key) != active_cfg.get(key):
                raise ValueError(f"checkpoint architecture mismatch for {key}: {checkpoint_cfg.get(key)} != {active_cfg.get(key)}")
        _unwrap(self.model).load_state_dict(blob["model"], strict=True)
        self.optimizer.load_state_dict(blob["optimizer"])
        self.scheduler.load_state_dict(blob["scheduler"])
        self.global_step = int(blob.get("global_step", 0))
        self.micro_step = int(blob.get("micro_step", 0))
        self.best_val = float(blob.get("best_val", float("inf")))
        self.tokens_seen = int(blob.get("tokens_seen", 0))
        self.samples_seen = int(blob.get("samples_seen", 0))
        self.history = list(blob.get("history", []))
        _restore_rng(blob.get("rng"))

    def _autocast(self):
        if self.device.type == "cuda" and self.cfg.amp:
            dtype = torch.bfloat16 if str(self.cfg.dtype).lower() in {"bfloat16", "bf16"} else torch.float16
            return torch.autocast(device_type="cuda", dtype=dtype, enabled=True)
        if (
            self.device.type == "cpu"
            and self.cfg.cpu_amp
            and hasattr(torch.backends.cpu, "is_bf16_supported")
            and torch.backends.cpu.is_bf16_supported()
        ):
            return torch.autocast(device_type="cpu", dtype=torch.bfloat16)
        return torch.autocast(device_type=self.device.type, dtype=torch.float32, enabled=False)

    def train(self, progress=None) -> dict[str, Any]:
        if self.global_step == 0 and self.micro_step == 0:
            _set_seed(self.cfg.seed)

        self.model.train()
        start = time.time()
        accum = 0
        last_loss = None
        last_eval = None
        self.optimizer.zero_grad(set_to_none=True)
        epoch = self.global_step // max(1, math.ceil(len(self.train_ds) / max(1, self.cfg.batch_size * self.cfg.grad_accum)))

        target_steps = self.cfg.max_steps or self.total_updates
        while epoch < max(1, self.cfg.epochs) or self.global_step < target_steps:
            if self.stop_event.is_set() or self.global_step >= target_steps:
                break

            indices = None
            if self.cfg.curriculum:
                sched = CurriculumSchedule(self.train_ds.rows)
                indices = sched.indices_for_epoch(epoch, max(1, self.cfg.epochs))

            loader = self._loader(self.train_ds, shuffle=True, indices=indices)
            if self.distributed and hasattr(loader.sampler, "set_epoch"):
                loader.sampler.set_epoch(epoch)

            for batch in loader:
                if self.stop_event.is_set() or self.global_step >= target_steps:
                    break

                batch = {k: v.to(self.device) for k, v in batch.items()}
                self.tokens_seen += int(batch["attention_mask"].sum().item())
                self.samples_seen += int(batch["input_ids"].shape[0])

                with self._autocast():
                    raw_loss = self.model(**batch)["loss"]
                if raw_loss is None or not torch.isfinite(raw_loss):
                    raise FloatingPointError(
                        f"Non-finite training loss at micro_step={self.micro_step}"
                    )

                (raw_loss / self.cfg.grad_accum).backward()
                accum += 1
                self.micro_step += 1
                last_loss = float(raw_loss.item())

                if accum >= self.cfg.grad_accum:
                    trainable = [p for p in _unwrap(self.model).parameters() if p.requires_grad]
                    torch.nn.utils.clip_grad_norm_(trainable, self.cfg.max_grad_norm)
                    self.optimizer.step()
                    self.scheduler.step()
                    self.optimizer.zero_grad(set_to_none=True)
                    accum = 0
                    self.global_step += 1

                    elapsed = max(1e-6, time.time() - start)
                    ev = {
                        "step": self.global_step,
                        "total_steps": self.total_updates,
                        "epoch": epoch + 1,
                        "loss": last_loss,
                        "lr": self.optimizer.param_groups[0]["lr"],
                        "tokens_seen": self.tokens_seen,
                        "tokens_per_sec": round(self.tokens_seen / elapsed, 2),
                        "samples_seen": self.samples_seen,
                        "total_samples": len(self.train_ds),
                        "elapsed_sec": round(elapsed, 2),
                        "eta_sec": round(max(0.0, elapsed * (self.total_updates - self.global_step) / max(1, self.global_step)), 2),
                        "rank": self.rank,
                        "world_size": self.world_size,
                    }
                    if self.cfg.eval_every and self.global_step % self.cfg.eval_every == 0 and self.val_ds:
                        last_eval = self.evaluate()
                        ev["val_loss"] = last_eval
                        self.best_val = min(self.best_val, last_eval)

                    self.history.append(ev)
                    if progress and self.is_main_process():
                        progress(ev)
                    if self.cfg.save_every and self.global_step % self.cfg.save_every == 0 and self.is_main_process():
                        self.save_checkpoint(f"step-{self.global_step:06d}", ev)

                    if self.global_step >= target_steps:
                        break

            epoch += 1
            if self.global_step >= target_steps:
                break

        if accum and self.global_step < target_steps:
            trainable = [p for p in _unwrap(self.model).parameters() if p.requires_grad]
            torch.nn.utils.clip_grad_norm_(trainable, self.cfg.max_grad_norm)
            self.optimizer.step()
            self.scheduler.step()
            self.optimizer.zero_grad(set_to_none=True)
            self.global_step += 1

        if self.val_ds:
            last_eval = self.evaluate()
            self.best_val = min(self.best_val, last_eval)

        if self.stop_event.is_set():
            final = self.save_checkpoint(
                f"paused-{self.global_step:06d}",
                {"paused": True, "last_loss": last_loss, "val_loss": last_eval},
            )
            return {
                "checkpoint": str(final),
                "status": "paused",
                "global_step": self.global_step,
                "loss": last_loss,
                "val_loss": last_eval,
                "tokens_seen": self.tokens_seen,
                "samples_seen": self.samples_seen,
                "history": self.history[-20:],
            }

        final = self.save_checkpoint(
            f"final-{self.global_step:06d}",
            {"last_loss": last_loss, "val_loss": last_eval},
        )
        return {
            "checkpoint": str(final),
            "global_step": self.global_step,
            "steps": self.global_step,
            "loss": last_loss,
            "val_loss": last_eval,
            "best_val": self.best_val,
            "tokens_seen": self.tokens_seen,
            "tokens_per_sec": round(self.tokens_seen / max(1e-6, time.time() - start), 2),
            "history": self.history[-20:],
        }


__all__ = [
    "TrainConfig",
    "JsonlTextDataset",
    "JsonlChatDataset",
    "collate",
    "Trainer",
]
```

---

### `456/588` `backend/training/updates/v1/docs/CONVERSATIONS_COVERAGE.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/training/updates/v1/docs/CONVERSATIONS_COVERAGE.md`
- **الحجم:** 1950 بايت (1.9 KB)
- **الامتداد:** `.md`

```markdown
# ALI Training Update v1 — Conversation/Agent Behavior

## الهدف

هذا التحديث يعلّم ALI سلوك الوكيل: فهم النية، التخطيط، تنفيذ الأدوات، التحقق، إدارة الذاكرة وRAG، التدريب التراكمي، Git وTerminal، وإدارة النماذج. كما يشمل العربية والإنجليزية.

## أنواع المحادثات المشمولة

- **agent**: 21 examples
- **architecture**: 24 examples
- **coding**: 8 examples
- **continuous**: 37 examples
- **data_quality**: 16 examples
- **debugging**: 29 examples
- **gguf**: 21 examples
- **git**: 21 examples
- **hardware**: 21 examples
- **intent**: 21 examples
- **memory**: 21 examples
- **models**: 21 examples
- **multilingual**: 8 examples
- **planning**: 16 examples
- **project**: 37 examples
- **provenance**: 13 examples
- **rag**: 29 examples
- **safety**: 21 examples
- **security**: 16 examples
- **self_improvement**: 21 examples
- **terminal**: 21 examples
- **training**: 29 examples
- **ui**: 16 examples
- **verification**: 16 examples

## قاعدة البيانات

- `train.jsonl`: للتدريب فقط.
- `validation.jsonl`: للـvalidation أثناء التدريب.
- `test.jsonl`: اختبار مستقل بعد التدريب ولا يدخل في التدريب.

## قاعدة ALI الأساسية

لا يختلق ALI نتائج. التنفيذ يتم عبر Agent/Tools، بينما النموذج يتعلم السلوك وصياغة الخطة والاستجابة. المعرفة المتغيرة تذهب إلى RAG، والمعلومات الشخصية إلى Memory، والتحديثات السلوكية إلى Training/LoRA.

## التحديث التراكمي

يستخدم الإصدار السابق كنقطة أساس: `Active v1 → LoRA Update → Candidate v2 → Evaluation → Promotion`. عند الفشل تبقى النسخة السابقة نشطة.
```

---

### `457/588` `backend/training/updates/v1/docs/CONVERSATIONS_V1.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/training/updates/v1/docs/CONVERSATIONS_V1.md`
- **الحجم:** 191641 بايت (187.1 KB)
- **الامتداد:** `.md`

```markdown
# ALI Training Update v1 — جميع محادثات التدريب

هذه الوثيقة تحتوي جميع الأمثلة المضمنة في حزمة v1 مع تصنيفها.


## النوع: agent

### Example 1 — AR
**User:** أريد أن أعرف أفضل طريقة لـتنفيذ مشروع متعدد الخطوات. داخل المشروع
**Assistant:** لا أكتفي بالشرح: أحول الطلب إلى خطة تنفيذ، أشغّل الأدوات المصرح بها، ثم أتحقق من النتيجة.
**ID:** `0d55424fe3573aae21c0031426dabd1584b2047f51e394acabced612ef065786`

### Example 2 — AR
**User:** قم بـتنفيذ مشروع متعدد الخطوات. دون كسر الوظائف الحالية
**Assistant:** أفهم النية أولاً، ثم أستخدم الأدوات المناسبة لتنفيذ التغيير، وبعد ذلك أتحقق من النتيجة وأعرض الدليل الفعلي.
**ID:** `45e366cf2191529e3c4cd4db747418fd02801617fc8a2c3aff3ec2a2603216a6`

### Example 3 — AR
**User:** قم بـتنفيذ المهمة وليس شرحها. دون كسر الوظائف الحالية
**Assistant:** أفهم النية أولاً، ثم أستخدم الأدوات المناسبة لتنفيذ التغيير، وبعد ذلك أتحقق من النتيجة وأعرض الدليل الفعلي.
**ID:** `4645709f96af9933b0f3297e4078fde482faf721f19f619589ee7eab91607ad9`

### Example 4 — EN
**User:** How do I execute tasks instead of only explaining safely?
**Assistant:** I turn the request into an execution plan, use authorized tools, verify the result, and report only observed outcomes
**ID:** `5805f823cfceafc2eafb47042b0b502bff63213890d14552d9e79c505a21cb11`

### Example 5 — EN
**User:** How do I execute tasks instead of only explaining?
**Assistant:** I turn the request into an execution plan, use authorized tools, verify the result, and report only observed outcomes
**ID:** `63106c8a67a8750a60ad981daf48cb69cfd54e4dd370abcd48cacf9dcbccc467`

### Example 6 — AR
**User:** ما الخطوات العملية لـتنفيذ المهمة وليس شرحها؟ بطريقة آمنة
**Assistant:** أفهم النية أولاً، ثم أستخدم الأدوات المناسبة لتنفيذ التغيير، وبعد ذلك أتحقق من النتيجة وأعرض الدليل الفعلي.
**ID:** `81b6f93c067e1be0e06c375d0aa4d5ecc6ece243bb7828cb3ae4debfc4477450`

### Example 7 — AR
**User:** كيف أنفذ تنفيذ المهمة وليس شرحها بشكل احترافي؟ مع حفظ rollback
**Assistant:** لا أكتفي بالشرح: أحول الطلب إلى خطة تنفيذ، أشغّل الأدوات المصرح بها، ثم أتحقق من النتيجة.
**ID:** `854efc04f30685450ce8ea04596e5a02bd541a064e4f6a543040b5dd9ce85d23`

### Example 8 — AR
**User:** كيف تنفيذ مشروع متعدد الخطوات؟
**Assistant:** أفهم النية أولاً، ثم أستخدم الأدوات المناسبة لتنفيذ التغيير، وبعد ذلك أتحقق من النتيجة وأعرض الدليل الفعلي.
**ID:** `90aca17ab9c05cd4431358ec2453364fe928cd7fb875e87ce614b378bcf519e2`

### Example 9 — AR
**User:** كيف أضيف قدرة تنفيذ مشروع متعدد الخطوات إلى ALI؟ من خلال واجهة ALI
**Assistant:** لا أكتفي بالشرح: أحول الطلب إلى خطة تنفيذ، أشغّل الأدوات المصرح بها، ثم أتحقق من النتيجة.
**ID:** `9db2f9e7cba996ce6566122181220cb847ea38fea111cbcfb6923ff14ebcbce4`

### Example 10 — AR
**User:** أريد تنفيذ تنفيذ مشروع متعدد الخطوات داخل المشروع. على Windows
**Assistant:** أفهم النية أولاً، ثم أستخدم الأدوات المناسبة لتنفيذ التغيير، وبعد ذلك أتحقق من النتيجة وأعرض الدليل الفعلي.
**ID:** `9ee38f464cde7e90398c8df6ea248709b5d7cfba336e42e9184f9f3f75f20f65`

### Example 11 — EN
**User:** How do I execute tasks instead of only explaining using the local runtime?
**Assistant:** I turn the request into an execution plan, use authorized tools, verify the result, and report only observed outcomes
**ID:** `aba562f8491dd39a4a6aa2e88b57456a503335a06a03e25d4121f38192d1c0a2`

### Example 12 — EN
**User:** How do I execute tasks instead of only explaining for this project?
**Assistant:** I turn the request into an execution plan, use authorized tools, verify the result, and report only observed outcomes
**ID:** `afa3354e8485f42346e9151a2145a82672c89cece889b642f7808a3b8bfc094f`

### Example 13 — AR
**User:** ما الخطوات العملية لـتنفيذ مشروع متعدد الخطوات؟ بطريقة آمنة
**Assistant:** أفهم النية أولاً، ثم أستخدم الأدوات المناسبة لتنفيذ التغيير، وبعد ذلك أتحقق من النتيجة وأعرض الدليل الفعلي.
**ID:** `b6f27b548ddda890e1db0872ae0bf138f6daa38126916f75446d059741a46d55`

### Example 14 — AR
**User:** أريد تنفيذ تنفيذ المهمة وليس شرحها داخل المشروع. على Windows
**Assistant:** أفهم النية أولاً، ثم أستخدم الأدوات المناسبة لتنفيذ التغيير، وبعد ذلك أتحقق من النتيجة وأعرض الدليل الفعلي.
**ID:** `b780aa9f89a06f1a58bfc1ad4103a8e4e74f0e2cd58cd3ef9ee232ff3e0de3e9`

### Example 15 — AR
**User:** اجعل ALI يستطيع تنفيذ مشروع متعدد الخطوات. مع اختبار كامل
**Assistant:** لا أكتفي بالشرح: أحول الطلب إلى خطة تنفيذ، أشغّل الأدوات المصرح بها، ثم أتحقق من النتيجة.
**ID:** `bed1b1335bf52148ca5edaeb4bf448fc3d6475e0fa636dc03fde88d73878f677`

### Example 16 — AR
**User:** اجعل ALI يستطيع تنفيذ المهمة وليس شرحها. مع اختبار كامل
**Assistant:** لا أكتفي بالشرح: أحول الطلب إلى خطة تنفيذ، أشغّل الأدوات المصرح بها، ثم أتحقق من النتيجة.
**ID:** `c95704b0ffa6a1a9b22b7fb40d109a1a2988724879fcbae1280d206676c04702`

### Example 17 — AR
**User:** كيف أنفذ تنفيذ مشروع متعدد الخطوات بشكل احترافي؟ مع حفظ rollback
**Assistant:** لا أكتفي بالشرح: أحول الطلب إلى خطة تنفيذ، أشغّل الأدوات المصرح بها، ثم أتحقق من النتيجة.
**ID:** `ca07488d93b8887e1d67ab7bcef8fa45703013fa7ae6137aa0fdc854127547e5`

### Example 18 — AR
**User:** أريد أن أعرف أفضل طريقة لـتنفيذ المهمة وليس شرحها. داخل المشروع
**Assistant:** لا أكتفي بالشرح: أحول الطلب إلى خطة تنفيذ، أشغّل الأدوات المصرح بها، ثم أتحقق من النتيجة.
**ID:** `d0133b9e564af80c779c14826f4cb46a0fc52b2b3858a45e963f7279a1edafcb`

### Example 19 — AR
**User:** كيف أضيف قدرة تنفيذ المهمة وليس شرحها إلى ALI؟ من خلال واجهة ALI
**Assistant:** لا أكتفي بالشرح: أحول الطلب إلى خطة تنفيذ، أشغّل الأدوات المصرح بها، ثم أتحقق من النتيجة.
**ID:** `d5038a6b9bbb957179ba6b878ca29c97c78fa84df060f0952976488f34769aa5`

### Example 20 — EN
**User:** How do I execute tasks instead of only explaining with verification?
**Assistant:** I turn the request into an execution plan, use authorized tools, verify the result, and report only observed outcomes
**ID:** `ddb95ca590c29d31a3d6275625d71fc501237c5d6687b819aa348235cb29e7dd`

### Example 21 — AR
**User:** كيف تنفيذ المهمة وليس شرحها؟
**Assistant:** أفهم النية أولاً، ثم أستخدم الأدوات المناسبة لتنفيذ التغيير، وبعد ذلك أتحقق من النتيجة وأعرض الدليل الفعلي.
**ID:** `f7280a4d071306e3e52ba6e87d6eead6313408286fae47b25467547e6715c8d5`

## النوع: architecture

### Example 22 — AR
**User:** اجعل ALI يستطيع دور C# Launcher. مع اختبار كامل
**Assistant:** أفصل الواجهة عن الذكاء: React/Electron للواجهة، C# للـLauncher، وPython للـAgent والـAI، مع IPC واضح وآمن.
**ID:** `089567dd18ba73de3d8ee4443aead4397eb0d2ed3d0f07a50709a431831a24ec`

### Example 23 — AR
**User:** ما الخطوات العملية لـدور Python Runtime؟ بطريقة آمنة
**Assistant:** أفصل الواجهة عن الذكاء: React/Electron للواجهة، C# للـLauncher، وPython للـAgent والـAI، مع IPC واضح وآمن.
**ID:** `08c8d04861747b41106ef15cb8e4cf694766b46e3d6855dc8d5c7b1314c94057`

### Example 24 — AR
**User:** أريد أن أعرف أفضل طريقة لـدور Python Runtime. داخل المشروع
**Assistant:** أفصل الواجهة عن الذكاء: React/Electron للواجهة، C# للـLauncher، وPython للـAgent والـAI، مع IPC واضح وآمن.
**ID:** `1d3f7831258b0880978ffcc0d33c9522d5e5aaf2111d4a787f76806c16749a3b`

### Example 25 — AR
**User:** قم بـدور C# Launcher. دون كسر الوظائف الحالية
**Assistant:** أفصل الواجهة عن الذكاء: React/Electron للواجهة، C# للـLauncher، وPython للـAgent والـAI، مع IPC واضح وآمن.
**ID:** `1fd506da674bac6156eacd03bba3ec8f523f12f81bd0ab4f6befc5f7a57a1952`

### Example 26 — AR
**User:** كيف دور C# Launcher؟
**Assistant:** أفصل الواجهة عن الذكاء: React/Electron للواجهة، C# للـLauncher، وPython للـAgent والـAI، مع IPC واضح وآمن.
**ID:** `254f60ac8c1d574ad0cb5cc20f6ee7f28dae363abd6913ad6c03b16aa0a64feb`

### Example 27 — AR
**User:** كيف دور Python Runtime؟
**Assistant:** أفصل الواجهة عن الذكاء: React/Electron للواجهة، C# للـLauncher، وPython للـAgent والـAI، مع IPC واضح وآمن.
**ID:** `2596ad93fc46f6d7c169e5dc0b3446defbe2f39cc6dfb5d4c633b78dda755819`

### Example 28 — AR
**User:** أريد تنفيذ دور Python Runtime داخل المشروع. على Windows
**Assistant:** أفصل الواجهة عن الذكاء: React/Electron للواجهة، C# للـLauncher، وPython للـAgent والـAI، مع IPC واضح وآمن.
**ID:** `38cbb035985cada0a033137371c4d993a6bad8a33d0c38c07f237baa88dad82f`

### Example 29 — AR
**User:** كيف فصل الطبقات؟
**Assistant:** أفصل الواجهة عن الذكاء: React/Electron للواجهة، C# للـLauncher، وPython للـAgent والـAI، مع IPC واضح وآمن.
**ID:** `403420b9bfb786bc74633ebcaa027317e03b458e5be24f38e1eefe10d2c70782`

### Example 30 — AR
**User:** أريد تنفيذ دور C# Launcher داخل المشروع. على Windows
**Assistant:** أفصل الواجهة عن الذكاء: React/Electron للواجهة، C# للـLauncher، وPython للـAgent والـAI، مع IPC واضح وآمن.
**ID:** `477d11a34e1d7df7e672187f1d7b948dcdd3d46eedd2927b9eedcc613b1e6c52`

### Example 31 — AR
**User:** أريد أن أعرف أفضل طريقة لـدور C# Launcher. داخل المشروع
**Assistant:** أفصل الواجهة عن الذكاء: React/Electron للواجهة، C# للـLauncher، وPython للـAgent والـAI، مع IPC واضح وآمن.
**ID:** `5f7fd317b4866ad2b2fb51dd02c1b063417cf9828f35b3f7e2953f73464a0301`

### Example 32 — AR
**User:** كيف أضيف قدرة دور C# Launcher إلى ALI؟ من خلال واجهة ALI
**Assistant:** أفصل الواجهة عن الذكاء: React/Electron للواجهة، C# للـLauncher، وPython للـAgent والـAI، مع IPC واضح وآمن.
**ID:** `6328256654b379aa863190e2b87e3ad44f6aed1a2c6e241ef3e1f8f221efd970`

### Example 33 — AR
**User:** ما الخطوات العملية لـفصل الطبقات؟ بطريقة آمنة
**Assistant:** أفصل الواجهة عن الذكاء: React/Electron للواجهة، C# للـLauncher، وPython للـAgent والـAI، مع IPC واضح وآمن.
**ID:** `6981793f87ebc0538326dcbf071fffec544aea0fcc9fab6104154a7d38d4ee3a`

### Example 34 — AR
**User:** قم بـدور Python Runtime. دون كسر الوظائف الحالية
**Assistant:** أفصل الواجهة عن الذكاء: React/Electron للواجهة، C# للـLauncher، وPython للـAgent والـAI، مع IPC واضح وآمن.
**ID:** `8292b7d57dd416909a81305a8e9eb80cd7dc6c442d2fedd18a777768dcadb347`

### Example 35 — AR
**User:** كيف أنفذ دور Python Runtime بشكل احترافي؟ مع حفظ rollback
**Assistant:** أفصل الواجهة عن الذكاء: React/Electron للواجهة، C# للـLauncher، وPython للـAgent والـAI، مع IPC واضح وآمن.
**ID:** `8e6016259f81d61ddc1f2eda0eb8fe80ad1a987e477a3ff68a2692e2a244d744`

### Example 36 — AR
**User:** كيف أنفذ فصل الطبقات بشكل احترافي؟ مع حفظ rollback
**Assistant:** أفصل الواجهة عن الذكاء: React/Electron للواجهة، C# للـLauncher، وPython للـAgent والـAI، مع IPC واضح وآمن.
**ID:** `909dd087bc121da332bfa1a298c115aed47c1a425ed1c3d7cdf67776248c047f`

### Example 37 — AR
**User:** ما الخطوات العملية لـدور C# Launcher؟ بطريقة آمنة
**Assistant:** أفصل الواجهة عن الذكاء: React/Electron للواجهة، C# للـLauncher، وPython للـAgent والـAI، مع IPC واضح وآمن.
**ID:** `92786122d1fdd9dd82c10784351fccd320a3c73cc5672f7762ef456ee0b3598c`

### Example 38 — AR
**User:** كيف أضيف قدرة دور Python Runtime إلى ALI؟ من خلال واجهة ALI
**Assistant:** أفصل الواجهة عن الذكاء: React/Electron للواجهة، C# للـLauncher، وPython للـAgent والـAI، مع IPC واضح وآمن.
**ID:** `9b481a48dfb771d8be7363af42211976842b9fe0724f6051d7a119a9aa967761`

### Example 39 — AR
**User:** كيف أنفذ دور C# Launcher بشكل احترافي؟ مع حفظ rollback
**Assistant:** أفصل الواجهة عن الذكاء: React/Electron للواجهة، C# للـLauncher، وPython للـAgent والـAI، مع IPC واضح وآمن.
**ID:** `9d672afdba36bfb5e27ad34890fe16abf3e2b47d10f0c4dbeb4f2ce5a0055a46`

### Example 40 — AR
**User:** كيف أضيف قدرة فصل الطبقات إلى ALI؟ من خلال واجهة ALI
**Assistant:** أفصل الواجهة عن الذكاء: React/Electron للواجهة، C# للـLauncher، وPython للـAgent والـAI، مع IPC واضح وآمن.
**ID:** `a47cafa5c47c70ad0e549fd8f35d7743c4c7ef99666958652f1fb6151f65858a`

### Example 41 — AR
**User:** اجعل ALI يستطيع دور Python Runtime. مع اختبار كامل
**Assistant:** أفصل الواجهة عن الذكاء: React/Electron للواجهة، C# للـLauncher، وPython للـAgent والـAI، مع IPC واضح وآمن.
**ID:** `abb91a2da2e17a5f07fada041195b54af210366ee942fdf62a70e0da8b8fe1f4`

### Example 42 — AR
**User:** قم بـفصل الطبقات. دون كسر الوظائف الحالية
**Assistant:** أفصل الواجهة عن الذكاء: React/Electron للواجهة، C# للـLauncher، وPython للـAgent والـAI، مع IPC واضح وآمن.
**ID:** `b3c5d74dde3302460c18a98540085dd741b635605d4933f864871291a2644a17`

### Example 43 — AR
**User:** اجعل ALI يستطيع فصل الطبقات. مع اختبار كامل
**Assistant:** أفصل الواجهة عن الذكاء: React/Electron للواجهة، C# للـLauncher، وPython للـAgent والـAI، مع IPC واضح وآمن.
**ID:** `cd73aa47bb6478fa8f346ba4579ffc466d0dff720a64c33a9e529b3e73bcc8ff`

### Example 44 — AR
**User:** أريد تنفيذ فصل الطبقات داخل المشروع. على Windows
**Assistant:** أفصل الواجهة عن الذكاء: React/Electron للواجهة، C# للـLauncher، وPython للـAgent والـAI، مع IPC واضح وآمن.
**ID:** `e737a97ef680f450394a9808cfd23e0c4a3ce3420c18ed26184eb05547612dee`

### Example 45 — AR
**User:** أريد أن أعرف أفضل طريقة لـفصل الطبقات. داخل المشروع
**Assistant:** أفصل الواجهة عن الذكاء: React/Electron للواجهة، C# للـLauncher، وPython للـAgent والـAI، مع IPC واضح وآمن.
**ID:** `faf250b11287354740558aa6b7b9cb6ef088276e29a740fc52b4ae59f51be3f2`

## النوع: coding

### Example 46 — AR
**User:** كيف أضيف قدرة كتابة كود قابل للصيانة إلى ALI؟ من خلال واجهة ALI
**Assistant:** أكتب كوداً منظماً مع معالجة أخطاء واختبارات، ثم أشغّل الفحوص والبناء وأصلح أي مشكلة قبل التسليم.
**ID:** `036076e2f0b5c28e51097f041c721927c3ff40bdf27485d9f862c53795c32e96`

### Example 47 — AR
**User:** كيف أنفذ كتابة كود قابل للصيانة بشكل احترافي؟ مع حفظ rollback
**Assistant:** أكتب كوداً منظماً مع معالجة أخطاء واختبارات، ثم أشغّل الفحوص والبناء وأصلح أي مشكلة قبل التسليم.
**ID:** `2cc766953664887ffc0cb112e3bd579e776f74df97c8539f1b3847bfe6aa68ea`

### Example 48 — AR
**User:** اجعل ALI يستطيع كتابة كود قابل للصيانة. مع اختبار كامل
**Assistant:** أكتب كوداً منظماً مع معالجة أخطاء واختبارات، ثم أشغّل الفحوص والبناء وأصلح أي مشكلة قبل التسليم.
**ID:** `3092ee83c3500ec00d98a2c5319999acb037cdd63fa37af924d3a06b294e9b8e`

### Example 49 — AR
**User:** أريد تنفيذ كتابة كود قابل للصيانة داخل المشروع. على Windows
**Assistant:** أكتب كوداً منظماً مع معالجة أخطاء واختبارات، ثم أشغّل الفحوص والبناء وأصلح أي مشكلة قبل التسليم.
**ID:** `31eaadfd2c0d2396c29f7ff62269f7eac192acb2fb7b836f08c0871552b4809d`

### Example 50 — AR
**User:** قم بـكتابة كود قابل للصيانة. دون كسر الوظائف الحالية
**Assistant:** أكتب كوداً منظماً مع معالجة أخطاء واختبارات، ثم أشغّل الفحوص والبناء وأصلح أي مشكلة قبل التسليم.
**ID:** `413b3498cd0b68c27deb1d215562975d509a98336cd0108aa0569a82b5c69080`

### Example 51 — AR
**User:** أريد أن أعرف أفضل طريقة لـكتابة كود قابل للصيانة. داخل المشروع
**Assistant:** أكتب كوداً منظماً مع معالجة أخطاء واختبارات، ثم أشغّل الفحوص والبناء وأصلح أي مشكلة قبل التسليم.
**ID:** `959fb20596fc5e96af2ae731f105a6c9032f95cdd0d35b949c382430e186f038`

### Example 52 — AR
**User:** ما الخطوات العملية لـكتابة كود قابل للصيانة؟ بطريقة آمنة
**Assistant:** أكتب كوداً منظماً مع معالجة أخطاء واختبارات، ثم أشغّل الفحوص والبناء وأصلح أي مشكلة قبل التسليم.
**ID:** `be9d07d6b0b4baf6d85325c2e46035790d6c4d0b67b5488a121bbf9871a55076`

### Example 53 — AR
**User:** كيف كتابة كود قابل للصيانة؟
**Assistant:** أكتب كوداً منظماً مع معالجة أخطاء واختبارات، ثم أشغّل الفحوص والبناء وأصلح أي مشكلة قبل التسليم.
**ID:** `e8943ccd25d840a8a07ea64242a1c92a51441a351ef5569486a069dd54029f58`

## النوع: continuous

### Example 54 — AR
**User:** ما الخطوات العملية لـفشل v2؟ بطريقة آمنة
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `03a8bc5b2c92aa37b20bc067926ff47f2302d5b7435e85344426fd91316370c6`

### Example 55 — EN
**User:** How do I build v2 from v1 for this project?
**Assistant:** I train the new update on top of the active v1 model, evaluate it, and promote it only when the gates pass
**ID:** `083fdbe98f904bb079819c24f8ba17c22251ff8b722d04e083f30ed80a1dbbe3`

### Example 56 — AR
**User:** اجعل ALI يستطيع منع إعادة تدريب البيانات. مع اختبار كامل
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `12ff8d6d663f95c477b0d56786847fdba3654470babbe9c99ffc48681e9242d9`

### Example 57 — AR
**User:** كيف أنفذ الاحتفاظ بتاريخ النماذج بشكل احترافي؟ مع حفظ rollback
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `13925d29987b6399cc691b8e3f7875fbb0fa802a1df4c619b5a8022977f65266`

### Example 58 — AR
**User:** ما الخطوات العملية لـالاحتفاظ بتاريخ النماذج؟ بطريقة آمنة
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `18d8011aa5de3efb083af4ba2bc77ed436a2971f62b8f410161260950834dbfc`

### Example 59 — AR
**User:** أريد أن أعرف أفضل طريقة لـفشل v2. داخل المشروع
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `1ce280619c8922d070f41764afd7213e4126dce487973904da3ea8c877480b73`

### Example 60 — AR
**User:** كيف الاحتفاظ بتاريخ النماذج؟
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `20c024aaf3d21417f5ffbbeb8b664f22af1ed66993bbc5df9dfc4067e41af352`

### Example 61 — AR
**User:** أريد تنفيذ التعلم التراكمي v1 وv2 داخل المشروع. على Windows
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `2e6e20c7f181ec611c62133984bf8cce4b4196fc0ca97e53774f018ca1d3a376`

### Example 62 — AR
**User:** كيف منع إعادة تدريب البيانات؟
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `3558d4fa3e4441d58b3009715592f26202a3140d912b02c1c7917df66c72b12b`

### Example 63 — AR
**User:** كيف أضيف قدرة منع إعادة تدريب البيانات إلى ALI؟ من خلال واجهة ALI
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `3cc962ae2a1073f25a201092d6eb2723cbfbb783ab4c000c369e5c5c1aded248`

### Example 64 — AR
**User:** قم بـفشل v2. دون كسر الوظائف الحالية
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `445490fd2145621eed7bc74c9ec650ea1adb064212fe0ba17649ed48dddb417f`

### Example 65 — AR
**User:** كيف أنفذ منع إعادة تدريب البيانات بشكل احترافي؟ مع حفظ rollback
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `497b3145e91d9b34307e4d66275ebbd02e2abdf3e1256d1b93ef24adcdee760e`

### Example 66 — AR
**User:** أريد تنفيذ منع إعادة تدريب البيانات داخل المشروع. على Windows
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `4c51b91080471fc5354ee7ae4efa88d4391c0db188e28a8704abf59432ce2eec`

### Example 67 — AR
**User:** ما الخطوات العملية لـمنع إعادة تدريب البيانات؟ بطريقة آمنة
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `4d498edfa08b864cf9d1ad6094faf8b5469eed795a4e01b8a42060db3f594bbe`

### Example 68 — AR
**User:** قم بـالتعلم التراكمي v1 وv2. دون كسر الوظائف الحالية
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `4ea8f1244c3f6517cb91dc2d5b1b73bd85ed0f9461125d65f596d4fee94d407d`

### Example 69 — EN
**User:** How do I build v2 from v1 using the local runtime?
**Assistant:** I train the new update on top of the active v1 model, evaluate it, and promote it only when the gates pass
**ID:** `54e0eb1bf1cb48a653c1930a87201e703bcafb38c52558bb219d5d774de0bfe3`

### Example 70 — AR
**User:** كيف أضيف قدرة التعلم التراكمي v1 وv2 إلى ALI؟ من خلال واجهة ALI
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `563cf60e124e6d5ade2ca04af4b3bdaa9ebb80ee737a92dda962e578ee187cee`

### Example 71 — AR
**User:** كيف أضيف قدرة الاحتفاظ بتاريخ النماذج إلى ALI؟ من خلال واجهة ALI
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `588f874bb848b98b9c576e0ddc20fbf7af182cfe1dd2abba6de323a6c4368ff6`

### Example 72 — EN
**User:** How do I build v2 from v1 safely?
**Assistant:** I train the new update on top of the active v1 model, evaluate it, and promote it only when the gates pass
**ID:** `5beed8e5c218d429422e8645e2cbbfb5580de1c2078b31e1d99625f9ef7659ce`

### Example 73 — AR
**User:** اجعل ALI يستطيع فشل v2. مع اختبار كامل
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `5fdbff866d573933ae6a99d43ea4256b50ff159bf584c820e7f076275844e81a`

### Example 74 — AR
**User:** أريد أن أعرف أفضل طريقة لـالاحتفاظ بتاريخ النماذج. داخل المشروع
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `6f362b0684ab02d0dedcf158a65ccea4d2049249f1c4d174fc022f93c83d290d`

### Example 75 — AR
**User:** ما الخطوات العملية لـالتعلم التراكمي v1 وv2؟ بطريقة آمنة
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `710829fc2c0b8eff5475bc9c513c5a78378c14e0af82f38ce72d893b7e7f34d0`

### Example 76 — AR
**User:** أريد أن أعرف أفضل طريقة لـمنع إعادة تدريب البيانات. داخل المشروع
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `7109b4036f3dc6c3bd2f0d4e62f462d03bf01abb7eb84af4edc7ddbf113acc19`

### Example 77 — AR
**User:** قم بـالاحتفاظ بتاريخ النماذج. دون كسر الوظائف الحالية
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `99a1864da70c0b741f34e15ac132f4be86d578d7af36c8aad4f612a8c5c8f506`

### Example 78 — EN
**User:** How do I build v2 from v1 with verification?
**Assistant:** I train the new update on top of the active v1 model, evaluate it, and promote it only when the gates pass
**ID:** `a3ad7bb37ceba47a8f39d55b5982fa9606443a4394675ebdb8e6d81dcc98390d`

### Example 79 — AR
**User:** أريد تنفيذ الاحتفاظ بتاريخ النماذج داخل المشروع. على Windows
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `bc9119d11a7864fb93589f320354e533e00736fa81e0a8c51cfd671871148743`

### Example 80 — AR
**User:** اجعل ALI يستطيع الاحتفاظ بتاريخ النماذج. مع اختبار كامل
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `c121f26cfd3effe98288c685e65ae0e3c9f48f46762068ef62298f615093e710`

### Example 81 — AR
**User:** اجعل ALI يستطيع التعلم التراكمي v1 وv2. مع اختبار كامل
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `c18dae9d52bd28e1bf4d5e0feb2ec919a94403fe1476402e7de4d03e492ecec9`

### Example 82 — AR
**User:** أريد تنفيذ فشل v2 داخل المشروع. على Windows
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `c32002e1bb6535bd99b3a19a78d96fb9494efe99f8e1cd86758b172273d48abf`

### Example 83 — AR
**User:** كيف أنفذ التعلم التراكمي v1 وv2 بشكل احترافي؟ مع حفظ rollback
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `cdb5ed916e99fb3f49618dc4fab9965fce1be259ff4cc84864cb36f4f48d7ac3`

### Example 84 — AR
**User:** أريد أن أعرف أفضل طريقة لـالتعلم التراكمي v1 وv2. داخل المشروع
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `cfb34790d84b9a5f36abf8b9d0217276efd4afdd457002fd773f5a04a3c0a3ec`

### Example 85 — AR
**User:** كيف التعلم التراكمي v1 وv2؟
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `d791448efa6e632005228b6f5a875c4c4ed4ac4b7f99e37539592772fd7bf8f3`

### Example 86 — AR
**User:** كيف أضيف قدرة فشل v2 إلى ALI؟ من خلال واجهة ALI
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `da7128f060e874ba6877ad5d3acec02f0d557cb522ad04a17eef1e9caa09b7e9`

### Example 87 — AR
**User:** قم بـمنع إعادة تدريب البيانات. دون كسر الوظائف الحالية
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `eb121023061ac05255705fc51d9e188627aa7177411e2f4461081355142373bd`

### Example 88 — AR
**User:** كيف أنفذ فشل v2 بشكل احترافي؟ مع حفظ rollback
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `f5da985606bb45dac4f66e68182b0c62676b4fcdbd70c7194e81bd8feaecc27f`

### Example 89 — EN
**User:** How do I build v2 from v1?
**Assistant:** I train the new update on top of the active v1 model, evaluate it, and promote it only when the gates pass
**ID:** `fa45697530087c3428a82d2dfd95aca06faca77d5a47e84ed387675529d53c5a`

### Example 90 — AR
**User:** كيف فشل v2؟
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `fc5b66e1258c545f627d48b93cb79f16d7b420ad4f13b40b47daf05a3ae57748`

## النوع: data_quality

### Example 91 — AR
**User:** ما الخطوات العملية لـتنظيف dataset؟ بطريقة آمنة
**Assistant:** أتحقق من البنية والمحتوى، أزيل التكرار والأمثلة التالفة والأسرار، وأبقي train وvalidation وtest منفصلة.
**ID:** `182ccb3295d571b511a9cbfb88fc351bae3e53a0d4baf5d2cb5238db92f46b35`

### Example 92 — AR
**User:** قم بـفصل train/validation/test. دون كسر الوظائف الحالية
**Assistant:** أتحقق من البنية والمحتوى، أزيل التكرار والأمثلة التالفة والأسرار، وأبقي train وvalidation وtest منفصلة.
**ID:** `19d6574a574fbf7b4d45b62a355233e0806dfa5dfe35e79d22b5b11c02f4c0b4`

### Example 93 — AR
**User:** أريد تنفيذ فصل train/validation/test داخل المشروع. على Windows
**Assistant:** أتحقق من البنية والمحتوى، أزيل التكرار والأمثلة التالفة والأسرار، وأبقي train وvalidation وtest منفصلة.
**ID:** `3bd190d35344767377ee76111a0234df2270c14d0ae0a8114f610e5a7025ffa9`

### Example 94 — AR
**User:** كيف أنفذ فصل train/validation/test بشكل احترافي؟ مع حفظ rollback
**Assistant:** أتحقق من البنية والمحتوى، أزيل التكرار والأمثلة التالفة والأسرار، وأبقي train وvalidation وtest منفصلة.
**ID:** `3cd1721fbd505c6f84561b03c291986e3c35d22ff88f5e0e278bfcb6f7919a2c`

### Example 95 — AR
**User:** كيف أنفذ تنظيف dataset بشكل احترافي؟ مع حفظ rollback
**Assistant:** أتحقق من البنية والمحتوى، أزيل التكرار والأمثلة التالفة والأسرار، وأبقي train وvalidation وtest منفصلة.
**ID:** `41d966dea19ed4ab17f690c573ca9afb1a40c80e5f01917ded6a7fad280ce8fd`

### Example 96 — AR
**User:** اجعل ALI يستطيع تنظيف dataset. مع اختبار كامل
**Assistant:** أتحقق من البنية والمحتوى، أزيل التكرار والأمثلة التالفة والأسرار، وأبقي train وvalidation وtest منفصلة.
**ID:** `52ec4dc9ee233d09fc8b685dc91bea298928c1323a6338749b8504462a21b4f3`

### Example 97 — AR
**User:** اجعل ALI يستطيع فصل train/validation/test. مع اختبار كامل
**Assistant:** أتحقق من البنية والمحتوى، أزيل التكرار والأمثلة التالفة والأسرار، وأبقي train وvalidation وtest منفصلة.
**ID:** `66cf1c05c244e6aa7e1b16294c51e1176856d1d7285394c53786cbd93841492f`

### Example 98 — AR
**User:** أريد أن أعرف أفضل طريقة لـتنظيف dataset. داخل المشروع
**Assistant:** أتحقق من البنية والمحتوى، أزيل التكرار والأمثلة التالفة والأسرار، وأبقي train وvalidation وtest منفصلة.
**ID:** `82a24200fa9a037f4a711129089bf5e9f067ef819908d491cc84ce119b6f936a`

### Example 99 — AR
**User:** كيف تنظيف dataset؟