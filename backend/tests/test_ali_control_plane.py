from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parents[1]))
from ali_control_plane import extract_contract, clarification, Planner, Store, Memory, ProjectAgent, MultiAgent, AgentLoop

def test_requirement_gap():
    c=extract_contract('أريد برنامج لإدارة مشروعي'); assert not c.complete and clarification(c)

def test_conflict():
    assert extract_contract('أريد النظام Offline وأريد المستخدمين يدخلون من أي مكان عبر الإنترنت').conflicts

def test_planning():
    c=extract_contract('أريد برنامج مخزن على ويندوز Python فيه مخزون ومبيعات'); assert len(Planner().layers(Planner().build(c)))>=5

def test_memory(tmp_path):
    s=Store(tmp_path/'state.db'); m=Memory(s); m.add('p','preference','Python SQLite',.9,'user','1'); assert m.search('p','Python SQLite','1'); s.close()

def test_secure_execution(tmp_path):
    s=Store(tmp_path/'state.db'); a=ProjectAgent(tmp_path/'project',s); assert a.write('x.py','print(1)\n',True)['ok']; assert a.run(f'{sys.executable} x.py',True)['ok']
    try: a.write('../outside','x',True); assert False
    except PermissionError: pass
    assert a.run('rm -rf project',True)['status']=='blocked'; s.close()

def test_multiagent_and_loop(tmp_path):
    m=MultiAgent(); m.register('developer',lambda x:x); m.register('tester',lambda x:x); assert m.run([('developer','x'),('tester','x')])['ok']; assert AgentLoop(tmp_path/'loop').execute('أريد برنامج مخزن على ويندوز Python فيه مخزون',dry_run=True)['ok']
