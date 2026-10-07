# -*- coding: utf-8 -*-
from pathlib import Path
import argparse,sys,json
ROOT=Path(__file__).resolve().parent.parent; sys.path.insert(0,str(ROOT))
from tools.gguf import GGUFManager
ap=argparse.ArgumentParser(); ap.add_argument('hf_dir'); ap.add_argument('outfile'); ap.add_argument('--llama-dir',default='vendor/llama.cpp'); ap.add_argument('--outtype',default='f16'); ap.add_argument('--quantize',default=''); ap.add_argument('--quantized-out',default='')
args=ap.parse_args(); m=GGUFManager(args.llama_dir); r=m.convert(args.hf_dir,args.outfile,args.outtype); print(json.dumps(r,ensure_ascii=False,indent=2));
if args.quantize: print(json.dumps(m.quantize(args.outfile,args.quantized_out or str(Path(args.outfile).with_name(Path(args.outfile).stem+'-'+args.quantize+'.gguf')),args.quantize),ensure_ascii=False,indent=2))
