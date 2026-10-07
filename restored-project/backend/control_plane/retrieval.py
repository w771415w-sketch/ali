from __future__ import annotations
from math import sqrt
import re
class HybridRetriever:
    def __init__(self,knowledge,embedding_fn=None):
        self.knowledge=knowledge;self.embedding_fn=embedding_fn
    def _lex(self,query,limit):
        return self.knowledge.search(query,limit=max(limit*3,10))
    def search(self,query,limit=5):
        lexical=self._lex(query,limit)
        if not self.embedding_fn:return {"mode":"lexical","results":lexical,"embedding_available":False}
        try:
            qv=self.embedding_fn(query); scored=[]
            for r in self.knowledge.rows:
                vec=self.embedding_fn(r["text"]); den=sqrt(sum(x*x for x in qv))*sqrt(sum(x*x for x in vec))
                sim=sum(a*b for a,b in zip(qv,vec))/den if den else 0.0
                scored.append((sim,r))
            emb=[{**r,"score":float(s),"citation":f"{r['source']}#{r['position']}"} for s,r in sorted(scored,key=lambda x:-x[0])[:limit]]
            merged={r["id"]:dict(r,score=float(r.get("score",0))) for r in lexical}
            for r in emb:merged[r["id"]]=dict(r,score=max(float(r.get("score",0)),float(r.get("score",0))))
            return {"mode":"hybrid","results":sorted(merged.values(),key=lambda x:-float(x.get("score",0)))[:limit],"embedding_available":True}
        except Exception as exc:return {"mode":"lexical_fallback","results":lexical,"embedding_available":False,"embedding_error":str(exc)}
