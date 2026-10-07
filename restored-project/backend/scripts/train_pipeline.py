#!/usr/bin/env python
"""CLI for the same progressive training pipeline used by the desktop UI."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.hardware import detect, training_profile
from training.pipeline import PipelineConfig, TrainingPipeline


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="ali-train", description="ALI AI 2.0 progressive training")
    p.add_argument("--stage", choices=("base", "sft", "lora"), default="base")
    p.add_argument("--scale", default="micro")
    p.add_argument("--train", required=True)
    p.add_argument("--validation", default="")
    p.add_argument("--base", default="")
    p.add_argument("--resume", default="")
    p.add_argument("--steps", type=int, default=0)
    p.add_argument("--epochs", type=int, default=1)
    p.add_argument("--seq", type=int, default=256)
    p.add_argument("--batch", type=int, default=1)
    p.add_argument("--accum", type=int, default=16)
    p.add_argument("--lr", type=float, default=3e-4)
    p.add_argument("--device", default="auto", help="auto, cpu, cuda, cuda:N")
    p.add_argument("--vocab-size", type=int, default=4096)
    p.add_argument("--lora-rank", type=int, default=8)
    p.add_argument("--lora-alpha", type=float, default=16.0)
    p.add_argument("--lora-dropout", type=float, default=.05)
    p.add_argument("--distributed-backend", default="auto")
    p.add_argument("--world-size", type=int, default=int(os.environ.get("WORLD_SIZE", "1")))
    args = p.parse_args(argv)

    device = args.device
    if device == "auto":
        hw = detect()
        device = training_profile(hw).get("device", "cpu")

    cfg = PipelineConfig(
        stage=args.stage, scale=args.scale,
        train_path=str(Path(args.train).resolve()),
        validation_path=str(Path(args.validation).resolve()) if args.validation else "",
        base_checkpoint=str(Path(args.base).resolve()) if args.base else "",
        resume_checkpoint=str(Path(args.resume).resolve()) if args.resume else "",
        max_steps=max(0, args.steps), epochs=max(1, args.epochs),
        max_seq_len=max(32, args.seq), batch_size=max(1, args.batch),
        grad_accum=max(1, args.accum), learning_rate=args.lr,
        device=device, tokenizer_vocab_size=max(128, args.vocab_size),
        lora_rank=max(1, args.lora_rank), lora_alpha=args.lora_alpha,
        lora_dropout=max(0.0, min(.99, args.lora_dropout)),
        distributed_backend=args.distributed_backend,
        world_size=max(1, args.world_size),
    )

    pipe = TrainingPipeline(ROOT, detect())
    result = pipe.run(cfg, progress=lambda ev: print(json.dumps(ev, ensure_ascii=False), flush=True))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
