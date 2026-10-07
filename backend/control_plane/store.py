from __future__ import annotations
import json,sqlite3,time
from pathlib import Path
class StateStore:
    def __init__(self,path):
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True); self.cx=sqlite3.connect(self.path,check_same_thread=False)
        self.cx.execute("PRAGMA journal_mode=WAL"); self.cx.execute("PRAGMA foreign_keys=ON"); self._schema()
    def _schema(self):
        self.cx.executescript("""CREATE TABLE IF NOT EXISTS projects(id TEXT PRIMARY KEY,version INTEGER NOT NULL,goal TEXT NOT NULL,stage TEXT NOT NULL,data TEXT NOT NULL,updated_at REAL NOT NULL);CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT,project_id TEXT,kind TEXT NOT NULL,data TEXT NOT NULL,created_at REAL NOT NULL);CREATE TABLE IF NOT EXISTS memory(id TEXT PRIMARY KEY,scope TEXT NOT NULL,kind TEXT NOT NULL,text TEXT NOT NULL,data TEXT NOT NULL,created_at REAL NOT NULL);CREATE TABLE IF NOT EXISTS failures(id TEXT PRIMARY KEY,signature TEXT NOT NULL,error TEXT NOT NULL,data TEXT NOT NULL,created_at REAL NOT NULL);CREATE TABLE IF NOT EXISTS artifacts(id TEXT PRIMARY KEY,kind TEXT NOT NULL,path TEXT NOT NULL,sha256 TEXT NOT NULL,version TEXT NOT NULL,metadata TEXT NOT NULL,created_at REAL NOT NULL);CREATE TABLE IF NOT EXISTS decisions(id TEXT PRIMARY KEY,project_id TEXT NOT NULL,topic TEXT NOT NULL,choice TEXT NOT NULL,reason TEXT NOT NULL,data TEXT NOT NULL,created_at REAL NOT NULL);"""); self.cx.commit()
    def put_project(self,project_id,version,goal,stage,data):
        self.cx.execute("INSERT INTO projects(id,version,goal,stage,data,updated_at) VALUES(?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET version=excluded.version,goal=excluded.goal,stage=excluded.stage,data=excluded.data,updated_at=excluded.updated_at",(project_id,version,goal,stage,json.dumps(data,ensure_ascii=False),time.time())); self.cx.commit()
    def get_project(self,project_id):
        row=self.cx.execute("SELECT id,version,goal,stage,data,updated_at FROM projects WHERE id=?",(project_id,)).fetchone();
        if not row:return None
        return {"id":row[0],"version":row[1],"goal":row[2],"stage":row[3],"data":json.loads(row[4]),"updated_at":row[5]}
    def event(self,project_id,kind,data): self.cx.execute("INSERT INTO events(project_id,kind,data,created_at) VALUES(?,?,?,?)",(project_id,kind,json.dumps(data,ensure_ascii=False),time.time())); self.cx.commit()
    def memory(self,scope,kind,text,data):
        mid=f"mem_{abs(hash((scope,kind,text,time.time()))) & 0xffffffff:08x}"; self.cx.execute("INSERT OR REPLACE INTO memory(id,scope,kind,text,data,created_at) VALUES(?,?,?,?,?,?)",(mid,scope,kind,text,json.dumps(data,ensure_ascii=False),time.time())); self.cx.commit(); return mid
    def memories(self,scope,limit=20):
        rows=self.cx.execute("SELECT id,kind,text,data,created_at FROM memory WHERE scope=? ORDER BY created_at DESC LIMIT ?",(scope,int(limit))).fetchall(); return [{"id":r[0],"kind":r[1],"text":r[2],"data":json.loads(r[3]),"created_at":r[4]} for r in rows]
    def failure(self,fid,signature,error,data): self.cx.execute("INSERT OR REPLACE INTO failures(id,signature,error,data,created_at) VALUES(?,?,?,?,?)",(fid,signature,error,json.dumps(data,ensure_ascii=False),time.time())); self.cx.commit()
    def failures(self,signature=None,limit=20):
        q="SELECT id,signature,error,data,created_at FROM failures"; args=[]
        if signature:q+=" WHERE signature=?"; args.append(signature)
        q+=" ORDER BY created_at DESC LIMIT ?"; args.append(int(limit)); rows=self.cx.execute(q,args).fetchall(); return [{"id":r[0],"signature":r[1],"error":r[2],"data":json.loads(r[3]),"created_at":r[4]} for r in rows]
    def close(self): self.cx.close()
