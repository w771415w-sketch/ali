# -*- coding: utf-8 -*-
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from runtime.doctor import run_doctor
print(json.dumps(run_doctor(ROOT),ensure_ascii=False,indent=2))
