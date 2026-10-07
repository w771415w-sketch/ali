# -*- coding: utf-8 -*-
"""First-party provider: ALI's own trained model only."""
from inference.engine import LocalInference
class LocalALIProvider:
    name='local-ali'
    def __init__(self,model_dir,tokenizer_dir=None,device='cpu'):self.engine=LocalInference(model_dir,tokenizer_dir,device)
    def stream(self,messages,**kwargs):return self.engine.stream(messages,**kwargs)
    def complete(self,messages,**kwargs):return self.engine.complete(messages,**kwargs)
