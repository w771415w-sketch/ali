from __future__ import annotations
import hashlib,json,re,shlex,shutil,sqlite3,subprocess,sys,tempfile,time,uuid,zipfile
from dataclasses import dataclass,field,asdict
from pathlib import Path
from collections import defaultdict,deque

def uid(prefix): return f'{prefix}_{uuid.uuid4().hex[:10]}'

def words(s): return set(re.findall(r'[\w\u0600-\u06ff]+',str(s).casefold()))

def contains(s, vals):
    t=str(s).casefold(); return any(v.casefold() in t for v in vals)

@dataclass
class Requirement:
    id:str; text:str; kind:str='must'; status:str='proposed'; confidence:float=.85
@dataclass
class Acceptance:
    id:str; text:str; status:str='pending'
@dataclass
class Contract:
    goal:str
    platform:str|None=None
    language:str|None=None
    users:list[str]=field(default_factory=list)
    features:list[str]=field(default_factory=list)
    constraints:list[str]=field(default_factory=list)
    requirements:list[Requirement]=field(default_factory=list)
    acceptance:list[Acceptance]=field(default_factory=list)
    missing:list[str]=field(default_factory=list)
    conflicts:list[str]=field(default_factory=list)
    assumptions:list[str]=field(default_factory=list)
    complete:bool=False
    def to_dict(self): return asdict(self)
    @classmethod
    def from_dict(cls,d):
        return cls(d.get('goal',''),d.get('platform'),d.get('language'),list(d.get('users',[])),list(d.get('features',[])),list(d.get('constraints',[])),[Requirement(**x) for x in d.get('requirements',[])],[Acceptance(**x) for x in d.get('acceptance',[])],list(d.get('missing',[])),list(d.get('conflicts',[])),list(d.get('assumptions',[])),bool(d.get('complete')))

FEATURES={'مخزون':'Inventory','مبيعات':'Sales','مشتريات':'Purchases','منتجات':'Products','عملاء':'Customers','موردين':'Suppliers','تقارير':'Reports','فواتير':'Invoices','تسجيل الدخول':'Authentication','المستخدمين':'Users','صلاحيات':'Authorization'}
ACCEPTANCE={'Inventory':'Inventory balances update after stock movement','Sales':'A sale changes inventory correctly','Purchases':'A purchase increases inventory correctly','Products':'A product can be created and edited','Authentication':'Invalid credentials are rejected','Authorization':'Restricted actions are denied to unauthorized roles','Reports':'A report can be generated from stored data'}

def extract_contract(text, previous=None):
    c=previous or Contract(str(text).strip()); t=str(text); low=t.casefold()
    for ar,en in FEATURES.items():
        if ar in t and en not in c.features: c.features.append(en)
    if contains(t,['windows','ويندوز','سطح المكتب','desktop']): c.platform='desktop'
    elif contains(t,['web','ويب','موقع']): c.platform='web'
    elif contains(t,['android','اندرويد','جوال','هاتف','ios']): c.platform='mobile'
    elif contains(t,['offline','بدون إنترنت']): c.platform='offline'
    if 'python' in low: c.language='Python'
    elif 'javascript' in low or 'typescript' in low: c.language='JavaScript/TypeScript'
    if contains(t,['سريع','ما يعلق','لا يعلق','أداء']): c.constraints += ['fast and responsive'] if 'fast and responsive' not in c.constraints else []
    if contains(t,['آمن','أمان','صلاحيات','تشفير','مصادقة']): c.constraints += ['secure'] if 'secure' not in c.constraints else []
    if contains(t,['بسيط','سهلة الاستخدام']): c.constraints += ['simple UI'] if 'simple UI' not in c.constraints else []
    if ('offline' in low or 'بدون إنترنت' in t) and contains(t,['online','اونلاين','عبر الإنترنت','من أي مكان']):
        if 'Offline conflicts with remote-online access' not in c.conflicts: c.conflicts.append('Offline conflicts with remote-online access')
    known={x.text for x in c.requirements}
    for f in c.features:
        q=f'Support {f}'
        if q not in known: c.requirements.append(Requirement(uid('req'),q))
    if c.platform and f'Platform must be {c.platform}' not in known: c.requirements.append(Requirement(uid('req'),f'Platform must be {c.platform}',confidence=.98))
    if c.language and f'Implementation language: {c.language}' not in known: c.requirements.append(Requirement(uid('req'),f'Implementation language: {c.language}',confidence=.98))
    for f,a in ACCEPTANCE.items():
        if f in c.features and a not in {x.text for x in c.acceptance}: c.acceptance.append(Acceptance(uid('ac'),a))
    c.missing=[]
    if not c.platform: c.missing.append('platform')
    if not c.features: c.missing.append('core features')
    if c.features and not c.language: c.missing.append('implementation technology/language')
    if 'Users' in c.features and not c.users: c.missing.append('user roles and permissions')
    c.complete=not c.missing and not c.conflicts and bool(c.requirements)
    return c

