#!/usr/bin/env python
from __future__ import annotations
import argparse,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
def main(argv=None):
 p=argparse.ArgumentParser(prog='ali'); sub=p.add_subparsers(dest='cmd',required=True)
 sub.add_parser('doctor'); h=sub.add_parser('harvest'); h.add_argument('path')
 a=p.parse_args(argv)
 if a.cmd=='doctor':
  from runtime.hardware import detect; print(detect().__dict__)
  return 0
 if a.cmd=='harvest':
  from data_engine.harvester import Harvester; print(Harvester(ROOT/'artifacts/harvest.sqlite3').scan(a.path)); return 0
 return 0
if __name__=='__main__': raise SystemExit(main())
