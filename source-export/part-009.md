                    self.hermes_lbl.configure(text=("HERMES · CONNECTED" if hs.get("exists") else "HERMES · EXTERNAL"), fg=C["GREEN"] if hs.get("exists") else C["BLUE"])
                except Exception: pass
                self.rh_context.configure(text=f"context={self.ctx_var.get()} · output={self.out_var.get()}")
        finally:
            self.root.after(2000, self._refresh_jobs_loop)

    def _refresh_threads(self):
        self.thread_list.delete(0, "end")
        self.thread_ids = []
        for row in self.sessions.list_threads(self.project_id, 60):
            title = row.get("title") or "New conversation"
            self.thread_list.insert("end", title[:42])
            self.thread_ids.append(row["id"])

    def _refresh_models(self):
        self.model_list.delete(0, "end")
        rows = self.registry.list("ALI")
        for row in rows[:80]:
            typ = row.get("artifact_type", "base")
            marker = "*" if row.get("status") == "active" else " "
            self.model_list.insert(
                "end",
                f"{marker} {row['status']:<9} {typ:<7} {row['version']}",
            )
        active = self.registry.active("ALI")
        self.model_card.configure(
            text=json.dumps(
                {
                    "active": active["version"] if active else None,
                    "loadable": len(self.registry.list_loadable("ALI")),
                    "runtime_loaded": self.runtime.model_engine is not None,
                    "kca": self.kca.get("functions", 0),
                },
                ensure_ascii=False,
                indent=2,
            )
        )

    def _load_active(self, load_runtime: bool = False):
        active = self.registry.active("ALI")
        if not active:
            self.model_lbl.configure(text="MODEL · not trained")
            self.runtime.model_engine = None
            return
        self.model_lbl.configure(text=f"MODEL · {active['version']} · lazy")
        if not load_runtime:
            return
        self._ensure_active_model_loaded()

    # ---------- conversation ----------
    def _new_thread(self, silent=False):
        if silent:
            recent = self.sessions.latest_thread(self.project_id)
            if recent:
                self.current_thread = recent["id"]
                self.history = []
                self.chat.clear()
                self.title_lbl.configure(text=recent.get("title") or "Conversation")
                for msg in self.sessions.load_messages(self.current_thread):
                    if msg["role"] in ("user", "assistant"):
                        self.history.append({"role": msg["role"], "content": msg["content"]})
                    if msg["role"] == "user":
                        self.chat.add_message("user", msg["content"], on_copy=self._copy)
                    elif msg["role"] == "assistant":
                        self.chat.add_message("assistant", msg["content"], meta="saved", on_copy=self._copy)
                    elif msg["role"] == "tool":
                        self.chat.add_message("tool", msg["content"], meta="tool")
                return
        title = "New conversation"
        self.current_thread = self.sessions.new_thread(self.project_id, title)
        self.history = []
        self.chat.clear()
        self.title_lbl.configure(text=title)
        self._refresh_threads()
        if not silent:
            self._append_system("New conversation", meta="session")

    def _thread_selected(self, _event=None):
        sel = self.thread_list.curselection()
        if not sel:
            return
        tid = self.thread_ids[sel[0]]
        if tid == self.current_thread:
            return
        self.current_thread = tid
        row = self.thread_repo.get(tid) or {}
        self.title_lbl.configure(text=row.get("title") or "Conversation")
        self.history = []
        self.chat.clear()
        for msg in self.sessions.load_messages(tid):
            role = msg["role"]
            content = msg["content"]
            if role in ("user", "assistant"):
                self.history.append({"role": role, "content": content})
            if role == "user":
                self.chat.add_message("user", content, on_copy=self._copy)
            elif role == "assistant":
                self.chat.add_message("assistant", content, meta="saved", on_copy=self._copy)
            elif role == "tool":
                self.chat.add_message("tool", content, meta="tool")
        self._append_system("Conversation restored from local database.", meta="session")

    def send(self):
        if self.busy:
            return
        text = self.entry.get("1.0", "end-1c").strip()
        if not text:
            return
        self.entry.delete("1.0", "end")

        # Keep the exact user wording in the transcript, but normalize/correct it
        # before routing and model inference so typos and Arabic variants are understood.
        adapted = self.language_adapter.adapt(text, preferred_profile=self.cfg.get("language_profile", "ar-SA")) if self.language_adapter else {"normalized": text, "corrections": [], "detected": {"profile": "unknown"}}
        processing_text = str(adapted.get("normalized") or text)
        self._last_language_adaptation = adapted

        self.chat.add_message("user", text, on_copy=self._copy)
        self.history.append({"role": "user", "content": text})
        self.sessions.save_message(
            self.current_thread, "user", text,
            meta={"normalized": processing_text, "corrections": adapted.get("corrections", []), "detected_profile": adapted.get("detected", {}).get("profile")}
        )
        if adapted.get("corrections"):
            self._append_system(
                "تصحيح/تطبيع لغوي: " + ", ".join(
                    f"{x.get('from')} → {x.get('to')}" for x in adapted["corrections"]
                ),
                meta="language-adaptation",
            )

        try:
            envelope = RequestEnvelope(
                raw_text=processing_text, project_dir=self.project_dir, session_id=self.current_thread,
                language="auto", channel="desktop",
                metadata={"mode": self.ai_mode.get(), "language_profile": adapted.get("detected", {}).get("profile")}
            )
            kca_state = self.kca_router.build_state(envelope)
            self.intent_lbl.configure(
                text=f"{kca_state.intent} · {kca_state.confidence:.0%} · KCA"
            )
            plan = self.orchestrator.make_plan(processing_text)
            self.activity.event(
                f"تم تحليل الطلب: {kca_state.intent} · {kca_state.confidence:.0%}",
                phase="routing", progress=.08, status="ok"
            )
            self.activity.event(
                f"خطة التنفيذ: {len(plan.steps)} خطوة",
                phase="planning", progress=.12, status="ok"
            )
        except Exception as exc:
            self.intent_lbl.configure(text="chat")
            self._append_system(f"KCA routing fallback: {exc}", meta="kca-warning")

        try:
            hroute = self.hermes_router.route(processing_text)
            self._hermes_prompt_context = hroute.get("prompt_context", "") if hroute.get("used") else ""
            if hroute.get("used"):
                self._append_system("HERMES CONTEXT\n" + self._hermes_prompt_context, meta="hermes")
                self.status.configure(text="Hermes external context loaded · read-only")
            else:
                self._hermes_prompt_context = ""
        except Exception as exc:
            self._hermes_prompt_context = ""
            self._append_system(f"Hermes integration skipped: {exc}", meta="hermes-warning")

        self.busy = True
        self.cancel_requested = False
        if hasattr(self, "activity"): self.activity.event("User task received", phase="routing", progress=0.02, status="running")
        self.send_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        threading.Thread(target=self._reply_worker, daemon=True).start()

    def stop_generation(self):
        self.cancel_requested = True
        self.status.configure(text="Stopping generation…")
        self.stop_btn.configure(state="disabled")
        if hasattr(self, "activity"): self.activity.event("Generation stop requested", phase="control", progress=0, status="stopping")

    def _reply_worker(self):
        assistant_text = ""
        mode = "unknown"
        final = None
        bubble = None
        trace_lines: list[str] = []
        web_docs: list[dict] = []
        try:
            self._ensure_active_model_loaded()
            model_history = []
            for message in self.history:
                if message.get("role") == "user" and self.language_adapter:
                    fixed = self.language_adapter.correct_spelling(message.get("content", ""))
                    model_history.append({"role": "user", "content": fixed.get("text", message.get("content", ""))})
                else:
                    model_history.append(dict(message))
            for ev in self.runtime.stream_answer(
                model_history,
                self.project_dir,
                system_prompt=self._system_prompt(),
            ):
                if self.cancel_requested:
                    break
                kind = ev.get("type")
                if kind == "stage":
                    name = str(ev.get("name", "work"))
                    message = str(ev.get("message", "")).strip()
                    if message:
                        trace_lines.append(f"{name}: {message}")
                        self.root.after(0, lambda lines=list(trace_lines): self._update_stream_trace(lines))
                elif kind == "web":
                    data = ev.get("web") or {}
                    web_docs = [dict(d) for d in (data.get("documents") or []) if d.get("url")]
                    if web_docs:
                        trace_lines.append(f"web: تم العثور على {len(web_docs)} مصادر")
                        self.root.after(0, lambda lines=list(trace_lines): self._update_stream_trace(lines))
                        self.root.after(0, lambda docs=list(web_docs): self._update_stream_sources(docs))
                elif kind == "delta":
                    piece = sanitize_output(str(ev.get("text", "")))
                    assistant_text += piece
                    if piece and stream_safe(assistant_text, self.history[-1].get('content', '') if self.history else ""):
                        if bubble is None:
                            bubble = True
                            self.root.after(0, self._ensure_stream_bubble)
                        self.root.after(0, lambda p=assistant_text: self._update_stream(p))
                elif kind == "replace":
                    replacement = sanitize_output(str(ev.get("text", "")))
                    assistant_text = replacement
                    self.root.after(0, lambda p=replacement: self._update_stream(p))
                elif kind == "tool":
                    self.root.after(0, lambda e=ev: self._append_tool_event(e))
                elif kind == "final":
                    final = ev
                    mode = str(ev.get("mode", "model"))
                    web_final = ev.get("web") or {}
                    if isinstance(web_final, dict):
                        web_docs = [dict(d) for d in (web_final.get("documents") or []) if d.get("url")]
                    if ev.get("text") is not None:
                        assistant_text = sanitize_output(str(ev.get("text", "")))
            if final is not None and final.get("text") is not None:
                if final.get("mode") != "model" or not assistant_text:
                    assistant_text = str(final.get("text", ""))
                meta = {"mode": mode, "steps": trace_lines[-8:], "web": {"documents": web_docs} if web_docs else None}
                self.root.after(
                    0,
                    lambda: self._update_stream(assistant_text, final=True, mode=mode, meta=meta),
                )
            if not self.cancel_requested and assistant_text.strip():
                self.history.append({"role": "assistant", "content": assistant_text})
                self.sessions.save_message(
                    self.current_thread, "assistant", assistant_text,
                    meta={"mode": mode, "steps": trace_lines[-8:], "web": {"documents": web_docs} if web_docs else None},
                )
                self.root.after(0, lambda: self._post_answer(final or {}, mode))
        except Exception as exc:
            try:
                self.error_learning.record("desktop", str(exc), user_text=self.history[-1].get("content", "") if self.history else "", reason="runtime_exception")
            except Exception:
                pass
            self.root.after(0, lambda e=exc: self._append_system(f"تعذر تنفيذ الطلب: {e}", meta="error"))
        finally:
            self.busy = False
            self.root.after(0, self._generation_done)

    def _system_prompt(self):
        return (
            "You are ALI AI 2.5, a local-first professional assistant. "
            "Understand intent and context. Use tools only when required. "
            "Verify computer actions and never invent tool output. "
            "Separate memory, knowledge and learned weights. "
            "When uncertain, state uncertainty. "
            "For tools use the exact <tool_call> JSON contract. "
            "Treat request understanding as KCA state: intent, goal, candidate actions, observation, verification and recovery."
            + (("\n\nHERMES EXTERNAL CONTEXT (READ-ONLY):\n" + self._hermes_prompt_context) if self._hermes_prompt_context else "")
        )

    def _ensure_stream_bubble(self):
        if self.streaming_bubble is None:
            self.streaming_bubble = self.chat.add_message(
                "assistant", "", meta="يعمل الآن…", on_copy=self._copy
            )

    def _update_stream_trace(self, lines):
        if self.streaming_bubble is None:
            self._ensure_stream_bubble()
        try:
            self.streaming_bubble.set_trace(lines)
        except Exception:
            pass

    def _update_stream_sources(self, docs):
        if self.streaming_bubble is None:
            self._ensure_stream_bubble()
        try:
            self.streaming_bubble.add_web_sources(docs)
        except Exception:
            pass

    def _update_stream(self, text, final=False, mode="model", meta=None):
        if self.streaming_bubble is None:
            self._ensure_stream_bubble()
        self.streaming_bubble.set_text(text)
        if meta:
            steps = meta.get("steps") or []
            docs = ((meta.get("web") or {}).get("documents") or []) if isinstance(meta.get("web"), dict) else []
            self.streaming_bubble.set_trace(steps)
            self.streaming_bubble.add_web_sources(docs)
        if final:
            self.streaming_bubble.set_meta("الإجابة مكتملة · " + mode)
            self.last_assistant_bubble = self.streaming_bubble
            self.streaming_bubble = None
            self.intent_lbl.configure(text=f"Completed · {mode}")

    def _generation_done(self):
        self.busy = False
        self.send_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        if self.streaming_bubble is not None and not self.streaming_bubble.text.get("1.0", "end-1c").strip():
            self.streaming_bubble.destroy()
            try:
                self.chat.bubbles.remove(self.streaming_bubble)
            except ValueError:
                pass
        self.streaming_bubble = None

    def _post_answer(self, final, mode):
        web = final.get("web") or {}
        docs = [d for d in web.get("documents", []) if d.get("url")] if isinstance(web, dict) else []
        if docs:
            self.status.configure(text=f"تمت الإجابة بعد فحص {len(docs)} مصادر من الإنترنت داخل المحادثة")

    def _append_system(self, text, meta="system"):
        self.chat.add_message("system", str(text), meta=meta)

    def _append_tool_event(self, event):
        data = json.dumps(
            {"tool": event.get("tool"), "result": event.get("result")},
            ensure_ascii=False, indent=2,
        )
        self.chat.add_message("tool", data, meta="tool")
        self.sessions.save_message(self.current_thread, "tool", data, meta={"tool": event.get("tool")})

    def _copy(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(str(text))
        self.status.configure(text="Copied to clipboard")

    # ---------- workspace/editor ----------
    def _choose_dir(self):
        path = filedialog.askdirectory(initialdir=self.project_dir)
        if not path:
            return
        self.project_dir = os.path.abspath(path)
        self.project_id = self.sessions.ensure_project(self.project_dir, Path(path).name)
        self.cfg["last_dir"] = self.project_dir
        save_cfg(self.cfg)
        self.workspace_lbl.configure(text=Path(self.project_dir).name)
        self._new_thread(silent=True)
        self.populate_tree()

    def populate_tree(self):
        self.tree.delete(*self.tree.get_children())
        root_id = self.tree.insert("", "end", text=Path(self.project_dir).name or self.project_dir, open=True, values=(self.project_dir,))

        def walk(parent, path, depth=0):
            if depth > 3:
                return
            try:
                entries = sorted(
                    path.iterdir(),
                    key=lambda p: (p.is_file(), p.name.lower())
                )
            except Exception:
                return
            for child in entries:
                if child.name in {".git", ".venv", "__pycache__", ".pytest_cache", "models.sqlite3"}:
                    continue
                iid = self.tree.insert(
                    parent, "end",
                    text=child.name,
                    values=(str(child),),
                    open=False,
                )
                if child.is_dir():
                    walk(iid, child, depth + 1)

        walk(root_id, Path(self.project_dir))

    def open_selected_file(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        path = Path(self.tree.item(sel[0], "values")[0])
        if not path.is_file():
            return
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception as exc:
            text = f"ERROR: {exc}"
        self.editor.set(text[:2_000_000])
        self.editor_path = path
        self.nb.select(self.editor_tab)

    def _choose_editor_file(self):
        path = filedialog.askopenfilename(initialdir=self.project_dir)
        if path:
            self.editor.set(Path(path).read_text(encoding="utf-8", errors="replace"))
            self.editor_path = Path(path)
            self.nb.select(self.editor_tab)

    def save_editor(self):
        if not self.editor_path:
            messagebox.showwarning(APP, "No file selected.")
            return
        ctx = ConversationContext(
            "editor", self.project_dir,
            self.runtime.permission_manager.mode, "ALI", "High",
            tool_registry=self.runtime.registry,
        )
        tool = self.runtime.registry.get("write_file")
        decision = self.runtime.permission_manager.check(
            tool_name="write_file", permission=tool.permission,
            ctx=ctx, kwargs={"path": str(self.editor_path)},
        )
        if decision.needs_ask and not messagebox.askyesno(
            "Permission", f"Allow saving {self.editor_path.name}?"
        ):
            return
        if not decision.allowed and not decision.needs_ask:
            messagebox.showerror(APP, decision.reason or "Permission denied")
            return
        if decision.needs_ask:
            self.runtime.permission_manager.grant("write_file", session=True)
        self.editor_path.write_text(self.editor.get(), encoding="utf-8")
        self.populate_tree()
        self.status.configure(text=f"Saved {self.editor_path}")

    def revert_editor(self):
        if self.editor_path and self.editor_path.exists():
            self.editor.set(self.editor_path.read_text(encoding="utf-8", errors="replace"))

    # ---------- tools / agent ----------
    def _dispatch_tool(self, text):
        ctx = ConversationContext(
            "compat", self.project_dir,
            self.runtime.permission_manager.mode, "ALI", "High",
            tool_registry=self.runtime.registry,
        )
        return self.runtime.tool_dispatch(text, ctx)

    def _local_reply(self, text):
        return self.runtime.answer(
            [{"role": "user", "content": text}],
            self.project_dir,
        ).get("text", "")

    def _agent_reply(self, text):
        ctx = ConversationContext(
            "agent", self.project_dir,
            self.runtime.permission_manager.mode, "ALI", "High",
            tool_registry=self.runtime.registry,
        )
        desc = [
            {"name": n, "description": t.description, "input_schema": t.input_schema}
            for n, t in self.runtime.registry.all().items()
        ]
        result = AgentLoop(self.runtime, max_steps=8).run(
            [{"role": "user", "content": text}], ctx, desc
        )
        return result.get("text", "")

    # ---------- training ----------
    def train_dialog(self):
        w = tk.Toplevel(self.root)
        w.title("ALI AI 2.5 · Training Center")
        w.geometry("820x760")
        w.configure(bg=C["BG"])

        tk.Label(
            w, text="PROGRESSIVE REAL TRAINING",
            bg=C["BG"], fg=C["INK"], font=("Segoe UI Semibold", 14),
        ).pack(anchor="w", padx=18, pady=(16, 2))
        tk.Label(
            w,
            text="Tokenizer → Base → SFT → LoRA → Evaluation → Model Registry",
            bg=C["BG"], fg=C["MUTED"], font=("Segoe UI", 9),
        ).pack(anchor="w", padx=18, pady=(0, 12))

        form = tk.Frame(w, bg=C["PANEL"], highlightbackground=C["LINE"], highlightthickness=1)
        form.pack(fill="x", padx=16, pady=8)

        fields = {}
        rows = [
            ("Stage", "stage", "base"),
            ("Scale", "scale", str(self.train_profile.get("scale", "small"))),
            ("Train JSONL", "train", str(ROOT / "data" / "training" / "device_p50" / "chat_train.jsonl")),
            ("Validation JSONL", "val", str(ROOT / "data" / "training" / "device_p50" / "chat_validation.jsonl")),
            ("Base checkpoint/HF", "base", ""),
            ("Resume checkpoint", "resume", ""),
            ("Epochs", "epochs", "1"),
            ("Max steps (0=epochs)", "steps", "0"),
            ("Sequence length", "seq", str(self.train_profile.get("seq_len", 256))),
            ("Batch", "batch", str(self.train_profile.get("batch_size", 1))),
            ("Grad accumulation", "accum", str(self.train_profile.get("grad_accum", 16))),
            ("Learning rate", "lr", "0.0003"),
        ]
        for label, key, value in rows:
            row = tk.Frame(form, bg=C["PANEL"])
            row.pack(fill="x", padx=10, pady=4)
            tk.Label(row, text=label, width=23, anchor="w", bg=C["PANEL"], fg=C["MUTED"]).pack(side="left")
            if key in {"stage", "scale"}:
                choices = ["base", "sft", "lora"] if key == "stage" else list(PROFILES)
                var = tk.StringVar(value=value)
                ttk.Combobox(row, textvariable=var, values=choices, state="readonly").pack(side="left", fill="x", expand=True)
                fields[key] = var
            else:
                ent = tk.Entry(row, bg=C["PANEL_2"], fg=C["INK"], insertbackground=C["INK"], relief="flat")
                ent.insert(0, value)
                ent.pack(side="left", fill="x", expand=True)
                fields[key] = ent

        preview = tk.Text(
            w, bg=C["EDITOR"], fg=C["INK"], relief="flat",
            font=("Consolas", 8), height=11,
        )
        preview.pack(fill="both", expand=True, padx=16, pady=8)

        def build_plan_view(*_):
            try:
                hp = build_training_plan(fields["scale"].get(), self.hardware)
                preview.delete("1.0", "end")
                preview.insert("1.0", json.dumps(hp, ensure_ascii=False, indent=2))
            except Exception as exc:
                preview.delete("1.0", "end")
                preview.insert("1.0", str(exc))

        fields["scale"].trace_add("write", build_plan_view)
        build_plan_view()

        def start():
            payload = {k: v.get() for k, v in fields.items()}
            w.destroy()
            self._start_pipeline(payload)

        buttons = tk.Frame(w, bg=C["BG"])
        buttons.pack(fill="x", padx=16, pady=8)
        self._button(buttons, "Start training job", start, side="right", accent=True)
        self._button(buttons, "Cancel", w.destroy, side="right")

    def _start_pipeline(self, f):
        from training.pipeline import PipelineConfig
        self._ensure_model_services()
        train = str(Path(f["train"]).resolve())
        val = str(Path(f["val"]).resolve()) if f.get("val") else ""
        base = str(Path(f["base"]).resolve()) if f.get("base") else ""
        resume = str(Path(f["resume"]).resolve()) if f.get("resume") else ""

        selected_method = str(self.cfg.get("training_method", "lora_continue_cpu"))
        stage_map = {
            "lora_cpu": "lora",
            "lora_continue_cpu": "lora",
            "continued_sft_cpu": "sft",
            "full_finetune_micro_cpu": "base",
        }
        selected_stage = stage_map.get(selected_method, str(f.get("stage", "lora")))
        if selected_method in {"lora_continue_cpu", "continued_sft_cpu"} and not resume:
            active = self.registry.active("ALI")
            candidate = (active or {}).get("checkpoint") or (active or {}).get("hf_dir") or ""
            if candidate:
                candidate_path = Path(candidate)
                resume = str(candidate_path if candidate_path.is_absolute() else (ROOT / candidate_path).resolve())
                if not Path(resume).exists():
                    resume = ""

        def work(progress):
            cfg = PipelineConfig(
                name="ALI",
                stage=selected_stage,
                scale=f["scale"],
                train_path=train,
                validation_path=val,
                base_checkpoint=base,
                resume_checkpoint=resume,
                max_steps=max(0, int(f["steps"])),
                epochs=max(1, int(f["epochs"])),
                max_seq_len=max(32, int(f["seq"])),
                batch_size=max(1, int(f["batch"])),
                grad_accum=max(1, int(f["accum"])),
                learning_rate=float(f["lr"]),
                device=self.train_profile["device"],
            )
            return self.pipeline.run(
                cfg,
                progress=lambda ev: progress(
                    f"{ev.get('stage')} · {ev.get('status')}",
                    .95 if ev.get("status") == "success" else .5,
                ),
            )

        job = self.jobs.run("ALI progressive training", work, "training")
        if hasattr(self, "activity"): self.activity.event(f"Training queued [{job.id[:8]}]", phase="training", progress=0.0, status="queued")
        self.status.configure(text=f"Training queued [{job.id[:8]}]")
        self.nb.select(self.jobs_tab)

    def accumulated_training_dialog(self):
        w=tk.Toplevel(self.root); w.title("ALI AI 2.5 · Training Files"); w.geometry("1120x820"); w.minsize(900,680); w.configure(bg=C["BG"])
        top=tk.Frame(w,bg=C["BG"]); top.pack(fill="x",padx=14,pady=12)
        tk.Label(top,text="ملفات التدريب التراكمي" if self.rtl else "Accumulated Training Files",bg=C["BG"],fg=C["INK"],font=("Segoe UI Semibold",14)).pack(side="left")
        self.acc_status=tk.Label(top,text="",bg=C["SOFT"],fg=C["GREEN"],font=("Segoe UI Semibold",8),padx=10,pady=5); self.acc_status.pack(side="right")
        drop=tk.Frame(w,bg=C["PANEL_2"],highlightbackground=C["LINE"],highlightthickness=1,height=120); drop.pack(fill="x",padx=14,pady=6); drop.pack_propagate(False)
        tk.Label(drop,text="DROP .MD TRAINING FILES HERE" if not self.rtl else "اسحب ملفات Markdown التدريبية إلى هنا",bg=C["PANEL_2"],fg=C["MUTED"],font=("Segoe UI Semibold",11)).pack(expand=True)
        list_frame=tk.Frame(w,bg=C["BG"]); list_frame.pack(fill="both",expand=True,padx=14,pady=8)
        cols=("file","status","samples","size","hash")
        table=ttk.Treeview(list_frame,columns=cols,show="headings")
        for c,h in zip(cols,("File","Status","Samples","Size","Content SHA256")): table.heading(c,text=h)
        table.column("file",width=300); table.column("status",width=130); table.column("samples",width=80); table.column("size",width=100); table.column("hash",width=420)
        table.pack(side="left",fill="both",expand=True)
        sb=ttk.Scrollbar(list_frame,orient="vertical",command=table.yview); sb.pack(side="right",fill="y"); table.configure(yscrollcommand=sb.set)
        log=tk.Text(w,height=8,bg=C["EDITOR"],fg=C["INK"],font=("Consolas",8),relief="flat"); log.pack(fill="x",padx=14,pady=6)
        def refresh():
            table.delete(*table.get_children()); st=self.accumulated_training.status(); ready=st['merge_ready']; self.acc_status.configure(text=f"Adapters: {st['pending_adapters']} / {st['merge_threshold']} · {'MERGE READY' if ready else 'ACCUMULATING'}")
            with self.accumulated_training._connect() as c:
                for r in c.execute("SELECT * FROM sources ORDER BY id DESC LIMIT 120").fetchall():
                    table.insert('', 'end', values=(r['original_name'],r['status'],r['samples'],r['characters'],r['content_hash'][:32]+'…'))
        def add():
            paths=filedialog.askopenfilenames(filetypes=[("Markdown","*.md *.markdown")]);
            if not paths:return
            results=self.accumulated_training.add_files(paths)
            log.insert('end',json.dumps(results,ensure_ascii=False,indent=2)+'\n'); refresh()
        def run_update():
            batches=self.accumulated_training.pending_batch_paths()
            if not batches:
                messagebox.showinfo(APP,"لا توجد ملفات جديدة صالحة للتدريب." if self.rtl else "No new validated training files."); return
            active=self.registry.active('ALI')
            if not active:
                messagebox.showwarning(APP,"تحتاج إلى نموذج ALI أساسي/نشط قبل التدريب التراكمي." if self.rtl else "An active ALI base model is required before accumulated training."); return
            def work(progress):
                _manager, pipeline, _pipe = self._ensure_model_services()
                merged=self.accumulated_training.batches/'current_accumulated.jsonl'
                seen=set(); written=0
                with merged.open('w',encoding='utf-8') as out:
                    for batch in batches:
                        for line in batch.read_text(encoding='utf-8').splitlines():
                            if not line.strip():continue
                            obj=json.loads(line); ident=str(obj.get('content_hash') or obj.get('id') or '')
                            if not ident or ident in seen:continue
                            seen.add(ident); out.write(json.dumps(obj,ensure_ascii=False)+'\n'); written+=1
                from training.pipeline import PipelineConfig
                base=active.get('hf_dir') or active.get('checkpoint') or ''
                if base and not Path(base).is_absolute():
                    base=str((ROOT / base).resolve())
                cfg=PipelineConfig(name='ALI',stage='lora',scale=str(self.cfg.get('training',{}).get('scale','micro')),train_path=str(merged),validation_path='',base_checkpoint=str(base),max_steps=max(1,int(self.cfg.get('training',{}).get('auto_learning_steps',1))),epochs=1,max_seq_len=192,batch_size=1,grad_accum=1,learning_rate=1e-4,device=str(self.train_profile.get('device','cpu')),lora_rank=8,lora_alpha=16.0,lora_dropout=.05,curriculum=True)
                progress('training update',.15)
                result=pipeline.run(cfg,progress=lambda ev: progress(f"{ev.get('stage')} · {ev.get('status')}", .55 if ev.get('status')=='progress' else .35))
                adapter_path=result.get('adapter')
                if not adapter_path:
                    raise RuntimeError('Training pipeline completed without producing a LoRA adapter.')
                aid=self.accumulated_training.register_adapter(adapter_path,base_version=str(active.get('version','')),dataset_hash=result.get('manifest',{}).get('lineage',{}).get('dataset_hash',''),metadata={'run_id':result.get('run_id'),'samples':written})
                self.accumulated_training.mark_sources_as_adapterized(batches)
                progress('adapter pending',.7,adapter_id=aid)
                merge=self.accumulated_training.merge_pending(active)
                if merge.get('status') == 'candidate':
                    candidate=Path(merge['output']).resolve()
                    candidate_version=f"accumulated-{merge['merge_id']}"
                    self.registry.register(
                        'ALI', candidate_version, artifact_type='merged', status='candidate',
                        base_version=str(active.get('version','')), checkpoint=str(candidate), hf_dir=str(candidate),
                        train_config={'kind':'accumulated_merge','adapter_ids':merge.get('adapter_ids',[]),'run_id':result.get('run_id')},
                        eval={'status':'pending'}, metadata={'accumulated_merge_id':merge['merge_id']},
                    )
                    merge['registry_version']=candidate_version
                progress('accumulated update complete',1.0,merge=merge)
                return {'samples':written,'adapter_id':aid,'merge':merge,'run_id':result.get('run_id')}
            job=self.jobs.run("ALI accumulated training update",work,"training")
            self.status.configure(text=f"Accumulated training queued [{job.id[:8]}]"); self.activity.event(f"Accumulated training queued [{job.id[:8]}]",phase="training",progress=0,status="queued"); w.after(500,refresh)
        bar=tk.Frame(w,bg=C["BG"]); bar.pack(fill="x",padx=14,pady=8)
        self._button(bar,"Add Markdown Files",add,side="left",accent=True); self._button(bar,"Run Training Update",run_update,side="left"); self._button(bar,"Refresh",refresh,side="left"); self._button(bar,"Close",w.destroy,side="right")
        try:
            from tkinterdnd2 import DND_FILES, TkinterDnD
            if hasattr(drop,'drop_target_register'):
                drop.drop_target_register(DND_FILES); drop.dnd_bind('<<Drop>>',lambda e:self.accumulated_training_drop_paths(e.data,add,log,refresh))
        except Exception:
            pass
        refresh()

    def accumulated_training_drop_paths(self,data,add_callback,log,refresh_callback):
        raw=str(data).strip(); paths=[]; cur=''; in_brace=False
        for ch in raw:
            if ch=='{': in_brace=True; cur=''
            elif ch=='}': in_brace=False; paths.append(cur); cur=''
            elif ch.isspace() and not in_brace:
                if cur: paths.append(cur); cur=''
            else: cur+=ch
        if cur: paths.append(cur)
        results=self.accumulated_training.add_files([p for p in paths if p.lower().endswith(('.md','.markdown'))]); log.insert('end',json.dumps(results,ensure_ascii=False,indent=2)+'\n'); refresh_callback()

    # ---------- data / knowledge ----------
    def dataset_dialog(self):
        self.knowledge_dialog()

    def knowledge_dialog(self):
        w = tk.Toplevel(self.root)
        w.title("ALI AI 2.5 · Dataset + Knowledge")
        w.geometry("940x700")
        w.configure(bg=C["BG"])

        path_var = tk.StringVar(value=self.project_dir)
        tk.Entry(
            w, textvariable=path_var, bg=C["PANEL_2"],
            fg=C["INK"], insertbackground=C["INK"], relief="flat",
        ).pack(fill="x", padx=16, pady=12)

        out = tk.Text(
            w, bg=C["EDITOR"], fg=C["INK"], relief="flat",
            font=("Consolas", 8),
        )
        out.pack(fill="both", expand=True, padx=16, pady=8)

        def run():
            def work(progress):
                from data_engine.harvester import Harvester
                from training.dataset import build_chat_dataset, build_causal_dataset
                from knowledge.ingest import ingest_harvest
                db = ROOT / "artifacts" / "harvest.sqlite3"
                progress("harvesting", .1)
                stats = Harvester(db).scan(path_var.get())
                progress("building datasets", .45)
                chat = build_chat_dataset(db, ROOT / "data" / "training")
                causal = build_causal_dataset(db, ROOT / "data" / "training")
                progress("indexing knowledge", .8)
                knowledge = ingest_harvest(db, ROOT / "runtime_knowledge.sqlite3")
                progress("done", 1)
                return {
                    "harvest": stats,
                    "chat_dataset": chat,
                    "causal_dataset": causal,
                    "knowledge": knowledge,
                }

            job = self.jobs.run("Harvest + Dataset + Knowledge", work, "dataset")
            out.insert("end", f"Queued job {job.id[:8]}\n")

        self._button(w, "Scan · Dedup · Build · Ingest", run, accent=True)

    # ---------- models / weights ----------
    def models_dialog(self):
        self.nb.select(self.model_tab)
        self._refresh_models()

    def import_weights(self):
        _manager, weights, _pipeline = self._ensure_model_services()
        paths = filedialog.askopenfilenames(
            initialdir=str(self.weights.models_root / "inbox"),
            filetypes=[
                ("ALI/HF weights", "*.safetensors *.pt *.pth *.bin"),
                ("GGUF", "*.gguf"),
                ("All files", "*.*"),
            ],
        )
        if not paths:
            return
        for raw in paths:
            try:
                result = weights.install(raw, name="ALI")
                self.model_list.insert("end", f"IMPORTED  {result['type']}  {result['version']}")
            except Exception as exc:
                messagebox.showerror(APP, f"Import failed:\n{raw}\n\n{exc}")

    def import_weights_folder(self):
        _manager, weights, _pipeline = self._ensure_model_services()
        path = filedialog.askdirectory(initialdir=str(self.weights.models_root / "inbox"))
        if not path:
            return
        try:
            info = weights.install(path, name="ALI")
            messagebox.showinfo(APP, f"Installed {info['type']}:\n{info['path']}")
            self._refresh_models()
        except Exception as exc:
            messagebox.showerror(APP, str(exc))

    def _selected_model_row(self):
        sel = self.model_list.curselection()
        rows = self.registry.list("ALI")
        if not sel or sel[0] >= len(rows):
            return None
        return rows[sel[0]]

    def verify_selected_model(self):
        _manager, weights, _pipeline = self._ensure_model_services()
        from tools.gguf import GGUFManager
        row = self._selected_model_row()
        if not row:
            return
        path = row.get("hf_dir") or row.get("adapter") or row.get("gguf") or row.get("checkpoint")
        if not path:
            messagebox.showwarning(APP, "No artifact path.")
            return
        data = weights.verify(path) if Path(path).is_dir() else GGUFManager().validate(path)
        messagebox.showinfo(APP, json.dumps(data, ensure_ascii=False, indent=2))

    def promote_selected_model(self):
        from training.evaluator import promotion_gate
        from autonomy.improvement import ImprovementLoop
        row = self._selected_model_row()
        if not row:
            return
        try:
            ce = json.loads(row.get("eval_json") or "{}")
            base = self.registry.active("ALI")
            be = json.loads(base.get("eval_json") or "{}") if base else None
            regressions = ImprovementLoop(ROOT).run_tests()
            gate = promotion_gate(ce, be, regressions)
            if not gate.get("promote"):
                messagebox.showwarning(APP, gate.get("reason", "Promotion gate blocked."))
                return
            self.registry.promote("ALI", row["version"])
            self._load_active()
            self._refresh_models()
            messagebox.showinfo(APP, "Candidate promoted to active model.")
        except Exception as exc:
            messagebox.showerror(APP, str(exc))

    def export_gguf(self):
        from tools.gguf import GGUFManager
        active = self.registry.active("ALI")
        if not active or not active.get("hf_dir"):
            messagebox.showwarning(APP, "No active HF model is available.")
            return
        profile = str(self.cfg.get("conversion_profile", "q4_k_m"))
        out = filedialog.asksaveasfilename(
            initialdir=str(ROOT / "models" / "gguf"),
            defaultextension=".gguf",
            filetypes=[("GGUF", "*.gguf")],
        )
        if not out:
            return

        def work(progress):
            mgr = GGUFManager()
            progress(f"convert:{profile}", .15)
            direct = profile in {"f16", "bf16", "q8_0"}
            if direct:
                result = mgr.convert(active["hf_dir"], out, profile)
            else:
                temp_f16 = str(Path(out).with_name(Path(out).stem + "-f16.gguf"))
                converted = mgr.convert(active["hf_dir"], temp_f16, "f16")
                if not converted.get("path") and not Path(temp_f16).is_file():
                    return converted
                progress(f"quantize:{profile}", .70)
                result = mgr.quantize(temp_f16, out, profile.upper())
                result["conversion"] = converted
            progress("validate", .95)
            validation = mgr.validate(out)
            result["validation"] = validation
            result["profile"] = profile
            return result

        self.jobs.run("GGUF export + validation", work, "gguf")

    # ---------- diagnostics ----------
    def run_tests(self):
        def work(progress):
            p = subprocess.run(
                [sys.executable, "-m", "pytest", "tests", "-q", "--disable-warnings"],
                cwd=ROOT, capture_output=True, text=True, timeout=3600,
            )
            progress("tests complete", 1)
            return {"returncode": p.returncode, "output": (p.stdout or "") + "\n" + (p.stderr or "")}
        job = self.jobs.run("Full regression tests", work, "test")
        self.nb.select(self.jobs_tab)
        self._append_system(f"Regression job queued [{job.id[:8]}]", meta="tests")

    def doctor_dialog(self):
        from runtime.doctor import run_doctor
        w = tk.Toplevel(self.root)
        w.title("ALI AI 2.5 · Doctor")
        w.geometry("980x700")
        w.configure(bg=C["BG"])
        t = tk.Text(w, bg=C["EDITOR"], fg=C["INK"], font=("Consolas", 8), relief="flat")
        t.pack(fill="both", expand=True, padx=12, pady=12)
        try:
            t.insert("1.0", json.dumps(run_doctor(ROOT), ensure_ascii=False, indent=2))
        except Exception as exc:
            t.insert("1.0", str(exc))

    def memory_dialog(self):
        w = tk.Toplevel(self.root)
        w.title("ALI AI 2.5 · Memory")
        w.geometry("920x640")
        w.configure(bg=C["BG"])
        q = tk.Entry(w, bg=C["PANEL_2"], fg=C["INK"], insertbackground=C["INK"], relief="flat")
        q.pack(fill="x", padx=12, pady=12)
        t = tk.Text(w, bg=C["EDITOR"], fg=C["INK"], font=("Consolas", 8), relief="flat")
        t.pack(fill="both", expand=True, padx=12, pady=8)
        self._button(
            w, "Search",
            lambda: (
                t.delete("1.0", "end"),
                t.insert("1.0", json.dumps(self.runtime.memory.search(q.get(), 100), ensure_ascii=False, indent=2)),
            ),
            accent=True,
        )

    def learning_center_dialog(self):
        w = tk.Toplevel(self.root)
        w.title("ALI AI · مركز المعرفة وتعلّم الأخطاء")
        w.geometry("1040x720")
        w.configure(bg=C["BG"])

        header=tk.Frame(w,bg=C["BG"]); header.pack(fill="x",padx=14,pady=(14,8))
        tk.Label(header,text="مركز المعرفة والتعلّم المستمر",bg=C["BG"],fg=C["INK"],font=("Segoe UI Semibold",16)).pack(side="left")
        tk.Label(header,text="الأخطاء لا تدخل الأوزان تلقائيًا؛ التصحيح المعتمد فقط يصبح جاهزًا للجيل التالي.",bg=C["BG"],fg=C["MUTED"],font=("Segoe UI",9)).pack(side="left",padx=14)

        stats=tk.Frame(w,bg=C["PANEL"]); stats.pack(fill="x",padx=14,pady=6)
        stat_vars={k:tk.StringVar(value="—") for k in ("open","recovered","approved","trained")}
        for label,key in (("أخطاء مفتوحة","open"),("مستعادة","recovered"),("تصحيحات جاهزة","approved"),("مصَحَّحات دخلت تدريبًا","trained")):
            card=tk.Frame(stats,bg=C["WHITE"],highlightbackground=C["LINE"],highlightthickness=1); card.pack(side="left",fill="x",expand=True,padx=4,pady=4)
            tk.Label(card,text=label,bg=C["WHITE"],fg=C["MUTED"],font=("Segoe UI",8)).pack(pady=(8,2))
            tk.Label(card,textvariable=stat_vars[key],bg=C["WHITE"],fg=C["BLUE"],font=("Segoe UI Semibold",14)).pack(pady=(0,8))

        body=tk.Frame(w,bg=C["BG"]); body.pack(fill="both",expand=True,padx=14,pady=8)
        left=tk.Frame(body,bg=C["WHITE"],highlightbackground=C["LINE"],highlightthickness=1); left.pack(side="left",fill="both",expand=True,padx=(0,5))
        right=tk.Frame(body,bg=C["WHITE"],highlightbackground=C["LINE"],highlightthickness=1); right.pack(side="left",fill="both",expand=True,padx=(5,0))
        tk.Label(left,text="الحالات المسجلة",bg=C["WHITE"],fg=C["INK"],font=("Segoe UI Semibold",10)).pack(anchor="w",padx=10,pady=10)
        incidents=tk.Text(left,bg=C["EDITOR"],fg=C["INK"],font=("Consolas",8),relief="flat",wrap="word"); incidents.pack(fill="both",expand=True,padx=10,pady=(0,10))
        tk.Label(right,text="التصحيحات المعتمدة للجيل القادم",bg=C["WHITE"],fg=C["INK"],font=("Segoe UI Semibold",10)).pack(anchor="w",padx=10,pady=10)
        corrections=tk.Text(right,bg=C["EDITOR"],fg=C["INK"],font=("Consolas",8),relief="flat",wrap="word"); corrections.pack(fill="both",expand=True,padx=10,pady=(0,10))

        def refresh():
            try:
                st=self.error_learning.stats()
                inc=st.get("incidents",{}); cor=st.get("corrections",{})
                stat_vars["open"].set(str(inc.get("open",0)))
                stat_vars["recovered"].set(str(inc.get("recovered",0)))
                stat_vars["approved"].set(str(st.get("approved_corrections",0)))
                stat_vars["trained"].set(str(sum(v for k,v in cor.items() if str(k).startswith("trained:"))))
                incidents.delete("1.0","end"); incidents.insert("1.0", json.dumps(self.error_learning.pending(200),ensure_ascii=False,indent=2))
                corrections.delete("1.0","end"); corrections.insert("1.0", json.dumps(self.error_learning.corrections("approved",200),ensure_ascii=False,indent=2))
            except Exception as exc:
                incidents.delete("1.0","end"); incidents.insert("1.0",str(exc))

        def add_correction():
            user=simpledialog.askstring("تصحيح موثوق","السؤال/رسالة المستخدم:",parent=w)
            if not user: return
            bad=simpledialog.askstring("الناتج الخاطئ","النص الذي تريد تصحيحه:",parent=w) or ""
            corrected=simpledialog.askstring("الإجابة الصحيحة","اكتب الإجابة الصحيحة التي تريد تعليمها للجيل القادم:",parent=w)
            if not corrected: return
            try:
                self.error_learning.add_correction(user,bad,corrected,component="desktop",reason="manual_verified_correction",source="user")
                refresh()
                self.status.configure(text="تم حفظ التصحيح كبيانات معتمدة للجيل القادم.")
            except Exception as exc:
                messagebox.showerror(APP,str(exc),parent=w)

        bar=tk.Frame(w,bg=C["BG"]); bar.pack(fill="x",padx=14,pady=(0,12))
        self._button(bar,"إضافة تصحيح معتمد",add_correction,side="left",accent=True)
        self._button(bar,"تحديث",refresh,side="left")
        self._button(bar,"إغلاق",w.destroy,side="right")
        refresh()

    def settings_dialog(self):
        w = tk.Toplevel(self.root)
        w.title("ALI AI 2.5 · Settings")
        w.geometry("860x820")
        w.configure(bg=C["BG"])

        internet = tk.BooleanVar(value=self.runtime.allow_internet)
        auto = tk.BooleanVar(value=bool(self.cfg.get("auto_improve", False)))
        mode = tk.StringVar(value=self.runtime.permission_manager.mode)
        language_profile = tk.StringVar(value=str(self.cfg.get("language_profile", "ar-SA")))
        training_method = tk.StringVar(value=str(self.cfg.get("training_method", "lora_continue_cpu")))
        conversion_profile = tk.StringVar(value=str(self.cfg.get("conversion_profile", "q4_k_m")))
        dataset_strategy = tk.StringVar(value=str(self.cfg.get("dataset_strategy", "cumulative_replay")))

        tk.Checkbutton(
            w, text="تفعيل البحث عبر الإنترنت داخل المحادثة (مع التحقق من المصادر)",
            variable=internet, bg=C["BG"], fg=C["INK"], selectcolor=C["PANEL"],
        ).pack(anchor="w", padx=18, pady=8)
        tk.Checkbutton(
            w, text="Enable gated automatic improvement scheduler",
            variable=auto, bg=C["BG"], fg=C["INK"], selectcolor=C["PANEL"],
        ).pack(anchor="w", padx=18, pady=8)

        def combo(title, var, values, pady=(10,2)):
            tk.Label(w, text=title, bg=C["BG"], fg=C["MUTED"]).pack(anchor="w", padx=18, pady=pady)
            ttk.Combobox(w, textvariable=var, values=values, state="readonly").pack(fill="x", padx=18)

        combo("لهجة/أسلوب الرد العربي", language_profile, ["ar-MSA","ar-SA","ar-YE","ar-EG"])
        combo("طريقة التدريب", training_method, [
            "lora_continue_cpu","lora_cpu","continued_sft_cpu","full_finetune_micro_cpu"
        ])
        combo("طريقة تحويل النموذج", conversion_profile, [
            "q4_k_m","q5_k_m","q6_k","q8_0","f16","bf16"
        ])
        combo("استراتيجية البيانات الجديدة", dataset_strategy, ["cumulative_replay","delta_only"])

        tk.Label(w, text="Permission mode", bg=C["BG"], fg=C["MUTED"]).pack(anchor="w", padx=18, pady=(12,2))
        ttk.Combobox(w, textvariable=mode, values=[x[0] for x in PERM_MODES], state="readonly").pack(fill="x", padx=18)

        tk.Label(
            w,
            text=(
                "P50: التدريب المحلي CPU-first بحد أقصى 6 خيوط ووظيفة ثقيلة واحدة. "
                "QLoRA/GPU التدريب مغلق افتراضيًا لأن Quadro M1000M فيها 2GB VRAM. "
                "استكمال التدريب يبدأ من Checkpoint/Adapter موثوق؛ GGUF مخرج تشغيل ولا يُستخدم كمصدر تدريب. "
                "البيانات الجديدة تُراجع وتُزيل التكرار وتُقيّم قبل اعتمادها."
            ),
            bg=C["BG"], fg=C["AMBER"], wraplength=790, justify="left",
        ).pack(anchor="w", padx=18, pady=18)

        def save():
            self.runtime.allow_internet = bool(internet.get())
            self.runtime.permission_manager.set_mode(mode.get())
            self.cfg.update({
                "allow_internet": bool(internet.get()),
                "auto_improve": bool(auto.get()),
                "perm_mode": mode.get(),
                "ai_mode": self.ai_mode.get(),
                "language_profile": language_profile.get(),
                "training_method": training_method.get(),
                "conversion_profile": conversion_profile.get(),
                "dataset_strategy": dataset_strategy.get(),
            })
            try:
                from conversation_intelligence.language_adapter import ArabicLanguageAdapter
                self.language_adapter = ArabicLanguageAdapter(profile=language_profile.get())
            except Exception:
                self.language_adapter = None
            save_cfg(self.cfg)
            w.destroy()
            self._refresh_status()

        self._button(w, "حفظ الإعدادات", save, accent=True)

    # ---------- compatibility ----------
    def _ai_mode_menu(self, parent=None):
        menu = tk.Menu(parent or self.root, tearoff=False, bg=C["PANEL"], fg=C["INK"])
        for mode in AI_MODES:
            menu.add_radiobutton(
                label=mode, variable=self.ai_mode,
                value=mode, command=lambda x=mode: self._set_ai_mode(x),
            )
        return menu

    def _set_ai_mode(self, mode):
        self.ai_mode.set(mode)
        self.cfg["ai_mode"] = mode
        save_cfg(self.cfg)
        self.status.configure(text=f"AI mode: {mode}")

    def run_terminal(self):
        cmd = self.term_entry.get().strip()
        if not cmd:
            return

        ctx = ConversationContext(
            "terminal", self.project_dir,
            self.runtime.permission_manager.mode, "ALI", "High",
            tool_registry=self.runtime.registry,
        )
        tool = self.runtime.registry.get("run_command")
        decision = self.runtime.permission_manager.check(
            tool_name="run_command", permission=tool.permission,
            ctx=ctx, kwargs={"command": cmd},
        )
        if decision.needs_ask:
            if not messagebox.askyesno("Terminal permission", f"Allow command?\n\n{cmd}"):
                return
            self.runtime.permission_manager.grant("run_command", session=True)
        elif not decision.allowed:
            self.term.insert("end", f"\nDENIED: {decision.reason}\n")
            return

        self.term.insert("end", f"\n$ {cmd}\n")
        self.nb.select(self.term_tab)

        def job():
            try:
                from tools.terminal_stream import stream_command
                self.root.after(0, lambda: self.activity.event(f"$ {cmd}", phase="terminal", progress=0.02, status="running"))
                for line in stream_command(self.project_dir, cmd, 120):
                    self.root.after(0, lambda x=line: self.term.insert("end", x + "\n"))