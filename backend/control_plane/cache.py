from __future__ import annotations
import time

class TTLCache:
    def __init__(self,max_items=256): self.max_items=max_items; self.data={}
    def get(self,key,default=None):
        row=self.data.get(key)
        if not row:return default
        if row[1] and row[1]<time.monotonic(): self.data.pop(key,None); return default
        return row[0]
    def set(self,key,value,ttl_s=60):
        if len(self.data)>=self.max_items and key not in self.data:self.data.pop(next(iter(self.data)))
        self.data[key]=(value,time.monotonic()+ttl_s if ttl_s else 0); return value
    def clear(self): self.data.clear()
