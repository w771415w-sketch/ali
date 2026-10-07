from __future__
from dataclasses import dataclass
@dataclass
class AcceptanceCheck:
    id:str; description:str; command:str; expected_returncode:int=0; stdout_contains:str|None=None
class AcceptanceRunner:
    def __init__(self,runner): self.runner=runner
    def run(self,checks,approved=True):
        results=[]
        for c in checks:
            r=self.runner.run(c.command,approved=approved); passed=r.returncode==c.expected_returncode and (c.stdout_contains is None or c.stdout_contains in r.stdout)
            results.append({"id":c.id,"description":c.description,"passed":passed,"command":r.command,"returncode":r.returncode,"stdout":r.stdout,"stderr":r.stderr})
        return {"passed":all(x["passed"] for x in results),"results":results}
