from __future__ import annotations
import re
PATTERNS=[
(re.compile(r"ModuleNotFoundError: No module named ['\"]([^'\"]+)",re.I),"missing_dependency"),
(re.compile(r"ImportError: cannot import name ['\"]([^'\"]+)",re.I),"import_api_mismatch"),
(re.compile(r"SyntaxError:",re.I),"syntax_error"),
(re.compile(r"FileNotFoundError:",re.I),"missing_file"),
(re.compile(r"PermissionError:",re.I),"permission_error"),
(re.compile(r"Timeout(Error|Expired):",re.I),"timeout"),
(re.compile(r"CUDA|out of memory",re.I),"memory_or_gpu_capacity"),
(re.compile(r"database is locked|OperationalError:.*database",re.I),"database_contention"),
(re.compile(r"HTTP\s*(401|403)",re.I),"authentication_or_authorization"),
(re.compile(r"HTTP\s*(404|410)",re.I),"resource_not_found")]
def classify_error(text):
    raw=str(text or "")
    for pat,kind in PATTERNS:
        m=pat.search(raw)
        if m:return {"kind":kind,"confidence":.95,"evidence":m.group(0)}
    return {"kind":"unknown","confidence":.20,"evidence":raw[-500:]}
def next_checks(kind):
    return {
"missing_dependency":["inspect environment","check manifest/lockfile","reproduce import"],
"syntax_error":["compile target file","inspect surrounding lines"],
"missing_file":["verify path","inspect project inventory"],
"permission_error":["inspect role","inspect filesystem boundary"],
"timeout":["measure elapsed time","inspect resource limits","bounded retry only"],
"memory_or_gpu_capacity":["inspect RAM/VRAM","reduce batch/context","verify hardware policy"],
"database_contention":["inspect connections","transaction scope","bounded backoff"],
"authentication_or_authorization":["verify credential/token presence without logging secret","inspect permission"],
"resource_not_found":["verify URL/path","check version/source"],
"import_api_mismatch":["inspect installed package version","compare API usage"]
}.get(kind,["collect logs and reproduce"])
