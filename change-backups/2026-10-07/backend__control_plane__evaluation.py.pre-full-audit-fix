from __future__
from dataclasses import dataclass
from typing import Callable,Any
@dataclass
class EvalCase:
    id:str; category:str; run:Callable[[],Any]; predicate:Callable[[Any],bool]; description:str=""
class Evaluator:
    CATEGORIES=("golden","regression","adversarial","coding","arabic","long_context","tool_use","agent","safety","real_world")
    def run(self,cases):
        results=[]
        for c in cases:
            try: out=c.run(); passed=bool(c.predicate(out)); err=None
            except Exception as e: out=None; passed=False; err=str(e)
            results.append({"id":c.id,"category":c.category,"passed":passed,"error":err,"output":out,"description":c.description})
        return {"passed":all(x["passed"] for x in results),"count":len(results),"passed_count":sum(x["passed"] for x in results),"results":results}
