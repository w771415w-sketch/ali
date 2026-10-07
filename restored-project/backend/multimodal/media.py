# -*- coding: utf-8 -*-
"""Offline media decoding: image, WAV audio and video frames."""
from __future__ import annotations
from pathlib import Path
import math, subprocess, wave
import torch

def _norm_img(t):return t.float()/255.0 if t.max()>1.5 else t.float()
def load_image(path:str|Path,size:int=128)->torch.Tensor:
    from PIL import Image
    img=Image.open(path).convert('RGB').resize((size,size))
    return torch.from_numpy(__import__('numpy').asarray(img)).permute(2,0,1).float()/255.0

def load_wav(path:str|Path,n_mels:int=64,max_seconds:int=20)->torch.Tensor:
    import numpy as np
    with wave.open(str(path),'rb') as wf:
        ch=wf.getnchannels(); sr=wf.getframerate(); frames=min(wf.getnframes(),sr*max_seconds); raw=wf.readframes(frames); width=wf.getsampwidth()
    dtype={1:np.int8,2:np.int16,4:np.int32}.get(width,np.int16); a=np.frombuffer(raw,dtype=dtype).astype(np.float32)
    if ch>1:a=a.reshape(-1,ch).mean(1)
    scale=float(2**(8*width-1)); a=torch.from_numpy(a/scale)
    if a.numel()<512:a=torch.nn.functional.pad(a,(0,512-a.numel()))
    win=400; hop=160; spec=torch.stft(a,n_fft=512,hop_length=hop,win_length=win,return_complex=True).abs(); spec=spec[:n_mels]; return torch.log1p(spec).unsqueeze(0)

def extract_video_frames(path:str|Path,size:int=128,max_frames:int=8)->torch.Tensor:
    """Uses local ffmpeg if available; no network/download occurs."""
    import tempfile, shutil
    if not shutil.which('ffmpeg'): raise FileNotFoundError('ffmpeg is required for video media support')
    with tempfile.TemporaryDirectory(prefix='ali-video-') as td:
        pattern=str(Path(td)/'f-%03d.jpg'); subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(path),'-vf',f'fps=1,scale={size}:{size}:force_original_aspect_ratio=decrease','-frames:v',str(max_frames),pattern],check=True,timeout=180)
        from PIL import Image
        frames=[]
        for p in sorted(Path(td).glob('f-*.jpg'))[:max_frames]:frames.append(load_image(p,size))
        if not frames: raise ValueError('no frames decoded from video')
        return torch.stack(frames)

def load_media(path:str|Path,size:int=128):
    p=Path(path); ext=p.suffix.lower()
    if ext in {'.png','.jpg','.jpeg','.webp','.bmp'}: return {'kind':'image','tensor':load_image(p,size)}
    if ext in {'.wav'}: return {'kind':'audio','tensor':load_wav(p)}
    if ext in {'.mp4','.mov','.mkv','.avi','.webm'}: return {'kind':'video','tensor':extract_video_frames(p,size)}
    raise ValueError(f'unsupported media type: {ext}')
