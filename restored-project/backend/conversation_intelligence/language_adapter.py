from __future__ import annotations
import json,re,unicodedata
from pathlib import Path
class ArabicLanguageAdapter:
    def __init__(self,catalog_path=None,profile="ar-SA"):
        path=Path(catalog_path or Path(__file__).resolve().parents[1]/"config"/"language_profiles.json"); self.catalog=json.loads(path.read_text(encoding="utf-8"))
        self.profile=profile if profile in self.catalog.get("profiles",{}) else self.catalog.get("default_profile","ar-SA")
        self.correctors={"البرانامج":"البرنامج","للبرانامج":"للبرنامج","البر نامج":"البرنامج","االبرنامج":"البرنامج","الختبار":"الاختبار","الختبارات":"الاختبارات","المشروعه":"المشروع","مشكله":"مشكلة","استيطع":"أستطيع","تسطيع":"تستطيع","قمتو":"قمت"}
    @staticmethod
    def normalize(text):
        text=unicodedata.normalize("NFKC",str(text or "")).replace("ـ","")
        text=re.sub(r"[ؐ-ًؚ-ٰٟۖ-ۭ]","",text)
        return re.sub(r"s+"," ",text).strip()
    def correct_spelling(self,text):
        out=self.normalize(text);changes=[]
        for bad,good in self.correctors.items():
            if bad in out: out=out.replace(bad,good);changes.append({"from":bad,"to":good})
        return {"text":out,"changes":changes}
    def detect(self,text):
        clean=self.normalize(text);scores={k:0 for k in self.catalog.get("profiles",{})}
        for pid,p in self.catalog.get("profiles",{}).items():
            scores[pid]=sum(1 for marker in p.get("markers",[]) if self.normalize(marker) in clean)
        if not re.search(r"[؀-ۿ]",clean): return {"profile":"unknown","confidence":0.0,"scores":scores}
        best=max(scores,key=scores.get)
        if scores[best]==0:return {"profile":"ar-MSA","confidence":0.50,"scores":scores}
        total=sum(scores.values()) or 1
        return {"profile":best,"confidence":round(scores[best]/total,3),"scores":scores}
    def adapt(self,text,preferred_profile=None):
        corrected=self.correct_spelling(text); detected=self.detect(corrected["text"]); profile=preferred_profile or self.profile
        if profile not in self.catalog.get("profiles",{}): profile=self.catalog.get("default_profile","ar-SA")
        return {"input":text,"normalized":corrected["text"],"corrections":corrected["changes"],"detected":detected,"response_profile":profile}
