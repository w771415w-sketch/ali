from __future__ import annotations
from dataclasses import dataclass
from collections import deque
from pathlib import Path
import sqlite3,threading,time,json
@dataclass
class Budget:
    max_seconds:float=300; max_tool_calls:int=30; max_tasks:int=50; max_tokens:int|None=None
    started_at:float=0; tool_calls:int=0; tasks:int=0; tokens:int=0
    def __post_init__(self):
        if not self.started_at:self.started_at=time.monotonic()
    def check(self):
        if time.monotonic()-self.started_at>self.max_seconds:raise TimeoutError("time budget exceeded")
    def consume_tool(self,n=1): self.tool_calls+=n; self.check(); assert self.tool_calls<=self.max_tool_calls,"tool budget exceeded"
    def consume_task(self,n=1): self.tasks+=n; self.check(); assert self.tasks<=self.max_tasks,"task budget exceeded"
    def consume_tokens(self,n): self.tokens+=n; self.check(); assert self.max_tokens is None or self.tokens<=self.max_tokens,"token budget exceeded"
    def snapshot(self): return {"elapsed_s":time.monotonic()-self.started_at,"max_seconds":self.max_seconds,"tool_calls":self.tool_calls,"tasks":self.tasks,"tokens":self.tokens}
class RateLimiter:
    def __init__(self,limit,window_s=60): self.limit=limit; self.window_s=window_s; self._d={}; self._lock=threading.Lock()
    def allow(self,key):
        now=time.monotonic()
        with self._lock:
            q=self._d.setdefault(str(key),deque())
            while q and now-q[0]>=self.window_s:q.popleft()
            if len(q)>=self.limit:return False
            q.append(now); return True
class CircuitBreaker:
    def __init__(self,failure_threshold=3,recovery_s=30): self.threshold=failure_threshold; self.recovery_s=recovery_s; self.failures=0; self.state="closed"; self.opened_at=0
    def allow(self):
        if self.state=="closed":return True
        if self.state=="open" and time.monotonic()-self.opened_at>=self.recovery_s:self.state="half_open"; return True
        return self.state=="half_open"
    def success(self): self.failures=0; self.state="closed"; self.opened_at=0
    def failure(self):
        self.failures+=1
        if self.failures>=self.threshold:self.state="open"; self.opened_at=time.monotonic()
class RetryPolicy:
    def __init__(self,attempts=2,backoff_s=.05): self.attempts=max(1,attempts); self.backoff_s=backoff_s
    def run(self,fn):
        last=None
        for i in range(self.attempts):
            try:return fn()
            except Exception as e:
                last=e
                if i+1<self.attempts:time.sleep(self.backoff_s*(i+1))
        raise last
class IdempotencyLedger:
    def __init__(self,path):
        self.cx=sqlite3.connect(Path(path),check_same_thread=False,isolation_level=None); self.lock=threading.Lock()
        self.cx.execute("CREATE TABLE IF NOT EXISTS idempotency(key TEXT PRIMARY KEY,status TEXT,result TEXT,created REAL,updated REAL)")
    def claim(self,key):
        now=time.time()
        with self.lock:
            self.cx.execute("BEGIN IMMEDIATE")
            try:
                cur=self.cx.execute("INSERT OR IGNORE INTO idempotency VALUES(?,?,?,?,?)",(key,"running",None,now,now)); self.cx.execute("COMMIT"); return cur.rowcount==1
            except Exception:self.cx.execute("ROLLBACK"); raise
    def complete(self,key,result): self.cx.execute("UPDATE idempotency SET status='complete',result=?,updated=? WHERE key=?",(json.dumps(result,ensure_ascii=False),time.time(),key))
    def fail(self,key,error): self.cx.execute("UPDATE idempotency SET status='failed',result=?,updated=? WHERE key=?",(json.dumps({"error":error},ensure_ascii=False),time.time(),key))
    def get(self,key):
        r=self.cx.execute("SELECT key,status,result,created,updated FROM idempotency WHERE key=?",(key,)).fetchone()
        return None if not r else {"key":r[0],"status":r[1],"result":None if not r[2] else json.loads(r[2]),"created":r[3],"updated":r[4]}
    def close(self): self.cx.close()
class CancellationToken:
    def __init__(self): self._cancelled=False
    def cancel(self): self._cancelled=True
    def check(self):
        if self._cancelled: raise RuntimeError("cancelled")