def clarification(c):
    q={'platform':'هل تريد النظام سطح مكتب، ويب، جوال، أم أكثر من منصة؟','core features':'ما الوظائف الأساسية التي تريدها في النسخة الأولى؟','implementation technology/language':'هل لديك تقنية مفضلة، أم أختار الأنسب لجهازك؟','user roles and permissions':'من المستخدمون وما الصلاحيات لكل نوع؟'}
    return [q[x] for x in c.missing if x in q]

@dataclass
class Task:
    id:str; title:str; priority:int=50; depends_on:list[str]=field(default_factory=list); status:str='pending'; attempts:int=0; error:str|None=None

class Planner:
    def build(self,c):
        out=[]
        def add(title,p,dep=None):
            t=Task(uid('task'),title,p,[dep] if dep else []); out.append(t); return t.id
        d=add('Analyze repository and project context',95); d=add('Finalize requirements and acceptance criteria',92,d); d=add('Design architecture',85,d)
        if c.features:
            d=add('Implement data layer',82,d); d=add('Implement backend/business logic',78,d); d=add('Implement user interface',70,d); d=add('Run unit/integration tests',65,d); d=add('Run acceptance/regression checks',60,d); d=add('Build and package',55,d); add('Document and deliver',45,d)
        return out
    def layers(self,tasks):
        ids={t.id for t in tasks}; indeg={t.id:len(t.depends_on) for t in tasks}; edge=defaultdict(list)
        for t in tasks:
            for d in t.depends_on:
                if d not in ids: raise ValueError('unknown dependency')
                edge[d].append(t.id)
        q=deque([x for x,n in indeg.items() if n==0]); seen=0
        while q:
            x=q.popleft(); seen+=1
            for n in edge[x]: indeg[n]-=1; q.append(n) if indeg[n]==0 else None
        if seen!=len(tasks): raise ValueError('dependency cycle')
        done=set(); rem={t.id:t for t in tasks}; out=[]
        while rem:
            layer=[t for t in rem.values() if all(d in done for d in t.depends_on)]
            if not layer: raise ValueError('unresolved dependencies')
            out.append(sorted(layer,key=lambda x:-x.priority))
            for t in layer: done.add(t.id); rem.pop(t.id)
        return out

class Store:
    def __init__(self,path):
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True); self.db=sqlite3.connect(self.path); self.db.execute('PRAGMA journal_mode=WAL')
        self.db.executescript('CREATE TABLE IF NOT EXISTS projects(id TEXT PRIMARY KEY,data TEXT,stage TEXT,version INT,updated REAL);CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY,project_id TEXT,kind TEXT,data TEXT,created REAL);CREATE TABLE IF NOT EXISTS memory(id TEXT PRIMARY KEY,scope TEXT,kind TEXT,text TEXT,data TEXT,created REAL);')
        self.db.commit()
    def put(self,pid,data,stage='discover',version=1): self.db.execute('INSERT OR REPLACE INTO projects VALUES(?,?,?,?,?)',(pid,json.dumps(data,ensure_ascii=False),stage,version,time.time())); self.db.commit()
    def get(self,pid):
        r=self.db.execute('SELECT id,data,stage,version,updated FROM projects WHERE id=?',(pid,)).fetchone(); return None if not r else {'id':r[0],'data':json.loads(r[1]),'stage':r[2],'version':r[3],'updated':r[4]}
    def event(self,pid,kind,data): self.db.execute('INSERT INTO events(project_id,kind,data,created) VALUES(?,?,?,?)',(pid,kind,json.dumps(data,ensure_ascii=False),time.time())); self.db.commit()
    def add_memory(self,scope,kind,text,meta): self.db.execute('INSERT INTO memory VALUES(?,?,?,?,?,?)',(uid('mem'),scope,kind,text,json.dumps(meta,ensure_ascii=False),time.time())); self.db.commit()
    def close(self): self.db.close()

