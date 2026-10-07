# -*- coding: utf-8 -*-
"""Small trainable multimodal front-end for ALI.

It learns to map image/audio/video representations into the same hidden space as
ALI token embeddings. The language model can then condition on those prefix states.
"""
from __future__ import annotations
import torch
from torch import nn

class TinyVisionEncoder(nn.Module):
    def __init__(self,out_dim=256):
        super().__init__(); self.net=nn.Sequential(nn.Conv2d(3,32,5,2,2),nn.GELU(),nn.Conv2d(32,64,5,2,2),nn.GELU(),nn.Conv2d(64,128,3,2,1),nn.GELU(),nn.AdaptiveAvgPool2d((1,1))); self.proj=nn.Linear(128,out_dim)
    def forward(self,x):return self.proj(self.net(x).flatten(1))

class TinyAudioEncoder(nn.Module):
    def __init__(self,out_dim=256):
        super().__init__(); self.net=nn.Sequential(nn.Conv2d(1,32,5,2,2),nn.GELU(),nn.Conv2d(32,64,5,2,2),nn.GELU(),nn.Conv2d(64,128,3,2,1),nn.GELU(),nn.AdaptiveAvgPool2d((1,1))); self.proj=nn.Linear(128,out_dim)
    def forward(self,x):
        if x.dim()==3:x=x.unsqueeze(1)
        return self.proj(self.net(x).flatten(1))

class TinyVideoEncoder(nn.Module):
    def __init__(self,out_dim=256):
        super().__init__(); self.vision=TinyVisionEncoder(out_dim)
    def forward(self,x):
        b,t,c,h,w=x.shape; z=self.vision(x.reshape(b*t,c,h,w)).view(b,t,-1); return z.mean(1)

class MediaProjector(nn.Module):
    def __init__(self,media_dim:int,hidden_size:int,prefix_tokens:int=4):
        super().__init__(); self.prefix_tokens=prefix_tokens; self.net=nn.Sequential(nn.Linear(media_dim,hidden_size*2),nn.GELU(),nn.Linear(hidden_size*2,hidden_size*prefix_tokens))
    def forward(self,x):return self.net(x).view(x.size(0),self.prefix_tokens,-1)

class ALIMultimodalFrontEnd(nn.Module):
    def __init__(self,hidden_size:int=256):
        super().__init__(); self.vision=TinyVisionEncoder(hidden_size); self.audio=TinyAudioEncoder(hidden_size); self.video=TinyVideoEncoder(hidden_size); self.projector=MediaProjector(hidden_size,hidden_size)
    def encode(self,kind,tensor):
        if kind=='image': z=self.vision(tensor)
        elif kind=='audio': z=self.audio(tensor)
        elif kind=='video': z=self.video(tensor)
        else: raise ValueError(kind)
        return self.projector(z)
