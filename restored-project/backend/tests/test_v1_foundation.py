from __future__ import annotations
import json, tempfile
from pathlib import Path

def test_job_manager_lifecycle(tmp_path):
    from core.job_manager import JobManager
    import time
    jm=JobManager(tmp_path/'jobs.json')
    job=jm.run('demo',lambda progress:(progress('work',.5),{'ok':True})[-1],'test')
    for _ in range(50):
        if jm.get(job.id).status in {'completed','failed'}: break
        time.sleep(.02)
    assert jm.get(job.id).status=='completed'
    assert jm.get(job.id).result['ok'] is True

def test_orchestrator_plan_has_verification_for_commands():
    from core.orchestrator import Orchestrator
    o=Orchestrator(object())
    p=o.make_plan('run_command python --version')
    assert p.intent=='run_command'
    assert [x.action for x in p.steps]==['run_command','verify_command']
    assert p.steps[0].requires_confirmation

def test_scaling_profiles_grow():
    from training.scaling import PROFILES, estimated_param_count
    counts=[estimated_param_count(PROFILES[k]) for k in ('micro','small','medium','large','xlarge')]
    assert counts==sorted(counts)
    assert counts[-1]>counts[0]

def test_gguf_validator_rejects_non_gguf(tmp_path):
    from tools.gguf import GGUFManager
    p=tmp_path/'bad.gguf'; p.write_bytes(b'NOTGGUF'+b'0'*30)
    r=GGUFManager(tmp_path).validate(p)
    assert r['exists'] and not r['valid']

def test_project_identity():
    cfg=json.loads(Path('PROJECT_VERSION.json').read_text(encoding='utf-8'))
    assert cfg['name']=='ALI AI'
    assert cfg['version'].startswith(('4.5.', '4.6.'))
    assert cfg['previous_project']=='2.5.0'
    assert cfg['previous_release']=='2.0.0'
