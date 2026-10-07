from pathlib import Path
import json, sqlite3
from integration.hermes.config import HermesConfig
from integration.hermes.adapter import HermesAdapter
from integration.hermes.router import HermesContextRouter

def make_hermes(tmp_path):
    root=tmp_path/'Hermes'; (root/'memories').mkdir(parents=True); (root/'skills'/'demo').mkdir(parents=True)
    (root/'SOUL.md').write_text('soul',encoding='utf-8'); (root/'memories'/'MEMORY.md').write_text('memory',encoding='utf-8'); (root/'memories'/'USER.md').write_text('user',encoding='utf-8'); (root/'skills'/'demo'/'SKILL.md').write_text('skill',encoding='utf-8')
    (root/'kanban.db').touch()
    con=sqlite3.connect(root/'projects.db'); con.execute('create table items(name text)'); con.execute("insert into items values ('A')"); con.commit(); con.close()
    (root/'.env').write_text('SECRET=x',encoding='utf-8'); (root/'auth.json').write_text('{"token":"x"}',encoding='utf-8')
    return root

def test_adapter_read_only_and_secret_block(tmp_path):
    root=make_hermes(tmp_path); a=HermesAdapter(HermesConfig(root=str(root)))
    assert a.read_text('memories/MEMORY.md')=='memory'
    assert a.read_database('projects.db','SELECT name FROM items')[0]['name']=='A'
    try: a.read_text('.env')
    except PermissionError: pass
    else: raise AssertionError('secret file was readable')

def test_router_only_routes_hermes_requests(tmp_path):
    root=make_hermes(tmp_path); r=HermesContextRouter(HermesConfig(root=str(root)))
    assert r.route('كيف أفتح ملفًا محليًا؟')['used'] is False
    assert r.route('اعرض ذاكرة Hermes')['used'] is True
