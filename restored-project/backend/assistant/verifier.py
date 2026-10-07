from __future__ import annotations
from pathlib import Path
class IndependentVerifier:
    def verify(self,execution,plan,request):
        if execution is None:return {'ok':False,'reason':'no_execution'}
        if execution.get('tool_error'):return {'ok':False,'reason':'tool_error','evidence':execution['tool_error']}
        for artifact in execution.get('artifacts',[]):
            if not Path(artifact).exists():return {'ok':False,'reason':'missing_artifact','artifact':artifact}
        if plan.needs_web and execution.get('sources') is None:return {'ok':False,'reason':'missing_sources'}
        return {'ok':True,'checks':['execution','artifacts','required_evidence']}
