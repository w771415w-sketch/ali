from __future__ import annotations
from pathlib import Path
import hashlib,re,json
class KnowledgeBase:
    def __init__(self,root):
        self.root=Path(root); self.root.mkdir(parents=True,exist_ok=True); self.index=self.root/"index.json"
        try:self.rows=json.loads(self.index.read_text(encoding="utf-8"))
        except Exception:self.rows=[]
    def _save(self): self.index.write_text(json.dumps(self.rows,ensure_ascii=False,indent=2),encoding="utf-8")
    def ingest_text(self,source,text,chunk_size=900):
        source_hash=hashlib.sha256(text.encode("utf-8")).hexdigest(); clean=re.sub(r"\s+"," ",text).strip(); added=0
        for start in range(0,len(clean),chunk_size):
            chunk=clean[start:start+chunk_size]
            if not chunk:continue
            chunk_hash=hashlib.sha256((source+chunk).encode("utf-8")).hexdigest()
            if any(r["id"]==chunk_hash for r in self.rows):continue
            self.rows.append({"id":chunk_hash,"source":source,"source_hash":source_hash,"text":chunk,"position":start}); added+=1
        self._save(); return {"source":source,"chunks_added":added,"source_hash":source_hash}
    def ingest_file(self,path):
        p=Path(path); return self.ingest_text(str(p),p.read_text(encoding="utf-8",errors="replace"))
    def search(self,query,limit=5):
        tokens=set(re.findall(r"[\w\u0600-\u06ff]+",query.casefold())); results=[]
        for r in self.rows:
            rt=set(re.findall(r"[\w\u0600-\u06ff]+",r["text"].casefold())); overlap=len(tokens & rt)
            if overlap: results.append((overlap/(len(tokens) or 1),r))
        return [{**r,"score":score,"citation":f"{r['source']}#{r['position']}"} for score,r in sorted(results,key=lambda x:-x[0])[:limit]]
