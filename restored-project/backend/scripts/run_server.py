# -*- coding: utf-8 -*-
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from api.server import serve
from core.runtime import ALIRuntime
serve(ALIRuntime(ROOT,ROOT/'runtime.sqlite3',allow_internet=False),project_dir=ROOT)
