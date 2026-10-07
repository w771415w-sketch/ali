#!/usr/bin/env python
"""Seed local conversation memory from reviewed seed conversations.
This does not alter model weights; it provides immediate, provenance-aware recall.
"""
from __future__ import annotations
from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from memory.conversations import ConversationMemory

def main():
    db=ConversationMemory(ROOT/'runtime_conversations.sqlite3')
    src=ROOT/'data/seed/conversations_curriculum.jsonl' if (ROOT/'data/seed/conversations_curriculum.jsonl').exists() else ROOT/'data/seed/conversations.jsonl'; n=0
    with src.open(encoding='utf-8') as f:
        for line in f:
            try:o=json.loads(line); msgs=o.get('messages',[])
            except Exception: continue
            user=next((m.get('content','') for m in msgs if m.get('role')=='user'),'')
            assistant=next((m.get('content','') for m in msgs if m.get('role')=='assistant'),'')
            if user and assistant:
                meta=o.get('metadata') or {}; db.put(user,assistant,source=meta.get('source','reviewed-seed'),model_version=meta.get('version','curriculum-seed'),quality=1.0); n+=1
    print(json.dumps({'stored_or_updated':n,'db':str(ROOT/'runtime_conversations.sqlite3')},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
