        # drop into the Training Center.
        pairs_md = list(MARKDOWN_INLINE_ROLE_RE.finditer(text))
        if pairs_md:
            result = []
            for m in pairs_md:
                u = self._clean_role_content(m.group(2))
                a = self._clean_role_content(m.group(4))
                if u and a:
                    result.append([
                        {"role": "user", "content": u},
                        {"role": "assistant", "content": a},
                    ])
            if result:
                return result

        pairs = list(INLINE_ROLE_RE.finditer(text))
        if pairs:
            result = []
            for m in pairs:
                u = self._clean_role_content(m.group(2))
                a = self._clean_role_content(m.group(4))
                if u and a:
                    result.append([
                        {"role": "user", "content": u},
                        {"role": "assistant", "content": a},
                    ])
            if result:
                return result
        return []

    def _json_samples(self, obj: Any) -> list[list[dict[str, str]]]:
        items = obj if isinstance(obj, list) else [obj]
        out: list[list[dict[str, str]]] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            messages = item.get("messages")
            if isinstance(messages, list):
                clean = []
                for m in messages:
                    if not isinstance(m, dict):
                        continue
                    content = str(m.get("content", "")).strip()
                    role = ROLE_MAP.get(str(m.get("role", "user")).strip().lower(), str(m.get("role", "user")))
                    if content and role in {"system", "user", "assistant", "tool"}:
                        clean.append({"role": role, "content": content})
                if any(m["role"] == "user" for m in clean) and any(m["role"] == "assistant" for m in clean):
                    out.append(clean)
                    continue
            user = item.get("user", item.get("prompt", item.get("question")))
            assistant = item.get("assistant", item.get("response", item.get("answer")))
            if user is not None and assistant is not None:
                out.append([
                    {"role": "user", "content": str(user).strip()},
                    {"role": "assistant", "content": str(assistant).strip()},
                ])
        return [x for x in out if x[0].get("content") and x[-1].get("content")]

    @staticmethod
    def _extract_source_text(path: Path) -> str:
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            try:
                import fitz
                with fitz.open(path) as doc:
                    return "\n\n".join(page.get_text("text") for page in doc)
            except ImportError as exc:
                raise ValueError("pdf_requires_pymupdf") from exc
        if suffix == ".docx":
            try:
                with zipfile.ZipFile(path) as z:
                    xml = z.read("word/document.xml")
                root = ElementTree.fromstring(xml)
                parts = []
                for node in root.iter():
                    if node.tag.endswith("}t") and node.text:
                        parts.append(node.text)
                    elif node.tag.endswith("}p"):
                        parts.append("\n")
                return html.unescape(" ".join(parts))
            except (KeyError, zipfile.BadZipFile, ElementTree.ParseError) as exc:
                raise ValueError("invalid_docx") from exc
        if suffix in {".html", ".htm"}:
            try:
                from bs4 import BeautifulSoup
                return BeautifulSoup(path.read_text(encoding="utf-8", errors="replace"), "html.parser").get_text("\n")
            except ImportError:
                raw = path.read_text(encoding="utf-8", errors="replace")
                return re.sub(r"<[^>]+>", " ", raw)
        return path.read_text(encoding="utf-8", errors="replace")

    def parse_file(self, path: Path) -> tuple[list[list[dict[str, str]]], str, list[str]]:
        warnings: list[str] = []
        suffix = path.suffix.lower()
        raw = self._extract_source_text(path)
        safe, changed = redact_secrets(normalize_text(raw))
        if changed:
            warnings.append("secrets_redacted")
        if suffix in {".jsonl"}:
            samples = []
            for line in safe.splitlines():
                if not line.strip():
                    continue
                try:
                    samples.extend(self._json_samples(json.loads(line)))
                except Exception:
                    warnings.append("invalid_jsonl_line_ignored")
        elif suffix == ".json":
            try:
                samples = self._json_samples(json.loads(safe))
            except Exception as exc:
                raise ValueError(f"invalid_json:{exc}")
        elif suffix == ".csv":
            samples = []
            for row in csv.DictReader(safe.splitlines()):
                user = row.get("user") or row.get("prompt") or row.get("question")
                assistant = row.get("assistant") or row.get("response") or row.get("answer")
                if user and assistant:
                    samples.append([
                        {"role": "user", "content": str(user).strip()},
                        {"role": "assistant", "content": str(assistant).strip()},
                    ])
        else:
            samples = self._parse_messages(safe)
            stats = self._bundle_declared_stats(safe)
            actual_sections = len(re.findall(r'(?im)^\s*##\s*المحادثة\s+\d+\b', safe))
            if stats['declared_total'] is not None and stats['declared_total'] != actual_sections:
                warnings.append(f"declared_conversation_count_mismatch:{stats['declared_total']}!={actual_sections}")
            # Detect exact duplicate Q/A payloads inside a bundle; deduplication still
            # happens globally during import, but this warning explains why the accepted
            # sample count can be smaller than the number of headings.
            seen_ids=set(); dup_count=0
            for msg in samples:
                sid=self._sample_id(msg)
                if sid in seen_ids: dup_count += 1
                else: seen_ids.add(sid)
            if dup_count:
                warnings.append(f"duplicate_samples_in_file:{dup_count}")

        # A plain document is intentionally NOT turned into one giant "learn this" example.
        # That produces poor supervised data. Route it to RAG instead and ask the user to
        # provide explicit Q/A for weight training.
        if not samples:
            warnings.append("document_has_no_explicit_chat_pairs")
        return samples, safe, warnings

    def _sample_id(self, messages: list[dict[str, str]]) -> str:
        canonical = json.dumps(messages, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return normalized_hash(canonical)

    def _next_generation(self) -> str:
        maximum = 0
        for row in self.registry.list("ALI"):
            m = re.fullmatch(r"v(\d+)", str(row.get("version", "")))
            if m:
                maximum = max(maximum, int(m.group(1)))
        with self._connect() as c:
            for row in c.execute("SELECT generation FROM generations").fetchall():
                m = re.fullmatch(r"v(\d+)", str(row[0]))
                if m:
                    maximum = max(maximum, int(m.group(1)))
        return f"v{maximum + 1}"

    @staticmethod
    def _bundle_declared_stats(text: str) -> dict[str, int | None]:
        """Read optional bundle statistics without treating them as truth.

        Some hand/exported bundles contain a stale summary header. Import must always
        use the actual parsed conversations, but exposing a mismatch as a warning makes
        the Training Center transparent instead of silently hiding bad metadata.
        """
        def read_int(label: str):
            m=re.search(rf"{label}\s*:\s*\*\*(\d+)\*\*", text, flags=re.I)
            return int(m.group(1)) if m else None
        return {
            'declared_total': read_int('إجمالي المحادثات'),
            'declared_train': read_int('Train'),
            'declared_validation': read_int('Validation'),
            'declared_test': read_int('Test'),
        }

    # ---------------- import ----------------
    def import_files(self, paths: Iterable[str | Path]) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        with self._lock:
            for raw in paths:
                p = Path(raw).expanduser().resolve()
                if not p.exists() or not p.is_file():
                    results.append(ImportResult(False, str(p), "rejected", reason="file_not_found").to_dict())
                    continue
                if p.suffix.lower() not in SUPPORTED:
                    results.append(ImportResult(False, str(p), "rejected", reason="unsupported_training_format").to_dict())
                    continue
                source_hash = self._sha256_file(p)
                with self._connect() as c:
                    if c.execute("SELECT 1 FROM sources WHERE source_hash=?", (source_hash,)).fetchone():
                        results.append(ImportResult(False, str(p), "duplicate", source_hash=source_hash, reason="duplicate_source").to_dict())
                        continue
                try:
                    samples, safe, warnings = self.parse_file(p)
                except Exception as exc:
                    results.append(ImportResult(False, str(p), "rejected", source_hash=source_hash, reason=str(exc)).to_dict())
                    continue
                stored = self.validated / f"{source_hash[:16]}_{p.name}"
                stored.write_text(safe, encoding="utf-8")
                # Always index accepted material into RAG so new knowledge is immediately usable.
                # For explicit conversations, keep one Q/A pair per chunk and carry its
                # question/answer in metadata. This prevents a tiny model or a high-priority
                # generic FAQ from hijacking an exact user-training question.
                routed_to_rag = False
                if samples:
                    rag_chunks=[]; rag_meta=[]
                    for messages in samples:
                        users=[str(m.get('content','')).strip() for m in messages if str(m.get('role'))=='user' and str(m.get('content','')).strip()]
                        assistants=[str(m.get('content','')).strip() for m in messages if str(m.get('role'))=='assistant' and str(m.get('content','')).strip()]
                        question=users[-1] if users else ''
                        answer=assistants[-1] if assistants else ''
                        if not question or not answer:
                            continue
                        rag_chunks.append(f"**User:** {question}\n**Assistant:** {answer}")
                        rag_meta.append({'training_sample_id': self._sample_id(messages), 'training_question': question, 'training_answer': answer, 'priority': 180})
                    if rag_chunks:
                        self.knowledge.add_document(str(stored), p.name, "training-source", {"source_hash": source_hash, "priority": 180, "sample_count": len(rag_chunks)}, rag_chunks, chunk_metadata=rag_meta)
                        routed_to_rag = True
                else:
                    chunks = [safe[i:i + 1800] for i in range(0, len(safe), 1800) if safe[i:i + 1800].strip()]
                    if chunks:
                        self.knowledge.add_document(str(stored), p.name, "training-source", {"source_hash": source_hash}, chunks)
                        routed_to_rag = True

                seen = set()
                unique: list[list[dict[str, str]]] = []
                for messages in samples:
                    ident = self._sample_id(messages)
                    if ident in seen:
                        continue
                    with self._connect() as c:
                        exists = c.execute("SELECT 1 FROM samples WHERE sample_id=?", (ident,)).fetchone()
                    if exists:
                        warnings.append("duplicate_sample_skipped")
                        continue
                    seen.add(ident)
                    unique.append(messages)
                if not unique:
                    chash = normalized_hash(safe)
                    if samples:
                        # The file contains explicit training conversations, but every
                        # sample already exists in the persistent sample ledger. Do not
                        # mislabel this as RAG-only: the user supplied valid training
                        # data, it was simply already ingested in an earlier cycle.
                        reason = "all_samples_already_imported"
                        warnings.append(reason)
                        status = "duplicate"
                        result_ok = False
                        sample_count = len(samples)
                    else:
                        # RAG-only source: keep a source record but don't create fake training data.
                        reason = "no_explicit_chat_pairs"
                        status = "rag_only"
                        result_ok = True
                        sample_count = 0
                    with self._connect() as c:
                        c.execute(
                            "INSERT INTO sources(source_hash,content_hash,original_name,original_path,stored_path,batch_id,status,sample_count,characters,routed_to_rag,reason,warnings_json,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                            (source_hash, chash, p.name, str(p), str(stored), "", status, sample_count, len(safe), int(routed_to_rag), reason, json.dumps(warnings, ensure_ascii=False), time.time()),
                        )
                    results.append(ImportResult(result_ok, str(p), status, sample_count, len(safe), chash, source_hash, routed_to_rag=routed_to_rag, warnings=warnings, reason=("تمت إضافة الملف إلى المعرفة، لكن جميع عينات التدريب موجودة مسبقاً." if samples else "تمت إضافة الملف إلى المعرفة. لم توجد أزواج User/Assistant صريحة للتدريب.")).to_dict())
                    continue

                batch_id = f"batch-{time.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"
                batch_path = self.batches / f"{batch_id}.jsonl"
                lines = []
                for messages in unique:
                    lines.append(json.dumps({
                        "id": self._sample_id(messages),
                        "messages": [{"role": "system", "content": "You are ALI. Answer in the user's language and do not invent evidence."}, *messages],
                        "text": self._render_messages(messages),
                        "source": str(stored),
                        "source_hash": source_hash,
                        "content_hash": self._sample_id(messages),
                        "provenance": {"ingested_at": time.time(), "source_format": p.suffix.lower(), "warnings": warnings},
                    }, ensure_ascii=False))
                batch_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
                content_hash = normalized_hash("\n".join(x for x in lines))
                try:
                    with self._connect() as c:
                        cur = c.execute(
                            "INSERT INTO sources(source_hash,content_hash,original_name,original_path,stored_path,batch_id,status,sample_count,characters,routed_to_rag,reason,warnings_json,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                            (source_hash, content_hash, p.name, str(p), str(stored), batch_id, "validated", len(unique), len(safe), int(routed_to_rag), "", json.dumps(warnings, ensure_ascii=False), time.time()),
                        )
                        source_db_id = int(cur.lastrowid)
                        for messages in unique:
                            c.execute("INSERT INTO samples(sample_id,source_db_id,batch_id,created_at) VALUES(?,?,?,?)", (self._sample_id(messages), source_db_id, batch_id, time.time()))
                except sqlite3.IntegrityError:
                    results.append(ImportResult(False, str(p), "duplicate", source_hash=source_hash, content_hash=content_hash, reason="duplicate_content").to_dict())
                    continue
                results.append(ImportResult(True, str(p), "validated", len(unique), len(safe), content_hash, source_hash, batch_id, routed_to_rag=routed_to_rag, warnings=warnings).to_dict())
        return results

    # ---------------- status / dataset ----------------
    def _pending_rows(self) -> list[sqlite3.Row]:
        with self._connect() as c:
            return c.execute("SELECT * FROM sources WHERE status='validated' ORDER BY id").fetchall()

    def pending(self) -> list[dict[str, Any]]:
        return [dict(x) for x in self._pending_rows()]

    def status(self) -> dict[str, Any]:
        with self._connect() as c:
            counts = {row[0]: row[1] for row in c.execute("SELECT status, COUNT(*) FROM sources GROUP BY status").fetchall()}
            generations = c.execute("SELECT generation,base_version,status,evaluation_json,gguf_json,created_at FROM generations ORDER BY id DESC LIMIT 12").fetchall()
        return {
            **self._status,
            "pending_sources": int(counts.get("validated", 0)),
            "rag_only": int(counts.get("rag_only", 0)),
            "trained_sources": int(counts.get("trained", 0)),
            "rejected": int(counts.get("rejected", 0)),
            "duplicates": int(counts.get("duplicate", 0)),
            "generations": [dict(x) for x in generations],
            "active": self.registry.active("ALI"),
        }

    def _set_status(self, **updates: Any):
        with self._lock:
            self._status.update(updates)

    def _event(self, run_id: str, generation: str | None, phase: str, progress: float, status: str, message: str, payload: dict[str, Any] | None = None, callback: Callable[[dict[str, Any]], None] | None = None):
        event = {
            "run_id": run_id, "generation": generation, "phase": phase,
            "progress": max(0.0, min(1.0, float(progress))), "status": status,
            "message": message, "ts": time.time(), **(payload or {})
        }
        update = {"phase": phase, "progress": event["progress"], "message": message}
        payload_data = payload or {}
        for key in ("step", "total_steps", "samples_seen", "total_samples", "tokens_seen"):
            if key in payload_data and payload_data.get(key) is not None:
                update[key] = int(payload_data.get(key) or 0)
        for key in ("tokens_per_sec", "elapsed_sec", "eta_sec", "loss", "lr"):
            if key in payload_data and payload_data.get(key) is not None:
                update[key] = payload_data[key]
        self._set_status(**update)
        with self._connect() as c:
            c.execute(
                "INSERT INTO events(run_id,generation,ts,phase,progress,status,message,payload_json) VALUES(?,?,?,?,?,?,?,?)",
                (run_id, generation, event["ts"], phase, event["progress"], status, message, json.dumps(payload or {}, ensure_ascii=False)),
            )
        if callback:
            callback(event)

    def _error_correction_rows(self) -> list[dict[str, Any]]:
        rows = []
        for item in self.error_learning.corrections("approved", 100000):
            rows.append({
                "id": item["sample_id"],
                "messages": [
                    {"role": "system", "content": "You are ALI. Learn only from verified correction examples."},
                    *item["messages"],
                ],
                "text": f"<|system|>\nYou are ALI. Learn only from verified correction examples.<|eot|>\n"
                        f"<|user|>\n{item['user_text']}<|eot|>\n"
                        f"<|assistant|>\n{item['corrected_output']}<|eot|>\n",
                "source": "error-learning",
                "source_hash": item.get("fingerprint", ""),
                "content_hash": item["sample_id"],
                "provenance": {"source": "error-learning", "verified": True},
            })
        return rows

    def _historical_train_paths(self, parent_generation: str) -> list[Path]:
        """Resolve the parent cumulative dataset; fall back to verified ancestors only when needed."""
        result: list[Path] = []
        try:
            models_root = self.root / "models"
            if parent_generation:
                parent_path = generation_train_path(models_root, parent_generation)
                if parent_path and parent_path.exists():
                    return [parent_path]
                chain = [*build_ancestors(models_root, parent_generation), parent_generation]
            else:
                chain = []
            for gen in chain:
                path = generation_train_path(models_root, gen)
                if path and path.exists() and path not in result:
                    result.append(path)
        except Exception:
            pass
        return result

    def _build_dataset(self, rows: list[sqlite3.Row], run_dir: Path, parent_generation: str = "") -> tuple[Path, Path, Path, str, Path, Path, dict[str, Any]]:
        """Build both delta and cumulative datasets; training always consumes cumulative data."""
        delta_path = run_dir / "delta_train.jsonl"
        cumulative_path = run_dir / "cumulative_train.jsonl"
        new_samples: list[dict[str, Any]] = []
        for row in rows:
            batch = self.batches / f"{row['batch_id']}.jsonl"
            if not batch.exists():
                continue
            for line in batch.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    try:
                        new_samples.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        new_samples.extend(self._error_correction_rows())
        if not new_samples:
            # A generation can be rebuilt from its parent cumulative dataset after a retry.
            if not delta_path.exists():
                delta_path.write_text("", encoding="utf-8")
        else:
            # Deduplicate the new delta itself.
            temp = run_dir / "delta_raw.jsonl"
            temp.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in new_samples) + "\n", encoding="utf-8")
            merge_jsonl_unique([temp], delta_path)
            try:
                temp.unlink()
            except Exception:
                pass

        if not delta_path.exists() and not self._historical_train_paths(parent_generation):
            raise ValueError("no_train_samples")

        # Parent cumulative dataset(s) are the first inputs. Then the current delta.
        historical = self._historical_train_paths(parent_generation)
        inputs = [*historical, delta_path]
        merge_meta = merge_jsonl_unique(inputs, cumulative_path)
        train_path = cumulative_path

        stable_val = self.root / "data" / "training" / "device_p50" / "chat_validation.jsonl"
        val_path = run_dir / "stable_validation.jsonl"
        if stable_val.exists():
            val_path.write_text(stable_val.read_text(encoding="utf-8"), encoding="utf-8")
        else:
            val_path.write_text("", encoding="utf-8")

        # New-data holdout is derived only from current delta.
        delta_rows = list(iter_rows(delta_path)) if delta_path.exists() else []
        holdout_n = max(0, min(len(delta_rows) // 5, 20)) if len(delta_rows) >= 10 else 0
        holdout = delta_rows[-holdout_n:] if holdout_n else []
        new_val_path = run_dir / "new_data_validation.jsonl"
        new_val_path.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in holdout) + ("\n" if holdout else ""), encoding="utf-8")

        delta_hash = hashlib.sha256(delta_path.read_bytes()).hexdigest() if delta_path.exists() else ""
        cumulative_hash = hashlib.sha256(cumulative_path.read_bytes()).hexdigest()
        meta = {
            "parent_generation": parent_generation,
            "delta_dataset_hash": delta_hash,
            "cumulative_dataset_hash": cumulative_hash,
            "delta_samples": len(delta_rows),
            "cumulative_samples": int(merge_meta.get("written_rows", 0)),
            "duplicates_removed": int(merge_meta.get("duplicates_removed", 0)),
            "source_files": merge_meta.get("source_files", []),
        }
        return train_path, val_path, new_val_path, cumulative_hash, delta_path, cumulative_path, meta

    def _mark_generation_dataset(self, generation: str, kind: str, path: Path, dataset_hash: str, sample_count: int, parent_generation: str):
        with self._connect() as c:
            c.execute(
                "INSERT OR REPLACE INTO generation_datasets(generation,dataset_kind,path,dataset_hash,sample_count,parent_generation,created_at) VALUES(?,?,?,?,?,?,?)",
                (generation, kind, str(path), dataset_hash, int(sample_count), parent_generation, time.time()),
            )

    def _mark_sources(self, rows: list[sqlite3.Row], status: str, reason: str = ""):
        with self._connect() as c:
            for row in rows:
                c.execute("UPDATE sources SET status=?,reason=? WHERE id=?", (status, reason, row["id"]))

    # ---------------- actual continuous training ----------------
    def start(self, *, promote: bool = True, callback: Callable[[dict[str, Any]], None] | None = None, compute_mode: str = "auto") -> dict[str, Any]:
        with self._lock:
            if self._job_thread and self._job_thread.is_alive():
                return {"ok": False, "status": "running", "reason": "training_already_running"}
            rows = self._pending_rows()
            if not rows:
                return {"ok": False, "status": "waiting", "reason": "no_new_training_data"}
            active = self.registry.active("ALI")
            if not active:
                # Historical source reconstruction can bootstrap a first independent model.
                # The normal future path always uses the active parent model.
                active = {"version": "", "hf_dir": "", "checkpoint": ""}
            self._cancel.clear()
            generation = self._next_generation()
            run_id = f"continuous-{generation}-{time.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
            self._status = {"state": "running", "phase": "queued", "progress": 0.0, "message": "تم تجهيز دورة التعلم", "generation": generation, "started_at": time.time(), "finished_at": None, "error": None, "run_id": run_id, "step": 0, "total_steps": 0, "samples_seen": 0, "total_samples": 0, "tokens_seen": 0, "tokens_per_sec": 0.0, "elapsed_sec": 0.0, "eta_sec": None}
            self._status["compute_mode"] = str(compute_mode or "auto")
            self._job_thread = threading.Thread(target=self._run, args=(rows, active, generation, run_id, promote, callback, str(compute_mode or "auto")), daemon=True)
            self._job_thread.start()
            return {"ok": True, "status": "started", "generation": generation, "run_id": run_id, "base_version": active.get("version")}

    def cancel(self):
        self._cancel.set()
        return {"ok": True, "status": "cancelling"}

    def _run(self, rows: list[sqlite3.Row], active: dict[str, Any], generation: str, run_id: str, promote: bool, callback: Callable[[dict[str, Any]], None] | None, compute_mode: str):
        run_dir = self.runs / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        try:
            parent_generation = str(active.get("version") or (f"v{int(generation[1:]) - 1}" if generation.startswith("v") and generation[1:].isdigit() and int(generation[1:]) > 1 else ""))
            self._event(run_id, generation, "prepare", .05, "running", f"بدء {generation} من الأصل {parent_generation or 'bootstrap'}", callback=callback)
            train_path, val_path, new_val_path, dataset_hash, delta_path, cumulative_path, dataset_meta = self._build_dataset(rows, run_dir, parent_generation)
            if self._cancel.is_set():
                raise RuntimeError("cancelled_before_training")
            hw = detect(probe_torch=True, force=True)
            profile = training_profile(hw, mode=compute_mode)
            if str(profile.get("device")) == "cuda":
                budget = apply_cuda_memory_budget(float(profile.get("gpu_memory_fraction", 0.60) or 0.60))
                self._event(run_id, generation, "hardware", .12, "completed" if budget.get("ok") else "warning", "ميزانية VRAM تكيفية", {"budget": budget, "free_vram_gb": hw.gpu_mem_free_gb, "total_vram_gb": hw.vram_gb}, callback)
            cfg = PipelineConfig(
                name="ALI",
                stage="lora" if (active.get("hf_dir") or active.get("checkpoint")) else "base",
                scale=str(profile.get("scale", "micro")),
                train_path=str(train_path),
                validation_path=str(val_path),
                base_checkpoint=str(active.get("hf_dir") or active.get("checkpoint") or ""),
                max_steps=0,
                epochs=1,
                max_seq_len=max(64, min(256, int(profile.get("seq_len", 256)))),
                batch_size=1,
                grad_accum=max(1, min(16, int(profile.get("grad_accum", 16)))),
                learning_rate=3e-4,
                device=str(profile.get("device", "cpu")),
                lora_dropout=.05,
                curriculum=True,
                lora_rank=8 if float(hw.gpu_mem_free_gb or 0) < 1.35 else 16,
                lora_alpha=16.0 if float(hw.gpu_mem_free_gb or 0) < 1.35 else 32.0,
            )
            self._event(run_id, generation, "training", .15, "running", f"بدء التدريب على Dataset التراكمي لـ {generation}", {"samples": dataset_meta.get("cumulative_samples", 0), "delta_samples": dataset_meta.get("delta_samples", 0), "device": cfg.device, "scale": cfg.scale, "compute_mode": compute_mode, "gpu_util_percent": hw.gpu_util_percent, "free_vram_gb": hw.gpu_mem_free_gb}, callback)
            pipeline = TrainingPipeline(self.root, hardware=hw)
            result = pipeline.run(cfg, progress=lambda ev: self._pipeline_event(ev, run_id, generation, callback))
            if self._cancel.is_set():
                raise RuntimeError("cancelled_after_training")

            evaluation = dict(result.get("evaluation") or {})
            hf_dir = str(result.get("hf_dir") or "")
            checkpoint = str(result.get("checkpoint") or "")
            adapter = str(result.get("adapter") or "")
            if not hf_dir or not Path(hf_dir).exists():
                raise RuntimeError("candidate_hf_artifact_missing")
            if not evaluation or not math.isfinite(float(evaluation.get("loss", float("inf")))):
                raise RuntimeError("candidate_evaluation_invalid")

            self._mark_generation_dataset(generation, "delta", delta_path, dataset_meta.get("delta_dataset_hash", ""), int(dataset_meta.get("delta_samples", 0)), parent_generation)
            self._mark_generation_dataset(generation, "cumulative", cumulative_path, dataset_meta.get("cumulative_dataset_hash", dataset_hash), int(dataset_meta.get("cumulative_samples", 0)), parent_generation)

            # Evaluate on newly added holdout separately. The promotion baseline always uses
            # the same stable validation suite so v2 is compared with v1 fairly.
            new_eval: dict[str, Any] = {}
            if new_val_path.exists() and new_val_path.stat().st_size:
                try:
                    from tokenizer.spm import AliTokenizer
                    from model.ali_lm import AliConfig
                    from model.ali_lm import ALIForCausalLM
                    from model.ali_lm import load_state
                    tok_path = Path(hf_dir) / "tokenizer.model"
                    if tok_path.exists():
                        tok = AliTokenizer(tok_path)
                        pipe_for_eval = TrainingPipeline(self.root, hardware=hw)
                        eval_cfg = PipelineConfig(stage="lora", base_checkpoint=hf_dir, scale=cfg.scale, train_path=str(train_path), device=cfg.device)
                        eval_model = pipe_for_eval.new_model(eval_cfg, tok.vocab_size)
                        from training.evaluator import evaluate_model as eval_fn
                        new_eval = eval_fn(eval_model, tok, str(new_val_path), cfg.device)
                except Exception as exc:
                    new_eval = {"error": str(exc)}
            evaluation["new_data_holdout"] = new_eval

            baseline_eval = {}
            try:
                baseline_eval = json.loads(active.get("eval_json") or "{}")
            except Exception:
                baseline_eval = {}
            baseline_loss = baseline_eval.get("loss")
            # Bootstrap models are allowed to produce the first v1. Later generations must
            # not regress the stable validation holdout by more than 5%.
            if baseline_loss is None or not math.isfinite(float(baseline_loss)):
                regressions = {"passed": True, "reason": "no_usable_baseline"}
                gate = {"promote": True, "reason": "first learned generation with valid evaluation"}
            else:
                candidate_loss = float(evaluation.get("loss"))
                regressions = {"passed": candidate_loss <= float(baseline_loss) * 1.05, "candidate_loss": candidate_loss, "baseline_loss": float(baseline_loss), "max_regression": .05}
                gate = promotion_gate(evaluation, baseline_eval, regressions, min_improvement=-.05)
            model_status = "candidate"
            self._event(run_id, generation, "evaluate", .88, "completed", "انتهى التقييم وبوابة الترقية", {"evaluation": evaluation, "gate": gate}, callback)

            with self._connect() as c:
                c.execute("INSERT INTO generations(generation,base_version,run_id,dataset_hash,train_path,validation_path,checkpoint,hf_dir,adapter,evaluation_json,status,created_at,parent_generation,delta_dataset_hash,cumulative_dataset_hash,cumulative_sample_count) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                          (generation, str(active.get("version")), run_id, dataset_hash, str(train_path), str(val_path), checkpoint, hf_dir, adapter, json.dumps(evaluation, ensure_ascii=False), model_status, time.time(), parent_generation, dataset_meta.get("delta_dataset_hash", ""), dataset_meta.get("cumulative_dataset_hash", dataset_hash), int(dataset_meta.get("cumulative_samples", 0))))

            # Give the human-readable generation a stable alias in the main model registry.
            self.registry.register(
                "ALI", generation,
                artifact_type="merged",
                status="candidate",
                base_version=str(active.get("version")),
                checkpoint=checkpoint,
                hf_dir=hf_dir,
                adapter=adapter,
                dataset_hash=dataset_hash,
                tokenizer_hash="",
                artifact_hash="",
                train_config=cfg.to_dict(),
                eval={**evaluation, "generation": generation, "gate": gate},
                parent_generation=parent_generation,
                cumulative_dataset_hash=dataset_meta.get("cumulative_dataset_hash", dataset_hash),
            )

            if promote and bool(gate.get("promote")):
                self.registry.promote("ALI", generation)
                model_status = "active"
                if self.on_promotion:
                    try:
                        self.on_promotion(generation)
                    except Exception as exc:
                        self._event(run_id, generation, "promotion", .975, "warning", f"تم اعتماد {generation} لكن تعذر تحميله فوراً: {exc}", {"load_error": str(exc)}, callback)
                with self._connect() as c:
                    c.execute("UPDATE generations SET status='archived' WHERE generation<>? AND status='active'", (generation,))
                    c.execute("UPDATE generations SET status='active',promoted_at=? WHERE generation=?", (time.time(), generation))
                    for row in rows:
                        c.execute("UPDATE sources SET status='trained',reason='' WHERE id=?", (row["id"],))
                try:
                    correction_ids = [x.get("sample_id") for x in self.error_learning.corrections("approved", 100000)]
                    self.error_learning.mark_trained(correction_ids, generation)
                except Exception:
                    pass
                self._event(run_id, generation, "promotion", .97, "completed", f"{generation} تم اعتماده كنموذج Active", {"version": generation}, callback)
            else:
                with self._connect() as c:
                    c.execute("UPDATE generations SET status='candidate' WHERE generation=?", (generation,))
                self._event(run_id, generation, "promotion", .97, "waiting", f"{generation} مرشح ولم يتم اعتماده", {"gate": gate}, callback)

            gguf_info: dict[str, Any] = {}
            if model_status == "active":
                try:
                    from tools.gguf import GGUFManager
                    gguf_root = self.root / "vendor" / "llama.cpp"
                    gm = GGUFManager(gguf_root)
                    if gm.converter():
                        gguf_dir = self.generations / generation / "gguf"
                        f16 = gguf_dir / f"ALI-{generation}-F16.gguf"
                        q4 = gguf_dir / f"ALI-{generation}-Q4_K_M.gguf"
                        gguf_info["f16"] = gm.convert(hf_dir, f16, outtype="f16")
                        if gm.quantizer():
                            gguf_info["q4_k_m"] = gm.quantize(f16, q4, ftype="Q4_K_M")
                        self.registry.update_artifacts("ALI", generation, gguf=str(q4 if q4.exists() else f16), quantized=str(q4) if q4.exists() else "")
                    else:
                        gguf_info = {"status": "pending_converter", "llama_dir": str(gguf_root)}
                except Exception as exc:
                    gguf_info = {"status": "failed", "error": str(exc)}

            with self._connect() as c:
                c.execute("UPDATE generations SET gguf_json=? WHERE generation=?", (json.dumps(gguf_info, ensure_ascii=False), generation))

            generation_dir = self.generations / generation
            generation_dir.mkdir(parents=True, exist_ok=True)
            lineage = {
                "schema_version": 2,
                "generation": generation,
                "parent_generation": parent_generation,
                "ancestors": build_ancestors(self.root / "models", generation),
                "historical_base_version": active.get("version") or None,
                "delta_dataset": {"path": str(delta_path), "sha256": dataset_meta.get("delta_dataset_hash", ""), "samples": dataset_meta.get("delta_samples", 0)},
                "cumulative_dataset": {"path": str(cumulative_path), "sha256": dataset_meta.get("cumulative_dataset_hash", dataset_hash), "samples": dataset_meta.get("cumulative_samples", 0)},
                "artifacts": {"checkpoint": checkpoint, "adapter": adapter, "merged_hf": hf_dir, "gguf_f16": (gguf_info.get("f16") or {}).get("path", "") if isinstance(gguf_info.get("f16"), dict) else "", "gguf_q4_k_m": (gguf_info.get("q4_k_m") or {}).get("path", "") if isinstance(gguf_info.get("q4_k_m"), dict) else ""},
                "evaluation": evaluation,
                "gate": gate,
                "gguf": gguf_info,
                "status": model_status,
                "run_id": run_id,
                "created_at": time.time(),
            }
            (generation_dir / "generation.json").write_text(json.dumps(lineage, ensure_ascii=False, indent=2), encoding="utf-8")
            (generation_dir / "lineage.json").write_text(json.dumps(lineage, ensure_ascii=False, indent=2), encoding="utf-8")
            (generation_dir / "cumulative_report.json").write_text(json.dumps({**dataset_meta, "generation": generation, "parent_generation": parent_generation}, ensure_ascii=False, indent=2), encoding="utf-8")

            finished = time.time()
            self._status.update({"state": "completed", "phase": "done", "progress": 1.0, "message": f"اكتملت دورة {generation}", "finished_at": finished, "error": None, "eta_sec": 0, "elapsed_sec": round(finished - float(self._status.get("started_at") or finished), 2)})
            if callback:
                callback({"run_id": run_id, "generation": generation, "phase": "done", "progress": 1.0, "status": "completed", "message": f"اكتملت دورة {generation}"})
        except Exception as exc:
            error = str(exc)
            # Crucial: source status remains validated, so the failed batch can be retried.
            with self._connect() as c:
                c.execute("UPDATE generations SET status='failed',error=? WHERE generation=?", (error, generation))
            self._status.update({"state": "failed", "phase": "error", "progress": 1.0, "message": error, "finished_at": time.time(), "error": error})
            self._event(run_id, generation, "error", 1.0, "failed", error, callback=callback)

    def _pipeline_event(self, ev: dict[str, Any], run_id: str, generation: str, callback):
        st = str(ev.get("status", "running"))
        if st == "progress":
            inner = ev.get("event") or {}
            step = int(inner.get("step", 0) or 0)
            total_steps = int(inner.get("total_steps", 0) or 0)
            p = .15 + (.65 * min(1.0, step / total_steps) if total_steps else min(.65, .65 * step / max(1, step + 1)))
            msg = f"تدريب {generation}: الخطوة {step}/{total_steps or '—'} · loss={inner.get('loss', '—')}"
            eta = inner.get("eta_sec")
            if eta is not None:
                msg += f" · متبقٍ ~{max(0, int(eta))}ث"
            payload = {"event": inner}
            payload.update({k: inner[k] for k in ("step", "total_steps", "samples_seen", "total_samples", "tokens_seen", "tokens_per_sec", "elapsed_sec", "eta_sec", "loss", "lr") if k in inner})
            try:
                hw = detect(probe_torch=True)
                payload.update({"gpu_util_percent": hw.gpu_util_percent, "gpu_mem_used_gb": hw.gpu_mem_used_gb, "gpu_mem_free_gb": hw.gpu_mem_free_gb, "cuda_self_test": hw.cuda_self_test})
            except Exception:
                pass
            self._event(run_id, generation, "training", p, "running", msg, payload, callback)
        else:
            phase = str(ev.get("stage", "training"))
            p = .2 if phase == "tokenizer" else .82 if phase == "export" else .9 if phase == "complete" else .2
            self._event(run_id, generation, phase, p, st, f"{phase} · {st}", {k: v for k, v in ev.items() if k not in {"run_id", "stage", "status"}}, callback)

    # ---------------- versions ----------------
    def versions(self) -> list[dict[str, Any]]:
        rows = self.registry.list("ALI")
        out = []
        for row in rows:
            if str(row.get("version", "")).startswith("v"):
                item = dict(row)
                try:
                    item["evaluation"] = json.loads(item.get("eval_json") or "{}")
                except Exception:
                    item["evaluation"] = {}
                out.append(item)
        return out

    # ---------------- lifecycle ----------------
    def close(self) -> None:
        """Close all owned resources so temp dirs (and SQLite WAL files) can be deleted.

        Used by tests to make TemporaryDirectory cleanup deterministic on Windows.
        """
        try:
            if self.knowledge is not None and hasattr(self.knowledge, "close"):
                self.knowledge.close()
        except Exception:
            pass
        try:
            if self.error_learning is not None and hasattr(self.error_learning, "close"):
                self.error_learning.close()
        except Exception:
            pass
        try:
            if self.registry is not None and hasattr(self.registry, "close"):
                self.registry.close()
        except Exception:
            pass
        self._job_thread = None


__all__ = ["ContinuousLearningManager", "ImportResult"]
```

---

### `441/588` `backend/training/conversation.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/training/conversation.py`
- **الحجم:** 844 بايت (0.8 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Conversation-specialized ALI adaptation using real LoRA weights."""
from __future__ import annotations
from pathlib import Path
from typing import Any, Dict
import json
from model.ali_lm import ALIForCausalLM, AliConfig
from training.lora import apply_lora, save_lora_adapter, load_lora_adapter

def attach_conversation_adapter(model: ALIForCausalLM, rank:int=8, alpha:float=16.0, dropout:float=.05):
    return apply_lora(model,rank=rank,alpha=alpha,dropout=dropout)

def save_conversation_adapter(model, out_dir, meta:Dict[str,Any]|None=None):
    md={'specialization':'conversation','target':'assistant_response_and_tool_calling'}
    md.update(meta or {})
    return save_lora_adapter(model,out_dir,md)

def load_conversation_adapter(model, adapter_dir):
    load_lora_adapter(model,adapter_dir)
    return model
```

---

### `442/588` `backend/training/curriculum.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/training/curriculum.py`
- **الحجم:** 2291 بايت (2.2 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Deterministic curriculum scheduling for ALI training.

Samples receive a reproducible difficulty score from length, tool depth, code
complexity and language balance. The scheduler gradually exposes harder samples.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence, Mapping, Any
import hashlib, math, re

_AR=re.compile(r'[\u0600-\u06ff]')
_CODE=re.compile(r'(```|\b(def|class|import|SELECT|CREATE|function|const|try|except)\b)',re.I)
_TOOL=re.compile(r'"tool"\s*:|<tool_call>|<function_call>',re.I)

@dataclass(frozen=True)
class CurriculumConfig:
    warmup_fraction: float = 0.20
    mid_fraction: float = 0.55
    hard_fraction: float = 0.85
    min_score: float = 0.0
    max_score: float = 1.0

def score_record(row: Mapping[str, Any]) -> float:
    text=str(row.get('text') or '')
    words=max(1,len(text.split()))
    length=min(1.0, math.log1p(words)/math.log1p(600))
    turns=len(re.findall(r'<\|(?:system|user|assistant)\|>',text))
    tools=min(1.0, len(_TOOL.findall(text))/4.0)
    code=min(1.0, len(_CODE.findall(text))/8.0)
    arabic=1.0 if _AR.search(text) else 0.0
    # Blend breadth and complexity; avoid making very long noisy rows dominate.
    return round(min(1.0, 0.30*length+0.20*min(1.0,turns/8)+0.20*tools+0.20*code+0.10*arabic),6)

class CurriculumSchedule:
    def __init__(self, rows: Sequence[Mapping[str,Any]], cfg: CurriculumConfig|None=None):
        self.cfg=cfg or CurriculumConfig()
        enriched=[]
        for i,row in enumerate(rows):
            rid=str(row.get('id') or hashlib.sha256(str(row.get('text','')).encode('utf-8')).hexdigest())
            enriched.append((score_record(row),rid,i))
        enriched.sort(key=lambda x:(x[0],x[1]))
        self.indices=[x[2] for x in enriched]
        self.scores=[x[0] for x in enriched]

    def indices_for_epoch(self, epoch:int, epochs:int) -> list[int]:
        n=len(self.indices)
        if not n:return []
        progress=(epoch+1)/max(1,epochs)
        if progress <= self.cfg.warmup_fraction: frac=0.45
        elif progress <= self.cfg.mid_fraction: frac=0.70
        elif progress <= self.cfg.hard_fraction: frac=0.88
        else: frac=1.0
        take=max(1,int(n*frac))
        return self.indices[:take]
```

---

### `443/588` `backend/training/dataset.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/training/dataset.py`
- **الحجم:** 1801 بايت (1.8 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
from __future__ import annotations
from pathlib import Path
import json, sqlite3, hashlib
from typing import Dict, Any

def _write(rows, path):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8') as f:
        for r in rows: f.write(json.dumps(r,ensure_ascii=False)+'\n')

def build_chat_dataset(db_path:str|Path,out_dir:str|Path)->Dict[str,Any]:
    c=sqlite3.connect(db_path); c.row_factory=sqlite3.Row
    rows=c.execute("SELECT sample_hash,normalized FROM samples WHERE quality='ACCEPTED' AND role='conversation' ORDER BY id").fetchall(); c.close()
    out=Path(out_dir); n=len(rows); train_n=max(1,int(n*.9)) if n else 0; val_n=max(1,int(n*.05)) if n>=3 else max(0,n-train_n); train=rows[:train_n]; val=rows[train_n:train_n+val_n]; test=rows[train_n+val_n:]
    for name,part in [('train',train),('validation',val),('test',test)]: _write([{'id':r['sample_hash'],'text':r['normalized']} for r in part],out/f'chat_{name}.jsonl')
    return {'mode':'chat_sft','total':len(rows),'train':len(train),'validation':len(val),'test':len(test)}

def build_causal_dataset(db_path:str|Path,out_dir:str|Path)->Dict[str,Any]:
    c=sqlite3.connect(db_path); c.row_factory=sqlite3.Row
    rows=c.execute('SELECT chunk_hash,text FROM chunks ORDER BY id').fetchall(); c.close()
    data=[{'id':r['chunk_hash'],'text':r['text']} for r in rows if r['text'].strip()]
    out=Path(out_dir); n=len(data); nt=max(1,int(n*.9)) if n else 0; nv=max(1,int(n*.05)) if n else 0
    for name,part in [('train',data[:nt]),('validation',data[nt:nt+nv]),('test',data[nt+nv:])]: _write(part,out/f'cpt_{name}.jsonl')
    return {'mode':'continued_pretraining','total':n,'train':len(data[:nt]),'validation':len(data[nt:nt+nv]),'test':len(data[nt+nv:])}
```

---

### `444/588` `backend/training/evaluator.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/training/evaluator.py`
- **الحجم:** 1354 بايت (1.3 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
from __future__ import annotations
from pathlib import Path
from typing import Dict,Any
import json, math
import torch
from training.trainer import JsonlChatDataset, collate

def evaluate_model(model, tokenizer, path, device='cpu')->Dict[str,Any]:
    ds=JsonlChatDataset(path,tokenizer,model.config.max_position_embeddings); total=0.; n=0; model.to(device); model.eval()
    with torch.no_grad():
        for i in range(len(ds)):
            b=collate([ds[i]],tokenizer.pad_id); b={k:v.to(device) for k,v in b.items()}; out=model(**b); total+=float(out['loss'].item()); n+=1
    loss=total/max(1,n); return {'loss':loss,'perplexity':float(math.exp(min(20,loss))),'samples':n}

def promotion_gate(candidate:Dict[str,Any],baseline:Dict[str,Any]|None,regressions:Dict[str,Any],min_improvement:float=0.002)->Dict[str,Any]:
    tests_ok=bool(regressions.get('passed',False)); c=float(candidate.get('loss',float('inf'))); b=float((baseline or {}).get('loss',float('inf')))
    if not tests_ok: return {'promote':False,'reason':'regression tests failed'}
    if not math.isfinite(b): return {'promote':math.isfinite(c),'reason':'no baseline'}
    improved=c <= b*(1-min_improvement); return {'promote':improved,'reason':'validation loss improved' if improved else 'validation loss did not improve','candidate_loss':c,'baseline_loss':b}
```

---

### `445/588` `backend/training/examples/ALI_MASTER_TRAINING_4.5.2.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/training/examples/ALI_MASTER_TRAINING_4.5.2.json`
- **الحجم:** 320 بايت (0.3 KB)
- **الامتداد:** `.json`

```json
{
  "version": "4.5.2",
  "sources": [
    "ALI_Conversation_Training_Core_V2.md",
    "ALI_Conversation_Training_V1.md",
    "ALI_Professional_QA_P50_V2.md"
  ],
  "new_curated_cases": 30,
  "unique_conversation_blocks": 791,
  "dedup": "exact+normalized",
  "sensitive_machine_ids": "kept in knowledge profile only"
}
```

---

### `446/588` `backend/training/examples/ALI_MASTER_TRAINING_4.5.2.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/training/examples/ALI_MASTER_TRAINING_4.5.2.md`
- **الحجم:** 348411 بايت (340.2 KB)
- **الامتداد:** `.md`

```markdown
# ALI Master Training Dataset — 4.5.2

> Master conversation pack assembled from the project's prior conversation packs plus ThinkPad P50 / continuous-learning cases. Exact/normalized duplicate conversations are removed. Private machine identifiers remain in the Knowledge profile, not in generic training examples.

## Source packs
- ALI_Conversation_Training_Core_V2.md
- ALI_Conversation_Training_V1.md
- ALI_Professional_QA_P50_V2.md
- New curated 4.5.2 cases

## Intended routing
- Conversation/User/Assistant examples → training dataset
- Long reports, device facts, changing documentation → RAG/Knowledge
- User preferences and mutable facts → Memory

## Expected import
The ALI importer should extract each `User` + `Assistant` pair as a separate sample, hash/deduplicate it, and route the source to RAG as well.

---

## المحادثة 001 — intent
> النوع: `intent` · ID: `pending`

**User:** أريد منك تعديل المشروع.

**Assistant:** سأحدد أولاً ما الذي تريد تغييره وما الذي يجب أن يبقى دون تغيير، ثم أفحص البنية الحالية والملفات المتأثرة قبل اقتراح التنفيذ. لن أعتبر المهمة مكتملة حتى أتحقق من النتيجة الفعلية.

---
## المحادثة 002 — intent
> النوع: `intent` · ID: `pending`

**User:** طلبي غامض، هل تستطيع البدء؟

**Assistant:** أحتاج فقط إلى تحديد الهدف والنتيجة المطلوبة والقيود المهمة. إذا كانت معلومة حاسمة مفقودة فسأسأل سؤالاً محدداً بدلاً من التخمين.

---
## المحادثة 003 — intent
> النوع: `intent` · ID: `pending`

**User:** افهم هذه الجملة وحدد ما أريده.

**Assistant:** سأحوّل العبارة إلى هدف، وسياق، وقيود، ونتيجة متوقعة، ثم أختار الإجراء الأنسب. إذا كان هناك أكثر من تفسير معقول فسأذكره وأطلب اختياراً واحداً.

---
## المحادثة 004 — intent
> النوع: `intent` · ID: `pending`

**User:** أريد تنفيذ الطلب بالكامل وليس مجرد شرح.

**Assistant:** سأتعامل معه كمهمة تنفيذية: فحص، تخطيط، تعديل أو تشغيل، اختبار، تحقق، ثم عرض النتيجة. لن أكتفي بوصف الخطوات إذا كانت الأدوات المطلوبة متاحة.

---
## المحادثة 005 — intent
> النوع: `intent` · ID: `pending`
