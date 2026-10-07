from __future__ import annotations
from dataclasses import dataclass,field
import heapq,time,uuid
@dataclass(order=True)
class QueueItem:
    sort_key:tuple=field(init=False,repr=False); priority:int; created_at:float
    id:str=field(default_factory=lambda:"job_"+uuid.uuid4().hex[:10],compare=False)
    handler:object=field(default=None,compare=False); status:str=field(default="queued",compare=False); result:object=None; error:str|None=None
    def __post_init__(self): self.sort_key=(-self.priority,self.created_at)
class PriorityScheduler:
    def __init__(self,max_workers=1): self.max_workers=max(1,int(max_workers)); self._queue=[]; self.running=0
    def submit(self,handler,priority=50):
        x=QueueItem(priority,time.time(),handler=handler); heapq.heappush(self._queue,(x.sort_key,x)); return x.id
    def run_next(self):
        if self.running>=self.max_workers or not self._queue:return None
        _,x=heapq.heappop(self._queue); self.running+=1; x.status="running"
        try:x.result=x.handler(); x.status="complete"
        except Exception as e:x.error=str(e); x.status="failed"
        finally:self.running-=1
        return x
    def pending(self): return len(self._queue)