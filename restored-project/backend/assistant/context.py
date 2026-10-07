from __future__ import annotations
from dataclasses import dataclass
@dataclass
class ContextBudget: max_tokens:int; reserved_system:int=800; reserved_user:int=400; reserved_output:int=512
class ContextManager:
    def __init__(self,*,tokenizer=None,memory=None,rag=None,conversations=None): self.tokenizer=tokenizer; self.memory=memory; self.rag=rag; self.conversations=conversations
    def build(self,request):
        recent=self.conversations.recent(request.conversation_id) if self.conversations else []; memories=self.memory.relevant(request.text,limit=8) if self.memory else []; sources=self.rag.search(request.text,limit=8) if self.rag else []
        return {'budget':ContextBudget(4096).__dict__,'recent':recent,'memories':memories,'sources':sources,'attachments':request.attachments,'project_id':request.project_id}