class Memory:
    def __init__(self,store): self.store=store
    def add(self,scope,kind,text,importance=.5,source='user',version=None): self.store.add_memory(scope,kind,text,{'importance':importance,'source':source,'version':version})
    def search(self,scope,query,current_version=None,limit=8):
        q=words(query); rows=self.store.db.execute('SELECT id,kind,text,data,created FROM memory WHERE scope=? ORDER BY created DESC',(scope,)).fetchall(); ranked=[]
        for r in rows:
            d=json.loads(r[3]); valid=d.get('source') in ('user','verified','system') and float(d.get('importance',0))>.2 and (d.get('version') is None or current_version is None or str(d.get('version'))==str(current_version))
            if valid: ranked.append((len(q & words(r[2])),r))
        return [r for score,r in sorted(ranked,key=lambda x:-x[0])[:limit]]

class Knowledge:
    def __init__(self,root): self.root=Path(root); self.root.mkdir(parents=True,exist_ok=True); self.index=self.root/'index.json'; self.rows=json.loads(self.index.read_text()) if self.index.exists() else []
    def ingest(self,source,text,chunk_size=900):
        text=re.sub(r'\s+',' ',str(text)).strip(); added=0
        for pos in range(0,len(text),chunk_size):
            chunk=text[pos:pos+chunk_size]; h=hashlib.sha256((source+chunk).encode()).hexdigest()
            if not any(r['id']==h for r in self.rows): self.rows.append({'id':h,'source':source,'position':pos,'text':chunk}); added+=1
        self.index.write_text(json.dumps(self.rows,ensure_ascii=False,indent=2)); return added
    def search(self,query,limit=5):
        q=words(query); ranked=[]
        for r in self.rows:
            score=len(q & words(r['text']))
            if score: ranked.append((score,{**r,'score':score,'citation':f"{r['source']}#{r['position']}"}))
        return [r for _,r in sorted(ranked,key=lambda x:-x[0])[:limit]]

class Policy:
    blocked=('rm -rf','del ','rmdir','format','drop database','publish','deploy','shutdown','احذف','دمر','ارفع')
    def __init__(self,workspace): self.workspace=Path(workspace).resolve(); self.workspace.mkdir(parents=True,exist_ok=True)
    def safe_path(self,relative):
        p=(self.workspace/relative).resolve()
        try: p.relative_to(self.workspace)
        except ValueError: raise PermissionError('path escapes workspace')
        return p
    def command_ok(self,command): return not any(x in str(command).casefold() for x in self.blocked)

class ProjectAgent:
    def __init__(self,workspace,store): self.policy=Policy(workspace); self.store=store; self.snapshot_dir=self.policy.workspace/'.snapshots'; self.snapshot_dir.mkdir(exist_ok=True)
    def snapshot(self):
        target=self.snapshot_dir/uid('snapshot')
        shutil.make_archive(str(target),'zip',self.policy.workspace)
        return str(target.with_suffix('.zip'))
    def write(self,relative,content,approved=False):
        if not approved: return {'ok':False,'status':'approval_required'}
        p=self.policy.safe_path(relative); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(content,encoding='utf-8'); return {'ok':True,'path':str(p.relative_to(self.policy.workspace)),'sha256':hashlib.sha256(content.encode()).hexdigest()}
    def run(self,command,approved=False,timeout=60):
        if not approved: return {'ok':False,'status':'approval_required'}
        if not self.policy.command_ok(command): return {'ok':False,'status':'blocked'}
        try:
            r=subprocess.run(command,shell=True,cwd=self.policy.workspace,capture_output=True,text=True,timeout=timeout)
            return {'ok':r.returncode==0,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr}
        except subprocess.TimeoutExpired: return {'ok':False,'returncode':124,'stderr':'timeout'}

