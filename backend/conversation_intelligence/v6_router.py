# -*- coding: utf-8 -*-
"""Deterministic request framing and dialogue-state updates for ALI."""
from __future__ import annotations
from dataclasses import dataclass,asdict
import re,unicodedata
AR=re.compile(r"[\u0600-\u06ff]"); EN=re.compile(r"[A-Za-z]"); DIAC=re.compile(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]")
def normalize(s): return re.sub(r"\s+"," ",DIAC.sub("",unicodedata.normalize("NFKC",str(s or "")).replace("ـ","")).casefold()).strip()
def lang(s):
 a,e=len(AR.findall(str(s))),len(EN.findall(str(s))); return "mixed" if a and e else "ar" if a else "en" if e else "unknown"
def hit(s,words):
 t=normalize(s); return any(normalize(w) in t for w in words)
@dataclass(frozen=True)
class Frame:
 intent:str; mode:str; speech_act:str; language:str; domain:str; user_goal:str; confidence:float
 continuation:bool; confirmation:bool; correction:bool; cancellation:bool; multi_intent:bool
 freshness_required:bool; risk_level:str; ambiguity_level:str; requested_depth:str; output_format:str|None
 references:list[str]; constraints:list[str]; evidence_required:bool; confirmation_required:bool; required_tools:list[str]
 def to_dict(self): return asdict(self)
EXEC=("نفذ","شغل","طبق","أنشئ","انشئ","عدل","عدّل","احذف","ارفع","run","execute","create","edit","delete","deploy")
CONT=("كمل","اكمل","أكمل","تابع","واصل","من حيث توقفنا","continue")
CONF=("نعم","أيوه","ايوه","تمام","موافق","نفذها","ابدأ","yes","go ahead")
CANCEL=("توقف","أوقف","إلغاء","الغ","ألغ","cancel","stop")
CORRECT=("هذا خطأ","غير صحيح","صحح","incorrect","wrong")
FRESH=("الآن","الان","اليوم","الأحدث","آخر","حديث","latest","current","today","now","search")
RISK=("احذف","دمر","overwrite","delete","publish","انشر","ارفع","deploy","أرسل","إرسال")
def _domain(s):
 t=normalize(s); groups={"software":("python","javascript","react","electron","backend","frontend","كود","برمجة"),"ai":("llm","rag","lora","qlora","gguf","نموذج","تدريب","ذكاء اصطناعي"),"data":("sql","sqlite","postgres","csv","json","بيانات","قاعدة بيانات"),"git":("git","github","commit","branch","مستودع"),"security":("security","token","secret","permission","أمن","صلاحيات"),"windows":("windows","powershell","cmd","ويندوز"),"web":("http","https","browser","ويب")}
 score={k:sum(w in t for w in ws) for k,ws in groups.items()}; k=max(score,key=score.get); return k if score[k] else "general"
def frame(text,state=None):
 s=str(text or ""); t=normalize(s); cont=hit(s,CONT); conf=hit(s,CONF); corr=hit(s,CORRECT); cancel=hit(s,CANCEL); fresh=hit(s,FRESH)
 if cancel: intent,mode,sa,c="cancellation","cancel","cancellation",.99
 elif corr: intent,mode,sa,c="correction","recover","correction",.99
 elif conf: intent,mode,sa,c="confirmation","confirm","confirmation",.95
 elif cont: intent,mode,sa,c="follow_up","continue","continuation",.99
 elif hit(s,RISK) or hit(s,EXEC): intent,mode,sa,c="execution","execute","command",.92
 elif fresh: intent,mode,sa,c="research","research","question",.95
 elif "؟" in s or "?" in s: intent,mode,sa,c="question","answer","question",.85
 else: intent,mode,sa,c="request","answer","request",.70
 refs=[x for x in ("هذا","هذه","ذلك","السابق","السابقة","الأول","الثاني","it","that") if normalize(x) in t]
 multi=hit(s,("ثم","وبعدها","وأيضاً","also","and then")); risk="external_side_effect" if hit(s,("انشر","ارفع","deploy","publish")) else "high" if hit(s,RISK) else "none"
 ambiguity="dangerous" if risk=="external_side_effect" and not (state or {}).get("active_goal") else "high" if refs and not (state or {}).get("active_goal") else "medium" if len(t)<8 else "none"
 fmt="json" if "json" in t else "table" if "جدول" in t or "table" in t else "code" if "كود" in t or "code" in t else None
 domain=_domain(s); tools=[]
 if fresh: tools.append("web")
 if domain in {"software","ai","data","git","windows"} and (mode=="execute" or hit(s,("مشروع","ملف","اختبر","تشغيل"))): tools.append("project")
 if domain in {"software","data","ai"} and intent in {"question","request"}: tools.append("files_or_rag")
 return Frame(intent,mode,sa,lang(s),domain,"execute" if mode=="execute" else "continue" if cont else "recover" if corr else "understand",c,cont,conf,corr,cancel,multi,fresh,risk,ambiguity,"deep" if hit(s,("بالتفصيل","شامل","deep","detailed")) else "brief" if hit(s,("باختصار","مختصر","brief")) else "normal",fmt,refs,[],fresh,risk in {"high","external_side_effect"},sorted(set(tools)))
def update_state(previous,request):
 st=dict(previous or {}); st.setdefault("constraints",[]); st.setdefault("decisions",[]); st.setdefault("checkpoints",[]); st.setdefault("missing_requirements",[])
 if request.cancellation: st.update(stage="cancelled",pending_confirmation=None,pending_tool_action=None); return st
 if request.correction: st["stage"]="recover"
 elif request.confirmation and st.get("pending_confirmation"): st.update(stage="execute",pending_tool_action=st.get("pending_confirmation"),pending_confirmation=None)
 elif request.continuation: st["stage"]="execute" if st.get("active_goal") else "clarify"
 else: st.update(active_goal=request.intent,active_domain=request.domain,stage="clarify" if request.ambiguity_level in {"high","dangerous"} else "plan" if request.multi_intent else "discover")
 if request.confirmation_required and not request.confirmation: st["pending_confirmation"]=request.intent
 return st
