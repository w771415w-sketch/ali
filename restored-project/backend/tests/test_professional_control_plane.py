from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parents[1]))
from control_plane.code_intelligence import CodeIntelligence
from control_plane.dataset import DatasetPipeline
from control_plane.reliability import Budget,CircuitBreaker,RetryPolicy,CancellationToken
from control_plane.transaction import Transaction
from control_plane.project_io import Workspace
from control_plane.self_improvement import ImprovementManager

def test_code_intelligence(tmp_path):
    p=tmp_path/"x.py";p.write_text("import os\ndef hello():\n    return 1\n",encoding="utf-8")
    r=CodeIntelligence().parse_project(tmp_path)
    assert r["python"][0]["symbols"][0]["name"]=="hello"

def test_dataset_pipeline(tmp_path):
    d=DatasetPipeline(tmp_path)
    rows=[{"messages":[{"role":"user","content":"hello"},{"role":"assistant","content":"hi"}]}]*2
    clean,_=d.quality_filter(rows)
    assert len(d.dedupe(clean))==1

def test_reliability():
    b=Budget(max_tool_calls=1);b.consume_tool()
    try:b.consume_tool();assert False
    except AssertionError:pass
    c=CircuitBreaker(2);c.failure();c.failure();assert not c.allow()

def test_retry_cancel():
    n={"x":0}
    def f():
        n["x"]+=1
        if n["x"]<2:raise RuntimeError("boom")
        return 7
    assert RetryPolicy(2,0).run(f)==7
    t=CancellationToken();t.cancel()
    try:t.check();assert False
    except RuntimeError:pass

def test_transaction(tmp_path):
    from control_plane.store import StateStore
    from control_plane.project_agent import ProjectAgent
    root=tmp_path/"p";root.mkdir();Workspace(root).write("a.txt","one")
    s=StateStore(tmp_path/"s.db");a=ProjectAgent(root,s)
    tx=Transaction(a).add({"type":"write","path":"a.txt","content":"two"})
    assert tx.prepare()["count"]==1
    assert tx.commit(False)["status"]=="approval_required"
    r=tx.commit(True)
    assert r["ok"] and (root/"a.txt").read_text()=="two"
    s.close()

def test_improvement_gate(tmp_path):
    m=ImprovementManager(tmp_path/"imps.json");x=m.candidate("p","r","l");m.evaluate(x["id"],.9,True)
    assert m.approve(x["id"],True)["ok"]
