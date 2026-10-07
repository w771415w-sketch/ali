# -*- coding: utf-8 -*-
"""Train media-to-ALI projector with paired media tensors and target ALI hidden states."""
from __future__ import annotations
from pathlib import Path
import json, torch
from multimodal.media import load_media
from multimodal.model import ALIMultimodalFrontEnd

def train_pairs(manifest:str|Path,out_dir:str|Path,hidden_size:int=256,steps:int=200,lr:float=2e-4)->dict:
    rows=[json.loads(x) for x in Path(manifest).read_text(encoding='utf-8').splitlines() if x.strip()]
    if not rows: raise ValueError('empty multimodal manifest')
    model=ALIMultimodalFrontEnd(hidden_size).train(); opt=torch.optim.AdamW(model.parameters(),lr=lr); losses=[]
    for step in range(steps):
        row=rows[step%len(rows)]; media=load_media(row['path']); t=media['tensor'];
        if media['kind']=='image': inp=t.unsqueeze(0)
        elif media['kind']=='audio': inp=t.unsqueeze(0)
        else: inp=t.unsqueeze(0)
        z=model.encode(media['kind'],inp)
        target=torch.tensor(row['target_embedding'],dtype=z.dtype).view(1,1,-1).expand(1,z.size(1),-1)
        loss=torch.nn.functional.mse_loss(z,target); opt.zero_grad(); loss.backward(); opt.step(); losses.append(float(loss.item()))
    p=Path(out_dir); p.mkdir(parents=True,exist_ok=True)
    try:
        from safetensors.torch import save_file; save_file({k:v.detach().cpu() for k,v in model.state_dict().items()},str(p/'multimodal.safetensors'))
    except Exception: torch.save(model.state_dict(),p/'multimodal.pt')
    return {'steps':steps,'loss':losses[-1],'initial_loss':losses[0],'weights':str(p)}
