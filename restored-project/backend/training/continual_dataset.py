from __future__ import annotations
import hashlib,json,random
from pathlib import Path
class ContinualDataset:
    """Merge old+new data with deterministic replay; never destructively replaces the source dataset."""
    def __init__(self,root): self.root=Path(root);self.root.mkdir(parents=True,exist_ok=True)
    @staticmethod
    def fingerprint(row): return hashlib.sha256(json.dumps(row,ensure_ascii=False,sort_keys=True).encode("utf-8")).hexdigest()
    def read_jsonl(self,path):
        rows=[]
        for line_no,line in enumerate(Path(path).read_text(encoding="utf-8",errors="replace").splitlines(),1):
            if not line.strip():continue
            row=json.loads(line);row.setdefault("metadata",{});row["metadata"].setdefault("source_line",line_no);rows.append(row)
        return rows
    def merge(self,old_path,new_path,version,seed=17,replay_fraction=.25):
        old=self.read_jsonl(old_path) if old_path and Path(old_path).is_file() else []
        new=self.read_jsonl(new_path);seen={}
        for row in old+new:seen[self.fingerprint(row)]=row
        merged=list(seen.values());random.Random(seed).shuffle(merged)
        old_ids={self.fingerprint(x) for x in old};new_ids={self.fingerprint(x) for x in new}
        replay=[]
        if old and replay_fraction>0: replay=random.Random(seed).sample(old,min(max(1,int(len(old)*float(replay_fraction))),len(old)))
        path=self.root/f"dataset-{version}.jsonl";path.write_text("".join(json.dumps(r,ensure_ascii=False)+"\n" for r in merged),encoding="utf-8")
        manifest={"version":str(version),"records":len(merged),"old_records":len(old),"new_records":len(new),"new_unique":len(new_ids-old_ids),"replay_records":len(replay),"strategy":"cumulative_replay","seed":seed}
        (self.root/f"dataset-{version}.manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
        return {"path":str(path),**manifest}
