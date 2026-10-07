# -*- coding: utf-8 -*-
from pathlib import Path
import sys,argparse,json,torch
ROOT=Path(__file__).resolve().parent.parent; sys.path.insert(0,str(ROOT))
from model.ali_lm import AliConfig,ALIForCausalLM,save_hf_checkpoint
from tokenizer.spm import AliTokenizer
ap=argparse.ArgumentParser(); ap.add_argument('checkpoint'); ap.add_argument('out'); ap.add_argument('--tokenizer-dir',default='weights/tokenizer'); args=ap.parse_args()
b=ROOT/args.checkpoint if not Path(args.checkpoint).is_absolute() else Path(args.checkpoint); blob=torch.load(b/'checkpoint.pt',map_location='cpu',weights_only=False); m=ALIForCausalLM(AliConfig.from_dict(blob['config'])); m.load_state_dict(blob['model']); out=save_hf_checkpoint(m,ROOT/args.tokenizer_dir,ROOT/args.out,{'source_checkpoint':str(b)}); print(json.dumps({'hf_dir':str(out)},ensure_ascii=False,indent=2))
