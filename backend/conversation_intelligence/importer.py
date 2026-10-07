from __future__ import annotations
import hashlib,json,re
from pathlib import Path
SECRET_PATTERNS=[
 re.compile(r"(?i)(password|passwd|token|api[_-]?key|secret)\s*[:=]\s*[^\s,;]+"),
 re.compile(r"(?i)bearer\s+[A-Za-z0-9._-]+"),
 re.compile(r"(?i)login\s*=\s*[^\s,;]+"),
]
PATH_RE=re.compile(r"(?i)([A-Za-z]:\\[^\n]+|/home/[^\n]+|/mnt/data/[^\n]+)")
class ConversationImporter:
    def __init__(self):
        self.categories={
            "clarification":["المعلومات غير كافية","أحتاج معرفة","تحديد"],
            "verification":["تحقق","اختبر","التحقق","لا تصدق النظام"],
            "debugging":["Debugging","خطأ","الإصلاح","سبب المشكلة"],
            "tool_use":["Tool Call","الأدوات","استخدم أداة"],
            "project_execution":["Architecture","Database","Backend","Frontend","Build"],
            "arabic":["العربية","اللهجات","الأخطاء الإملائية"],
            "continuous_learning":["Checkpoint","Continued Training","GGUF","Regression"]
        }
    @staticmethod
    def sanitize(text):
        out=str(text);flags=[]
        for pat in SECRET_PATTERNS:
            if pat.search(out):out=pat.sub("[REDACTED_SECRET]",out);flags.append("secret")
        if PATH_RE.search(out):out=PATH_RE.sub("[REDACTED_PATH]",out);flags.append("path")
        return out,sorted(set(flags))
    def classify(self,text):
        t=str(text);scores={k:sum(1 for token in v if token.casefold() in t.casefold()) for k,v in self.categories.items()}
        return max(scores,key=scores.get) if max(scores.values() or [0]) else "general"
    def build_candidate(self,source_path,text):
        safe,flags=self.sanitize(text)
        return {"source":str(source_path),"source_sha256":hashlib.sha256(text.encode("utf-8")).hexdigest(),"category":self.classify(safe),"text":safe,"privacy_flags":flags,"approved":False}
    def import_markdown(self,path,max_candidates=500):
        p=Path(path);raw=p.read_text(encoding="utf-8",errors="replace")
        blocks=[x.strip() for x in re.split(r"\n(?=##+\s)",raw) if x.strip()]
        rows=[self.build_candidate(p,b) for b in blocks[:max_candidates] if len(b)>120]
        return {"source":str(p),"source_sha256":hashlib.sha256(raw.encode()).hexdigest(),"candidates":rows,"requires_review":True}
    def write_candidates(self,candidates,path):
        p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
        with p.open("w",encoding="utf-8") as f:
            for row in candidates:f.write(json.dumps(row,ensure_ascii=False)+"\n")
        return {"path":str(p),"records":len(candidates)}
