import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from config.device_profiles import recommend_for_hardware
from runtime.hardware import HardwareInfo
from runtime.device_policy import choose_policy
from security.commands import is_command_safe
from security.paths import safe_project_path
from security.permissions import PermissionManager,PermMode
from core.state_machine import AgentState
from core.verification import predicate
from agent.executor import AgentExecutor,Action
from conversation_intelligence.v6_router import frame,update_state
def p50(): return HardwareInfo(device_name="Lenovo ThinkPad P50",model="20EQS2L900",cpu_threads=8,physical_cores=4,ram_gb=32,ram_available_gb=21.32,gpu_name="NVIDIA Quadro M1000M",vram_gb=2,battery_percent=80,power_plugged=True,temperature_c=41.05)
def test_profile_and_policy():
 h=p50(); p=recommend_for_hardware(h); pol=choose_policy(h); assert p["id"].startswith("thinkpad-p50") and p["training"]["device"]=="cpu"; assert pol["training_enabled"] and pol["max_cpu_threads"]==6 and pol["max_concurrent_jobs"]==1
def test_battery_guard():
 h=p50(); h.battery_percent=38; h.power_plugged=False; assert not choose_policy(h)["training_enabled"]
def test_command_and_path_guards(tmp_path):
 assert is_command_safe("python -c 'print(1)'"); assert not is_command_safe("powershell -enc AAA"); assert safe_project_path(tmp_path,"src/main.py").parent==tmp_path/"src"
 try: safe_project_path(tmp_path,"../../secret.txt"); raise AssertionError("workspace escape allowed")
 except PermissionError: pass
def test_permission_hard_ceiling():
 pm=PermissionManager(); pm.grant("run_command"); pm.set_mode(PermMode.READ_ONLY.value); d=pm.check("run_command","default"); assert not d.allowed and not d.needs_ask
 pm.set_mode(PermMode.DEFAULT.value); assert pm.check("run_command","default").allowed is False and pm.check("read_file","read-only").allowed
def test_agent_requires_verification():
 state=AgentState(active_goal="demo"); ex=AgentExecutor(state); result=ex.execute(Action("write",lambda:"ok",lambda x:predicate("result",lambda:x=="ok",x))); assert result["ok"] and state.stage=="verify"
def test_conversation_resume_and_confirmation():
 r=frame("احذف الملف السابق",{"active_goal":"project"}); assert r.confirmation_required
 st=update_state({"active_goal":"project","pending_confirmation":"delete"},frame("نعم")); assert st["stage"]=="execute"
