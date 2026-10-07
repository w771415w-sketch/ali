from __future__
from pathlib import Path
DANGEROUS_WORDS=("delete","overwrite","format","drop database","rmdir","del ","rm -rf","publish","deploy","send","رفع","احذف","دمر")
class Policy:
    def __init__(self,workspace): self.workspace=Path(workspace).resolve()
    def path_allowed(self,path):
        try: Path(path).resolve().relative_to(self.workspace); return True
        except ValueError:return False
    def command_allowed(self,command):
        try:
            from security.commands import is_command_safe
            return bool(is_command_safe(str(command)))
        except Exception:
            t=str(command).casefold(); return not any(x in t for x in DANGEROUS_WORDS)
    def needs_approval(self,action): return bool(action.get("external_side_effect") or action.get("irreversible") or action.get("writes_outside_workspace"))
