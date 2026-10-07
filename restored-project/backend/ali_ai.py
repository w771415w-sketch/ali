# -*- coding: utf-8 -*-
"""ALI AI 2.5 — Professional Assistant / P50 local command center.

The desktop app is the control plane. It does not contain training logic itself:
UI -> jobs -> pipeline/runtime -> artifacts -> registry.

Primary UX:
- three-pane workspace (projects/conversations | local chat | inspector/editor/tools)
- persistent conversations in SQLite
- local streaming inference
- bounded tool calling with confirmation
- dataset/knowledge pipeline
- real tokenizer/base/SFT/LoRA training jobs
- immutable weight import + registry + promotion
- GGUF conversion/validation bridge
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog

from config.app_config import APP, VERSION, PALETTE, AI_MODES, PERM_MODES, MODELS, EFFORTS
from config.i18n import tr, normalize_language, is_rtl
from ui.rtl import configure_root, start_side, end_side, anchor_start
from config.paths import APP_PATHS
from core.context import ConversationContext
from core.runtime import ALIRuntime
from core.orchestrator import Orchestrator
from core.job_manager import JobManager
from core.session_store import SessionStore
from runtime.hardware import detect, training_profile, model_profile
from runtime.device_policy import choose_policy
from config.device_profiles import recommend_for_hardware
from runtime.resources import ResourceManager
from model.registry import ModelRegistry
from training.scaling import PROFILES, build_training_plan
from ui.theme import configure as configure_theme
from ui.widgets import ChatView, LineNumberedEditor
from control_plane import KCARequestRouter, RequestEnvelope, summary as kca_summary
from training.accumulated_updates import AccumulatedTrainingManager
from assistant.error_learning import ErrorLearningStore
from core.response_guard import sanitize_output, stream_safe
from ui.activity import ActivityCenter
from integration.hermes import HermesContextRouter

ROOT = APP_PATHS.project_root()
DB = ROOT / "artifacts" / "ali.sqlite3"
C = PALETTE


def load_cfg() -> dict:
    default = {
        "name": "Windows PC",
        "language": "ar",
        "ai_mode": "professional",
        "last_dir": str(ROOT),
        "allow_internet": True,
        "auto_improve": True,
        "perm_mode": "default",
        "language_profile": "ar-SA",
        "training_method": "lora_continue_cpu",
        "conversion_profile": "q4_k_m",
        "model": "ALI",
        "runtime": {"context": 384, "max_new_tokens": 384, "temperature": .65},
        "ui": {"right_tab": 0},
    }
    try:
        p = APP_PATHS.user_config()
        if p.exists():
            data = json.loads(p.read_text(encoding="utf-8"))
            for key, value in default.items():
                if key not in data:
                    data[key] = value
            return data
    except Exception:
        pass
    return default


def save_cfg(cfg: dict) -> None:
    p = APP_PATHS.user_config()
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, p)


class App:
    """Professional desktop UI, kept backward compatible with older tests."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.cfg = load_cfg()
        self.language = normalize_language(self.cfg.get("language", "ar"))
        self.rtl = is_rtl(self.language)
        self.busy = False
        self.cancel_requested = False
        self.history: list[dict] = []
        self.current_thread = ""
        self.streaming_bubble = None
        self.last_assistant_bubble = None
        self.project_dir = os.path.abspath(self.cfg.get("last_dir") or ROOT)

        self.hardware = detect()
        self.policy = choose_policy(self.hardware)
        self.train_profile = training_profile(self.hardware)
        self.model_profile = model_profile(self.hardware)
        self.device_profile = recommend_for_hardware(self.hardware)
        self.resources = ResourceManager(self.hardware)
        try:
            from conversation_intelligence.language_adapter import ArabicLanguageAdapter
            self.language_adapter = ArabicLanguageAdapter(profile=self.cfg.get("language_profile", "ar-SA"))
        except Exception:
            self.language_adapter = None

        self.registry = ModelRegistry(ROOT / "models" / "models.sqlite3")
        # Heavy model/training services are lazy-loaded so the desktop shell stays responsive.
        self.model_manager = None
        self.weights = None
        self.pipeline = None
        self.kca_router = KCARequestRouter()
        self.kca = kca_summary()
        self.self_manager = __import__("autonomy.self_manager", fromlist=["SelfManager"]).SelfManager(
            ROOT, max(8, int(self.hardware.ram_gb or 8))
        )
        self.runtime = ALIRuntime(
            ROOT,
            DB,
            None,
            bool(self.cfg.get("allow_internet", False)),
        )
        self.runtime.permission_manager.set_mode(self.cfg.get("perm_mode", "default"))
        self.orchestrator = Orchestrator(self.runtime)
        self.jobs = JobManager(ROOT / "runtime" / "jobs.json")
        self.accumulated_training = AccumulatedTrainingManager(ROOT, merge_threshold=4)
        self.error_learning = ErrorLearningStore(ROOT / "runtime_error_learning.sqlite3", ROOT)
        self.hermes_router = HermesContextRouter()
        self._hermes_prompt_context = ""
        self.sessions = SessionStore(DB)
        self.project_id = self.sessions.ensure_project(self.project_dir, Path(self.project_dir).name)
        self.thread_repo = self.sessions.threads
        self.message_repo = self.sessions.messages

        runtime_cfg = self.cfg.get("runtime", {})
        self.temp_var = tk.DoubleVar(value=float(runtime_cfg.get("temperature", .65)))
        self.ctx_var = tk.IntVar(value=int(runtime_cfg.get("context", self.policy["recommended_context"])))
        self.out_var = tk.IntVar(value=int(runtime_cfg.get("max_new_tokens", self.train_profile["max_new_tokens"])))
        self.ai_mode = tk.StringVar(value=self.cfg.get("ai_mode", "professional"))
        self.perm_mode = tk.StringVar(value=self.cfg.get("perm_mode", "default"))

        root.title(f"{APP} {VERSION} — Command Center")
        root.geometry("1600x960")
        root.minsize(1240, 760)
        root.configure(bg=C["BG"])
        configure_root(root, self.language)
        root.protocol("WM_DELETE_WINDOW", self._on_close)

        configure_theme(root)
        self._build()
        self._new_thread(silent=True)
        self._refresh_all()
        root.after(2500, self._refresh_hardware_loop)
        root.after(1800, self._refresh_jobs_loop)
        root.after(5000, self._auto_improvement_tick)

    # ---------- shell ----------
    def _build(self):
        self._build_header()
        self.body = ttk.Panedwindow(self.root, orient="horizontal")
        self.body.pack(fill="both", expand=True, padx=8, pady=8)

        self.left = ttk.Frame(self.body, style="Panel.TFrame", width=290)
        self.center = ttk.Frame(self.body)
        self.right = ttk.Frame(self.body, style="Panel.TFrame", width=390)
        self._set_pane_order()

        self._build_left()
        self._build_center()
        self._build_right()
        self._build_status()

        self.root.bind("<Control-n>", lambda _e: self._new_thread())
        self.root.bind("<Control-Return>", lambda _e: self.send())
        self.root.bind("<Control-Shift-P>", lambda _e: self.settings_dialog())
        self.root.bind("<F5>", lambda _e: self._refresh_all())

    def _set_pane_order(self):
        # The visual shell is mirrored as a unit: Arabic RTL places navigation on the right; English LTR on the left.
        try:
            existing = tuple(self.body.panes())
            for pane in existing:
                self.body.forget(pane)
            ordered = ((self.right, 2), (self.center, 4), (self.left, 1)) if self.rtl else ((self.left, 1), (self.center, 4), (self.right, 2))
            for pane, weight in ordered:
                self.body.add(pane, weight=weight)
        except Exception:
            # Keep the shell usable on Tk/ttk builds with different pane APIs.
            try:
                self.body.add(self.left, weight=1)
                self.body.add(self.center, weight=4)
                self.body.add(self.right, weight=2)
            except Exception:
                pass

    def set_language(self, language: str):
        """Persist language and rebuild the shell so every pane mirrors direction consistently."""
        new_lang = normalize_language(language)
        if new_lang == self.language:
            return
        active_thread = self.current_thread
        self.language = new_lang
        self.rtl = is_rtl(new_lang)
        self.cfg["language"] = new_lang
        save_cfg(self.cfg)
        configure_root(self.root, new_lang)
        for child in list(self.root.winfo_children()):
            try: child.destroy()
            except Exception: pass
        self._build()
        self.current_thread = active_thread
        self._load_thread_by_id(active_thread)
        self._refresh_all()

    def toggle_language(self):
        self.set_language("en" if self.language == "ar" else "ar")

    def _load_thread_by_id(self, thread_id: str):
        if not thread_id or not getattr(self, "thread_list", None):
            return
        if not self.thread_ids or thread_id not in self.thread_ids:
            return
        idx = self.thread_ids.index(thread_id)
        self.thread_list.selection_clear(0, "end")
        self.thread_list.selection_set(idx)
        self._thread_selected()

    def _build_header(self):
        c = C; root = self.root; side0 = start_side(root); side1 = end_side(root)
        h = tk.Frame(root, bg=c["BG"], height=72, highlightbackground=c["LINE"], highlightthickness=1)
        h.pack(fill="x"); h.pack_propagate(False)
        brand = tk.Frame(h, bg=c["BG"]); brand.pack(side=side0, padx=16)
        tk.Label(brand, text="◈", bg=c["BG"], fg=c["BLUE"], font=("Segoe UI Semibold", 21)).pack(side=side0, padx=(0,7))
        brand_text = tk.Frame(brand, bg=c["BG"]); brand_text.pack(side=side0)
        tk.Label(brand_text, text="ALI AI", bg=c["BG"], fg=c["INK"], font=("Segoe UI Semibold", 15)).pack(anchor=anchor_start(root))
        tk.Label(brand_text, text=tr("app_subtitle", self.language), bg=c["BG"], fg=c["MUTED"], font=("Segoe UI", 8)).pack(anchor=anchor_start(root))
        self.model_lbl = tk.Label(h, text=tr("model", self.language)+" · loading", bg=c["SOFT"], fg=c["BLUE"], padx=9, pady=5, font=("Segoe UI Semibold", 8)); self.model_lbl.pack(side=side0, padx=8)
        self.workspace_lbl = tk.Label(h, text=Path(self.project_dir).name, bg=c["BG"], fg=c["MUTED"], font=("Segoe UI", 9)); self.workspace_lbl.pack(side=side0, padx=4)
        self.device_lbl = tk.Label(h, text="", bg=c["BG"], fg=c["MUTED"], font=("Segoe UI", 8)); self.device_lbl.pack(side=side0, padx=10)
        self.kca_lbl = tk.Label(h, text=f"KCA · {self.kca.get('functions', 0)}", bg=c["SOFT"], fg=c["BLUE"], font=("Segoe UI Semibold", 8), padx=8, pady=4); self.kca_lbl.pack(side=side0, padx=3)
        self.local_lbl = tk.Label(h, text=tr("offline", self.language), bg=c["SOFT"], fg=c["GREEN"], font=("Segoe UI Semibold", 8), padx=8, pady=4); self.local_lbl.pack(side=side0, padx=3)
        self.auto_lbl = tk.Label(h, text=tr("auto_learn", self.language)+" · ON", bg=c["SOFT"], fg=c["GREEN"], font=("Segoe UI Semibold", 8), padx=8, pady=4); self.auto_lbl.pack(side=side0, padx=3)
        self.hermes_lbl = tk.Label(h, text="HERMES · EXTERNAL", bg=c["SOFT"], fg=c["BLUE"], font=("Segoe UI Semibold", 8), padx=8, pady=4); self.hermes_lbl.pack(side=side0, padx=3)
        self._button(h, "AR / EN" if self.language == "ar" else "EN / AR", self.toggle_language, side=side1)
        self._button(h, tr("open_project", self.language), self._choose_dir, side=side1)
        self._button(h, tr("doctor", self.language), self.doctor_dialog, side=side1)
        self._button(h, tr("models", self.language), self.models_dialog, side=side1)
        self._button(h, "التعلّم من الأخطاء", self.learning_center_dialog, side=side1)
        self._button(h, tr("train", self.language), self.train_dialog, side=side1, accent=True)

    def _build_left(self):
        c=C; root=self.root; side0=start_side(root); anchor=anchor_start(root)
        # Navigation rail visually follows the supplied reference while reusing the existing business callbacks.
        nav=tk.Frame(self.left,bg=c["RAIL"],highlightbackground=c["LINE"],highlightthickness=1); nav.pack(fill="x",padx=0,pady=0)
        brand=tk.Frame(nav,bg=c["RAIL"]); brand.pack(fill="x",padx=12,pady=(10,6))
        tk.Label(brand,text="◈",bg=c["RAIL"],fg=c["BLUE"],font=("Segoe UI Semibold",18)).pack(side=side0,padx=(0,7))
        tk.Label(brand,text="ALI AI",bg=c["RAIL"],fg=c["INK"],font=("Segoe UI Semibold",12)).pack(side=side0)
        nav_items=(("◌",tr("new_chat",self.language),self._new_thread),("▦",tr("projects",self.language),self._choose_dir),("□",tr("files",self.language),self.knowledge_dialog),("◎",tr("memory",self.language),self.memory_dialog),("⚒",tr("tools",self.language),self.settings_dialog),("⌕",tr("web",self.language),self.settings_dialog),("◈",tr("models",self.language),self.models_dialog),("◫",tr("datasets",self.language),self.knowledge_dialog),("◉",tr("jobs",self.language),lambda:self.nb.select(self.jobs_tab)),("⚙",tr("settings",self.language),self.settings_dialog))
        for icon,label,cmd in nav_items:
            row=tk.Frame(nav,bg=c["RAIL"]); row.pack(fill="x",padx=6,pady=1)
            b=tk.Label(row,text=f"{icon}  {label}",bg=c["RAIL"],fg=c["INK"],font=("Segoe UI",9),cursor="hand2",padx=9,pady=6,anchor=anchor); b.pack(fill="x")
            b.bind("<Button-1>",lambda _e,fn=cmd:fn()); b.bind("<Enter>",lambda _e,w=b:w.configure(bg=c["RAIL_HOVER"])); b.bind("<Leave>",lambda _e,w=b:w.configure(bg=c["RAIL"]))
        conv=tk.Frame(self.left,bg=c["BG"]); conv.pack(fill="x")
        tk.Label(conv,text=tr("conversations",self.language).upper(),bg=c["BG"],fg=c["MUTED"],font=("Segoe UI Semibold",8)).pack(anchor=anchor,padx=14,pady=(10,6))
        top=tk.Frame(conv,bg=c["BG"]); top.pack(fill="x",padx=10)
        self._button(top,"+ "+tr("new_chat",self.language),self._new_thread,side=side0,accent=True); self._button(top,tr("refresh",self.language),self._refresh_threads,side=side0)
        self.thread_list=tk.Listbox(conv,bg=c["SOFT"],fg=c["INK"],selectbackground="#eaf0ff",selectforeground=c["INK"],relief="flat",bd=0,activestyle="none",height=7,font=("Segoe UI",9))
        self.thread_list.pack(fill="x",padx=10,pady=(4,8)); self.thread_list.bind("<<ListboxSelect>>",self._thread_selected); self.thread_ids=[]
        tk.Label(conv,text=tr("projects",self.language).upper(),bg=c["BG"],fg=c["MUTED"],font=("Segoe UI Semibold",8)).pack(anchor=anchor,padx=14,pady=(2,6))
        self.tree=ttk.Treeview(conv,show="tree",height=8); self.tree.pack(fill="x",padx=10); self.tree.bind("<Double-1>",self.open_selected_file)
        self.left_actions=tk.Frame(conv,bg=c["BG"]); self.left_actions.pack(fill="x",padx=9,pady=8)
        for label,command in ((tr("datasets",self.language),self.knowledge_dialog),(tr("training_files",self.language),self.accumulated_training_dialog),(tr("files",self.language),self.knowledge_dialog),(tr("memory",self.language),self.memory_dialog),("التعلّم من الأخطاء",self.learning_center_dialog),("KCA",self.settings_dialog),(tr("self_learn",self.language),self.self_learn_now)):
            self._button(self.left_actions,label,command,side=side0)

    def _build_center(self):
        c=C; root=self.root; side0=start_side(root); side1=end_side(root); anchor=anchor_start(root)
        top=tk.Frame(self.center,bg=c["BG"],height=54); top.pack(fill="x"); top.pack_propagate(False)
        self.title_lbl=tk.Label(top,text=tr("new_chat",self.language),bg=c["BG"],fg=c["INK"],font=("Segoe UI Semibold",12)); self.title_lbl.pack(side=side0,padx=14,pady=14)
        self.intent_lbl=tk.Label(top,text=tr("ready",self.language),bg=c["BG"],fg=c["MUTED"],font=("Segoe UI",8)); self.intent_lbl.pack(side=side0,padx=12)
        self.chat=ChatView(self.center); self.chat.pack(fill="both",expand=True,padx=8)
        composer=tk.Frame(self.center,bg=c["BG"],highlightbackground=c["LINE"],highlightthickness=1); composer.pack(fill="x",padx=8,pady=8)
        chips=tk.Frame(composer,bg=c["BG"]); chips.pack(fill="x",padx=8,pady=(7,3))
        for label,prompt in ((tr("analyze",self.language),"حلل المشروع وحدد أهم المشاكل وخطة الإصلاح."),(tr("inspect_model",self.language),"افحص النموذج والأوزان الحالية ومسار التحميل."),(tr("train_tokenizer",self.language),"تحقق من بيانات التدريب ثم أنشئ tokenizer version جديدة."),(tr("train",self.language),"شغّل تدريب ALI مع checkpointing وevaluation."),(tr("import_weights",self.language),"افحص الأوزان الموجودة وأخبرني أين يجب تثبيتها."),(tr("check_device",self.language),"افحص الجهاز وحدد إعداد التدريب الآمن.")):
            self._button(chips,label,lambda x=prompt:self._insert_prompt(x),side=side0)
        self.entry=tk.Text(composer,height=4,wrap="word",bg=c["EDITOR"],fg=c["INK"],insertbackground=c["INK"],selectbackground="#eaf0ff",relief="flat",bd=0,font=("Segoe UI",10),padx=12,pady=10); self.entry.tag_configure("__ali_direction",justify="right" if self.rtl else "left"); self.entry.pack(fill="x",padx=8,pady=5); self.entry.bind("<KeyRelease>",lambda _e:self.entry.tag_add("__ali_direction","1.0","end"),add="+"); self.entry.bind("<Return>",self._on_return)
        controls=tk.Frame(composer,bg=c["BG"]); controls.pack(fill="x",padx=8,pady=(0,7))
        tk.Label(controls,text=tr("professional",self.language),bg=c["BG"],fg=c["MUTED"]).pack(side=side0)
        ttk.Combobox(controls,textvariable=self.ai_mode,values=AI_MODES,state="readonly",width=12).pack(side=side0,padx=(4,10))
        tk.Label(controls,text="Temp",bg=c["BG"],fg=c["MUTED"]).pack(side=side0)
        tk.Scale(controls,from_=0,to=1,resolution=.05,orient="horizontal",variable=self.temp_var,length=90,bg=c["BG"],fg=c["MUTED"],highlightthickness=0,troughcolor=c["LINE"],bd=0).pack(side=side0)
        tk.Label(controls,text="Ctx",bg=c["BG"],fg=c["MUTED"]).pack(side=side0,padx=(8,2)); tk.Entry(controls,width=7,textvariable=self.ctx_var,bg=c["SOFT"],fg=c["INK"],insertbackground=c["INK"],relief="flat",justify="right" if self.rtl else "left").pack(side=side0)
        tk.Label(controls,text="Out",bg=c["BG"],fg=c["MUTED"]).pack(side=side0,padx=(8,2)); tk.Entry(controls,width=7,textvariable=self.out_var,bg=c["SOFT"],fg=c["INK"],insertbackground=c["INK"],relief="flat",justify="right" if self.rtl else "left").pack(side=side0)
        self.stop_btn=self._button(controls,tr("stop",self.language),self.stop_generation,side=side1); self.stop_btn.configure(state="disabled")
        self.send_btn=self._button(controls,tr("send",self.language)+"  ↵",self.send,side=side1,accent=True)

    def _build_right(self):
        # Right rail is intentionally stacked: developer surfaces at the top, live execution in the middle,
        # and the system-health/telemetry list at the bottom as requested.
        self.right_stack=tk.PanedWindow(self.right,orient="vertical",sashwidth=5,bd=0,bg=C["LINE"],relief="flat")
        self.right_stack.pack(fill="both",expand=True,padx=4,pady=4)
        self.dev_frame=tk.Frame(self.right_stack,bg=C["BG"])
        self.activity_frame=tk.Frame(self.right_stack,bg=C["BG"],height=250)
        self.health_footer=tk.Frame(self.right_stack,bg=C["SOFT"],height=235)
        try:
            self.right_stack.add(self.dev_frame,stretch="always",minsize=180)
            self.right_stack.add(self.activity_frame,stretch="always",minsize=190)
            self.right_stack.add(self.health_footer,stretch="never",minsize=190)
        except Exception:
            self.right_stack.add(self.dev_frame); self.right_stack.add(self.activity_frame); self.right_stack.add(self.health_footer)
        self.nb=ttk.Notebook(self.dev_frame); self.nb.pack(fill="both",expand=True,padx=2,pady=2)
        self.overview_tab=ttk.Frame(self.nb,style="Panel.TFrame"); self.editor_tab=ttk.Frame(self.nb,style="Panel.TFrame"); self.term_tab=ttk.Frame(self.nb,style="Panel.TFrame"); self.jobs_tab=ttk.Frame(self.nb,style="Panel.TFrame"); self.model_tab=ttk.Frame(self.nb,style="Panel.TFrame")
        for tab,key in ((self.overview_tab,"overview"),(self.editor_tab,"editor"),(self.term_tab,"terminal"),(self.jobs_tab,"jobs"),(self.model_tab,"models")): self.nb.add(tab,text=tr(key,self.language))
        self._build_overview(); self._build_editor(); self._build_terminal(); self._build_jobs(); self._build_model_panel()
        self.activity=ActivityCenter(self.activity_frame,self.rtl)
        self._build_health_footer()

    def _build_overview(self):
        wrap=tk.Frame(self.overview_tab,bg=C["BG"]); wrap.pack(fill="both",expand=True,padx=8,pady=8)
        head=tk.Frame(wrap,bg=C["BG"]); head.pack(fill="x",pady=(0,7))
        tk.Label(head,text=tr("system_health",self.language),bg=C["BG"],fg=C["INK"],font=("Segoe UI Semibold",12)).pack(side=start_side(self.root))
        tk.Label(head,text="● "+tr("connected",self.language),bg=C["SOFT"],fg=C["GREEN"],font=("Segoe UI Semibold",8),padx=8,pady=4).pack(side=end_side(self.root))
        metrics=tk.Frame(wrap,bg=C["BG"]); metrics.pack(fill="x",pady=(0,7))
        self._health_metric(metrics,"CPU","cpu_metric"); self._health_metric(metrics,"GPU","gpu_metric"); self._health_metric(metrics,"RAM","ram_metric"); self._health_metric(metrics,"TEMP","temp_metric")
        self._card(wrap,"ACTIVE MODEL","model_card"); self._card(wrap,"WORKFLOW","workflow_card"); self._card(wrap,"MEMORY / RAG","memory_card"); self._card(wrap,"DEVICE","device_card"); self._card(wrap,"KCA CONTROL PLANE","kca_card")
        self.kca_card.configure(text="KCA functions: "+str(self.kca.get("functions",0)))

    def _health_metric(self,parent,label,attr):
        card=tk.Frame(parent,bg=C["WHITE"],highlightbackground=C["LINE"],highlightthickness=1); card.pack(side=start_side(self.root),fill="x",expand=True,padx=2)
        tk.Label(card,text=label,bg=C["WHITE"],fg=C["MUTED"],font=("Segoe UI Semibold",7)).pack(anchor=anchor_start(self.root),padx=8,pady=(6,1))
        value=tk.Label(card,text="—",bg=C["WHITE"],fg=C["INK"],font=("Segoe UI Semibold",10)); value.pack(anchor=anchor_start(self.root),padx=8,pady=(0,6)); setattr(self,attr,value)

    def _card(self, parent, title, attr):
        shell = tk.Frame(parent, bg=C["PANEL_2"], highlightbackground=C["LINE"], highlightthickness=1)
        shell.pack(fill="x", pady=5)
        tk.Label(
            shell, text=title, bg=C["PANEL_2"], fg=C["MUTED"],
            font=("Segoe UI Semibold", 8)
        ).pack(anchor="w", padx=10, pady=(8, 2))
        value = tk.Label(
            shell, text="loading…", bg=C["PANEL_2"], fg=C["INK"],
            justify="left", anchor="w", wraplength=330,
            font=("Consolas", 8),
        )
        value.pack(fill="x", padx=10, pady=(1, 9))
        setattr(self, attr, value)

    def _build_editor(self):
        self.editor = LineNumberedEditor(self.editor_tab)
        self.editor.pack(fill="both", expand=True, padx=6, pady=6)
        self.editor_path: Path | None = None

        bar = tk.Frame(self.editor_tab, bg=C["PANEL"])
        bar.pack(fill="x")
        self._button(bar, "Save", self.save_editor, side="left", accent=True)
        self._button(bar, "Revert", self.revert_editor, side="left")
        self._button(bar, "Open", self._choose_editor_file, side="left")
        self._button(bar, "Run tests", self.run_tests, side="left")

    def _build_terminal(self):
        self.term = tk.Text(
            self.term_tab, bg=C["EDITOR"], fg=C["INK"],
            insertbackground=C["INK"], font=("Consolas", 9),
            relief="flat", bd=0,
        )
        self.term.pack(fill="both", expand=True, padx=6, pady=6)

        row = tk.Frame(self.term_tab, bg=C["PANEL"])
        row.pack(fill="x")
        self.term_entry = tk.Entry(
            row, bg=C["PANEL_2"], fg=C["INK"], insertbackground=C["INK"], relief="flat"
        )
        self.term_entry.pack(side="left", fill="x", expand=True, padx=6, pady=6)
        self.term_entry.bind("<Return>", lambda _e: self.run_terminal())
        self._button(row, "Run", self.run_terminal, side="right", accent=True)

    def _build_jobs(self):
        self.jobs_list = tk.Listbox(
            self.jobs_tab, bg=C["EDITOR"], fg=C["INK"],
            selectbackground=C["LINE"], relief="flat", bd=0,
            font=("Consolas", 8),
        )
        self.jobs_list.pack(fill="both", expand=True, padx=6, pady=6)

    def _build_model_panel(self):
        self.model_list = tk.Listbox(
            self.model_tab, bg=C["EDITOR"], fg=C["INK"],
            selectbackground=C["LINE"], relief="flat", bd=0,
            font=("Consolas", 8),
        )
        self.model_list.pack(fill="both", expand=True, padx=6, pady=6)

        bar = tk.Frame(self.model_tab, bg=C["PANEL"])
        bar.pack(fill="x", padx=6, pady=6)
        self._button(bar, "Import file", self.import_weights, side="left", accent=True)
        self._button(bar, "Import folder", self.import_weights_folder, side="left")
        self._button(bar, "Verify", self.verify_selected_model, side="left")
        self._button(bar, "Promote", self.promote_selected_model, side="left")
        self._button(bar, "GGUF", self.export_gguf, side="left")
        self._button(bar, "Refresh", self._refresh_models, side="right")

    def _build_health_footer(self):
        side0=start_side(self.root); anchor=anchor_start(self.root)
        head=tk.Frame(self.health_footer,bg=C["SOFT"]); head.pack(fill="x",padx=8,pady=(7,4))
        tk.Label(head,text=tr("system_health",self.language),bg=C["SOFT"],fg=C["INK"],font=("Segoe UI Semibold",10)).pack(side=side0)
        self.health_state=tk.Label(head,text="● "+tr("connected",self.language),bg=C["SOFT"],fg=C["GREEN"],font=("Segoe UI Semibold",8)); self.health_state.pack(side=end_side(self.root))
        grid=tk.Frame(self.health_footer,bg=C["SOFT"]); grid.pack(fill="x",padx=8,pady=2)
        self.rh_cpu=self._health_tile(grid,"CPU"); self.rh_gpu=self._health_tile(grid,"GPU"); self.rh_ram=self._health_tile(grid,"RAM"); self.rh_temp=self._health_tile(grid,"TEMP")
        cards=tk.Frame(self.health_footer,bg=C["SOFT"]); cards.pack(fill="x",padx=8,pady=4)
        self.rh_model=self._health_line(cards,"MODEL"); self.rh_task=self._health_line(cards,"TASK"); self.rh_context=self._health_line(cards,"CONTEXT")
        self.rh_hermes=self._health_line(cards,"HERMES")
    def _health_tile(self,parent,label):
        f=tk.Frame(parent,bg=C["WHITE"],highlightbackground=C["LINE"],highlightthickness=1); f.pack(side="left",fill="x",expand=True,padx=2)
        tk.Label(f,text=label,bg=C["WHITE"],fg=C["MUTED"],font=("Segoe UI Semibold",7)).pack(anchor="w",padx=6,pady=(3,0)); v=tk.Label(f,text="—",bg=C["WHITE"],fg=C["INK"],font=("Segoe UI Semibold",9)); v.pack(anchor="w",padx=6,pady=(0,4)); return v
    def _health_line(self,parent,label):
        f=tk.Frame(parent,bg=C["WHITE"],highlightbackground=C["LINE"],highlightthickness=1); f.pack(fill="x",pady=2)
        tk.Label(f,text=label,bg=C["WHITE"],fg=C["MUTED"],font=("Segoe UI Semibold",7)).pack(side=start_side(self.root),padx=6,pady=3); v=tk.Label(f,text="—",bg=C["WHITE"],fg=C["INK"],font=("Consolas",7),anchor=anchor_start(self.root),justify="left"); v.pack(side=end_side(self.root),fill="x",expand=True,padx=6,pady=3); return v

    def _build_status(self):
        s=tk.Frame(self.root,bg=C["BG"],height=28,highlightbackground=C["LINE"],highlightthickness=1); s.pack(fill="x"); s.pack_propagate(False)
        side0=start_side(self.root); side1=end_side(self.root)
        self.status=tk.Label(s,text=tr("ready",self.language),bg=C["BG"],fg=C["MUTED"],font=("Segoe UI",8)); self.status.pack(side=side0,padx=10)
        self.perm_lbl=tk.Label(s,text="Permission: "+self.runtime.permission_manager.mode,bg=C["BG"],fg=C["AMBER"],font=("Segoe UI",8)); self.perm_lbl.pack(side=side1,padx=10)

    def _button(self, parent, text, command, *, side=None, accent=False):
        b=tk.Button(parent,text=text,command=command,bg=C["BLUE"] if accent else C["SOFT"],fg=C["WHITE"] if accent else C["INK"],activebackground="#eaf0ff",activeforeground=C["INK"],relief="flat",bd=0,cursor="hand2",font=("Segoe UI Semibold",8),padx=10,pady=6)
        b.pack(side=side or start_side(self.root),padx=3,pady=3)
        return b

    def _ensure_model_services(self):
        """Load heavy model/artifact services only when they are actually needed."""
        if self.model_manager is None or self.weights is None or self.pipeline is None:
            from model.manager import ModelManager
            from model.weights_manager import WeightsManager
            from training.pipeline import TrainingPipeline
            self.model_manager = ModelManager(ROOT, self.registry)
            self.weights = WeightsManager(ROOT, self.registry)
            self.pipeline = TrainingPipeline(ROOT, self.hardware)
        return self.model_manager, self.weights, self.pipeline

    def _ensure_active_model_loaded(self):
        manager, _weights, _pipeline = self._ensure_model_services()
        active = self.registry.active("ALI")
        if not active:
            return False
        current = getattr(manager, "current", None) or {}
        if current.get("version") == active.get("version") and self.runtime.model_engine is not None:
            return True
        try:
            engine, _ = manager.load(active)
            self.runtime.model_engine = engine
            self.model_lbl.configure(text=f"MODEL · {active['version']}")
            return True
        except Exception as exc:
            self.runtime.model_engine = None
            self._append_system(f"Model load unavailable: {exc}", meta="model-error")
            return False

    # ---------- autonomous learning ----------
    def _self_learning_running(self) -> bool:
        return any(
            j.get("kind") == "self-learning" and j.get("status") in {"queued", "running"}
            for j in self.jobs.snapshot()
        )

    def self_learn_now(self):
        if self._self_learning_running():
            self.status.configure(text="Self-learning job is already running")
            return
        db=ROOT / "artifacts" / "harvest.sqlite3"
        conv_db=ROOT / "runtime_conversations.sqlite3"
        steps=int(self.cfg.get("training",{}).get("auto_learning_steps", 1))
        scale=str(self.cfg.get("training",{}).get("auto_learning_scale", "micro"))
        device=str(self.train_profile.get("device", "cpu"))
        def work(progress):
            result=self.self_manager.autonomous_cycle(
                db, conv_db,
                scale=scale, steps=max(1,steps), device=device,
                progress=progress,
            )
            self.root.after(0, self._load_active)
            self.root.after(0, self._refresh_models)
            return result
        self.jobs.run("ALI Auto Self-Learning", work, "self-learning")
        self.status.configure(text="Self-learning cycle queued")
        self.auto_lbl.configure(text="AUTO LEARN · RUNNING")

    def _auto_improvement_tick(self):
        try:
            enabled=bool(self.cfg.get("auto_improve", self.cfg.get("agent",{}).get("auto_learning", True)))
            db=ROOT / "artifacts" / "harvest.sqlite3"
            conv_db=ROOT / "runtime_conversations.sqlite3"
            st=self.self_manager.status(db,conv_db)
            if not enabled:
                self.auto_lbl.configure(text="AUTO LEARN · OFF", fg=C["MUTED"])
            elif self._self_learning_running():
                self.auto_lbl.configure(text=f"AUTO LEARN · {st.get('new_samples',0)} NEW", fg=C["AMBER"])
            elif st.get("ready"):
                self.auto_lbl.configure(text=f"AUTO LEARN · STARTING ({st['new_samples']})", fg=C["GREEN"])
                self.self_learn_now()
            else:
                self.auto_lbl.configure(text=f"AUTO LEARN · {st.get('new_samples',0)}/{self.self_manager.min_new_samples}", fg=C["GREEN"])
        except Exception as exc:
            try:
                self.auto_lbl.configure(text="AUTO LEARN · ERROR", fg=C["RED"])
                self.status.configure(text=f"Auto-learning check failed: {exc}")
            except Exception:
                pass
        finally:
            try:self.root.after(60000, self._auto_improvement_tick)
            except Exception:pass

    # ---------- refresh ----------
    def _refresh_all(self):
        self.populate_tree()
        self._refresh_threads()
        self._refresh_models()
        self._refresh_status()
        self._load_active()

    def _refresh_status(self):
        snap = self.resources.snapshot()
        self.status.configure(
            text=f"CPU {snap.get('cpu_percent', '?')}%  ·  "
                 f"RAM free {snap.get('ram_available_gb', '?')} GB  ·  "
                 f"Disk {snap.get('disk_free_gb', '?')} GB"
        )
        self.perm_lbl.configure(
            text="Permission: " + self.runtime.permission_manager.mode
        )

    def _refresh_hardware_loop(self):
        try:
            self.hardware = detect(probe_torch=False)
            self.policy = choose_policy(self.hardware)
            self.train_profile = training_profile(self.hardware)
            self.device_profile = recommend_for_hardware(self.hardware)
            badge = "P50 SAFE" if self.device_profile.get("id", "").startswith("thinkpad-p50") else "ADAPTIVE"
            self.device_lbl.configure(text=f"{badge} · {self.hardware.cpu_cores}T · {self.hardware.ram_gb:.1f} GB")
            if hasattr(self, "cpu_metric"):
                self.cpu_metric.configure(text=f"{getattr(self.hardware,'cpu_percent',0) or 0:.0f}%")
                self.gpu_metric.configure(text=f"{getattr(self.hardware,'gpu_percent',0) or 0:.0f}%")
                self.ram_metric.configure(text=f"{getattr(self.hardware,'ram_used_percent',0) or 0:.0f}%")
                self.temp_metric.configure(text=f"{getattr(self.hardware,'temperature_c',0) or 0:.1f}°C")
            if hasattr(self, "rh_cpu"):
                self.rh_cpu.configure(text=f"{getattr(self.hardware,'cpu_percent',0) or 0:.0f}%")
                self.rh_gpu.configure(text=f"{getattr(self.hardware,'gpu_percent',0) or 0:.0f}%")
                self.rh_ram.configure(text=f"{getattr(self.hardware,'ram_used_percent',0) or 0:.0f}%")
                self.rh_temp.configure(text=f"{getattr(self.hardware,'temperature_c',0) or 0:.1f}°C")
            self.device_card.configure(
                text=json.dumps(
                    {"hardware": self.hardware.to_dict(), "policy": self.policy},
                    ensure_ascii=False, indent=2,
                )
            )
            self._refresh_status()
        finally:
            self.root.after(4000, self._refresh_hardware_loop)

    def _refresh_jobs_loop(self):
        try:
            self.jobs_list.delete(0, "end")
            for job in self.jobs.snapshot()[-50:]:
                self.jobs_list.insert(
                    "end",
                    f"{job['status']:<11} {job['progress'] * 100:5.1f}%  "
                    f"{job['name']} [{job['id'][:8]}]",
                )
            jobs=self.jobs.snapshot()
            self.workflow_card.configure(text="\n".join(f"{j['status']}: {j['name']}" for j in jobs[-8:]) or "No background jobs.")
            if hasattr(self, "activity"):
                running=next((j for j in reversed(jobs) if j.get('status') in {'queued','running'}), None)
                chosen=running or (jobs[-1] if jobs else None)
                if chosen: self.activity.update_job(chosen); self.rh_task.configure(text=f"{chosen.get('name','')} · {chosen.get('progress',0)*100:.0f}%")
                else: self.rh_task.configure(text="Ready")
                self.rh_model.configure(text=self.model_lbl.cget('text'))
                try:
                    hs=self.hermes_router.status(); self.rh_hermes.configure(text=("connected · RO" if hs.get("exists") else "external · not found")[:42])
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

        self.chat.add_message("user", text, on_copy=self._copy)
        self.history.append({"role": "user", "content": text})
        self.sessions.save_message(self.current_thread, "user", text)

        try:
            envelope = RequestEnvelope(
                raw_text=text, project_dir=self.project_dir, session_id=self.current_thread,
                language="auto", channel="desktop", metadata={"mode": self.ai_mode.get()},
            )
            kca_state = self.kca_router.build_state(envelope)
            self.intent_lbl.configure(
                text=f"{kca_state.intent} · {kca_state.confidence:.0%} · KCA"
            )
            plan = self.orchestrator.make_plan(text)
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
            hroute = self.hermes_router.route(text)
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
            for ev in self.runtime.stream_answer(
                self.history,
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

        def work(progress):
            cfg = PipelineConfig(
                name="ALI",
                stage=f["stage"],
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
        out = filedialog.asksaveasfilename(
            initialdir=str(ROOT / "models" / "gguf"),
            defaultextension=".gguf",
            filetypes=[("GGUF", "*.gguf")],
        )
        if not out:
            return

        def work(progress):
            progress("convert", .2)
            result = GGUFManager().convert(active["hf_dir"], out, "f16")
            progress("validate", .9)
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
                    self.root.after(0, lambda x=line: self.activity.event(str(x), phase="terminal", progress=0.5, status="running"))
                self.root.after(0, lambda: self.activity.event(f"Command completed: {cmd}", phase="terminal", progress=1.0, status="completed"))
            except Exception as exc:
                self.root.after(0, lambda e=exc: self.activity.event("Command error: " + str(e), phase="terminal", progress=1.0, status="error"))
                self.root.after(0, lambda e=exc: self.term.insert("end", "ERROR: " + str(e) + "\n"))

        threading.Thread(target=job, daemon=True).start()

    def _insert_prompt(self, text):
        self.entry.delete("1.0", "end")
        self.entry.insert("1.0", text)
        self.entry.focus_set()

    def _on_return(self, event):
        # Shift+Enter creates a newline; plain Enter submits.
        if event.state & 0x0001:
            return None
        self.send()
        return "break"

    def _on_close(self):
        try:
            self.cfg["language"] = self.language
            self.cfg["runtime"] = {
                "temperature": float(self.temp_var.get()),
                "context": int(self.ctx_var.get()),
                "max_new_tokens": int(self.out_var.get()),
            }
            save_cfg(self.cfg)
        except Exception:
            pass
        self.root.destroy()


def create_root():
    """Create a Tk root with native TkDnD support when available."""
    try:
        from tkinterdnd2 import TkinterDnD
        return TkinterDnD.Tk()
    except Exception:
        return tk.Tk()


def main():
    root = create_root()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
