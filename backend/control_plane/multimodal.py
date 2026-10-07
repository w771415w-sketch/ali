from __future__ import annotations
from pathlib import Path
import importlib.util
class MultimodalCapabilities:
    def inspect(self):
        modules=["PIL","pypdf","docx","openpyxl","python_pptx","speech_recognition","transformers"]
        return {m:importlib.util.find_spec(m) is not None for m in modules}
    def inspect_file(self,path):
        p=Path(path); suffix=p.suffix.casefold()
        families={".pdf":"document_pdf",".docx":"document_docx",".xlsx":"document_xlsx",".pptx":"document_pptx",".png":"image",".jpg":"image",".jpeg":"image",".webp":"image",".wav":"audio",".mp3":"audio"}
        kind=families.get(suffix,"unknown")
        return {"path":str(p),"kind":kind,"available":self.inspect()}
    def require(self,path,feature):
        caps=self.inspect()
        needed={"vision":"PIL","ocr":"transformers","pdf":"pypdf","docx":"docx","xlsx":"openpyxl","pptx":"python_pptx","speech":"speech_recognition"}.get(feature)
        return {"ok":bool(needed and caps.get(needed)),"feature":feature,"dependency":needed}
