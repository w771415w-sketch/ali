from __future__ import annotations
import hashlib,json,random,re
from pathlib import Path
class DatasetPipeline:
    def __init__(self,root):self.root=Path(root);self.root.mkdir(parents=True,exist_ok=True)
    @staticmethod
    def key(row):return hashlib.sha256(json.dumps(row,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
    def validate_jsonl(self,path):
        good=[];errors=[]
        for n,line in enumerate(Path(path).read_text(encoding="utf-8",errors="replace").splitlines(),1):
            if not line.strip():continue
            try:
                obj=json.loads(line); msgs=obj.get("messages")
                if not isinstance(msgs,list) or not any(m.get("role")=="user" for m in msgs):raise ValueError("missing valid messages")
                good.append(obj)
            except Exception as e:errors.append({"line":n,"error":str(e)})
        return good,errors
    def quality_filter(self,rows,min_user_chars=2,max_messages=64):
        out=[];rejected=[]
        for i,row in enumerate(rows):
            msgs=row.get("messages",[]); users=[m.get("content","") for m in msgs if m.get("role")=="user"]; assistants=[m.get("content","") for m in msgs if m.get("role")=="assistant"]
            if not users or not assistants or len(msgs)>max_messages or any(len(str(x).strip())<min_user_chars for x in users):rejected.append({"index":i,"reason":"quality_filter"})
            else:out.append(row)
        return out,rejected
    def dedupe(self,rows):
        seen=set();out=[]
        for r in rows:
            k=self.key(r)
            if k not in seen:seen.add(k);out.append(r)
        return out
    def split(self,rows,seed=17):
        rows=list(rows);random.Random(seed).shuffle(rows);n=len(rows);a=int(n*.9);b=int(n*.95);return rows[:a],rows[a:b],rows[b:]
    def detect_leakage(self,train,other_splits):
        keys={self.key(x) for x in train};return [{"split":name,"index":i} for name,rows in other_splits.items() for i,r in enumerate(rows) if self.key(r) in keys]
    def write_version(self,rows,version):
        p=self.root/f"dataset-{version}.jsonl";m=self.root/f"dataset-{version}.manifest.json"
        with p.open("w",encoding="utf-8") as f:
            for r in rows:f.write(json.dumps(r,ensure_ascii=False)+"\n")
        sha=hashlib.sha256(p.read_bytes()).hexdigest();m.write_text(json.dumps({"version":str(version),"records":len(rows),"sha256":sha,"format":"jsonl"},ensure_ascii=False,indent=2),encoding="utf-8");return {"path":str(p),"manifest":str(m),"sha256":sha,"records":len(rows)}