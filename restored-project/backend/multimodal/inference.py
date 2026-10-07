# -*- coding: utf-8 -*-
from __future__ import annotations
from pathlib import Path
import torch
from multimodal.media import load_media
from multimodal.model import ALIMultimodalFrontEnd

class MultimodalAdapter:
    def __init__(self,weights_dir:str|Path,hidden_size:int=256,device='cpu'):
        self.device=torch.device(device); self.model=ALIMultimodalFrontEnd(hidden_size).to(self.device).eval(); p=Path(weights_dir)
        state=p/'multimodal.safetensors'
        if state.exists():
            from safetensors.torch import load_file; self.model.load_state_dict(load_file(str(state),device='cpu'),strict=False)
        elif (p/'multimodal.pt').exists(): self.model.load_state_dict(torch.load(p/'multimodal.pt',map_location='cpu',weights_only=False),strict=False)
    @torch.no_grad()
    def prefix_from_file(self,path):
        media=load_media(path); return media['kind'],self.model.encode(media['kind'],media['tensor'].unsqueeze(0).to(self.device))