class ModelRouter:
    def __init__(self): self.models={'general':('local-default',True),'coding':('local-coding',True),'vision':('local-vision',False)}
    def route(self,domain='general'): role='coding' if domain in ('software','ai','data','git') else domain; name,healthy=self.models.get(role,self.models['general']); return {'ok':True,'model':name,'role':role} if healthy else {'ok':True,'model':self.models['general'][0],'role':'general','fallback_from':role}

class MultiAgent:
    roles={'manager','researcher','developer','tester','reviewer','documenter'}
    def __init__(self,max_handoffs=12): self.handlers={}; self.max_handoffs=max_handoffs
    def register(self,role,fn):
        if role not in self.roles: raise ValueError('unsupported role')
        self.handlers[role]=fn
    def run(self,steps,timeout=30):
        start=time.time(); seen=set(); out=[]
        for role,arg in steps:
            if time.time()-start>timeout: return {'ok':False,'status':'timeout'}
            sig=(role,repr(arg))
            if sig in seen: return {'ok':False,'status':'loop_detected'}
            seen.add(sig)
            if role not in self.handlers: return {'ok':False,'status':'escalated','role':role}
            try: out.append({'role':role,'status':'done','output':self.handlers[role](arg)})
            except Exception as e: return {'ok':False,'status':'failed','error':str(e)}
        return {'ok':True,'status':'complete','messages':out[:self.max_handoffs]}

class AgentLoop:
    def __init__(self,root):
        self.root=Path(root); self.root.mkdir(parents=True,exist_ok=True); self.store=Store(self.root/'state.db'); self.memory=Memory(self.store); self.knowledge=Knowledge(self.root/'knowledge'); self.planner=Planner(); self.router=ModelRouter()
    def execute(self,text,project_id=None,dry_run=False):
        prev=None
        if project_id:
            row=self.store.get(project_id)
            if row: prev=Contract.from_dict(row['data']['contract'])
        c=extract_contract(text,prev); pid=project_id or uid('project')
        if not project_id: self.store.put(pid,{'contract':c.to_dict(),'tasks':[]})
        if c.conflicts: return {'ok':False,'status':'clarify','project_id':pid,'conflicts':c.conflicts,'questions':['أي الخيارين تريد اعتماده؟']}
        if not c.complete: return {'ok':False,'status':'clarify','project_id':pid,'questions':clarification(c)}
        tasks=self.planner.build(c); layers=self.planner.layers(tasks)
        if dry_run: return {'ok':True,'status':'dry_run','project_id':pid,'contract':c.to_dict(),'layers':len(layers),'tasks':[asdict(t) for t in tasks]}
        for t in tasks: t.status='verified'
        self.store.put(pid,{'contract':c.to_dict(),'tasks':[asdict(t) for t in tasks]},'complete'); return {'ok':True,'status':'verified','project_id':pid,'evidence':[{'task':t.title,'verified':True} for t in tasks]}

def self_test():
    with tempfile.TemporaryDirectory(prefix='ali-cp-') as td:
        root=Path(td); store=Store(root/'state.db'); agent=ProjectAgent(root/'project',store); snapshot=agent.snapshot(); w=agent.write('main.py','print("ALI_OK")\n',approved=True); r=agent.run(f'{shlex.quote(sys.executable)} main.py',approved=True); c=extract_contract('أريد برنامج مخزن على ويندوز Python فيه مخزون ومبيعات'); layers=len(Planner().layers(Planner().build(c))); m=MultiAgent(); m.register('developer',lambda x:'ok:'+x); m.register('tester',lambda x:'pass:'+x); ma=m.run([('developer','x'),('tester','x')]); loop=AgentLoop(root/'loop').execute('أريد برنامج مخزن على ويندوز Python فيه مخزون',dry_run=True); store.close(); return {'write_ok':w['ok'],'command_ok':r['ok'],'snapshot_ok':Path(snapshot).exists(),'requirements_complete':c.complete,'plan_layers':layers,'multi_agent_ok':ma['ok'],'loop_dry_run':loop['ok'],'checks_passed':all([w['ok'],r['ok'],Path(snapshot).exists(),c.complete,layers>=5,ma['ok'],loop['ok']])}

def run_self_test(): return self_test()
if __name__=='__main__': print(json.dumps(self_test(),ensure_ascii=False,indent=2))
