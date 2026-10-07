# ALI Studio Pro — Design4

Current project source export: ALI Studio Pro Design4 4.6.0.

## Repository layout
- `source-export/part-001.md` … `part-085.md`: ordered slices of the full source export.
- `SOURCE_MANIFEST.json`: source metadata and part ordering.
- `scripts/reassemble_source.py`: local reassembly helper.

Hermes integration is intentionally inactive in this release and remains a later-phase integration.


## Conversation Intelligence V5

تمت إضافة حزمة مستقلة لتوسيع فهم المحادثات والردود:
- `conversation-intelligence/V5_CONVERSATION_INTELLIGENCE.md`
- `conversation-intelligence/intent_taxonomy_v5.json`
- `conversation-intelligence/response_policy_v5.json`
- `conversation-intelligence/v5_router.py`
- `conversation-intelligence/training_patterns_v5.jsonl`
- `conversation-intelligence/verify_v5.py`

الحزمة تغطي المتابعة والإحالات، الغموض، التصحيحات، البحث الحديث، التنفيذ متعدد المراحل، الذاكرة، اللغة المختلطة، الأمن، التحقق، وإدارة شكل الرد. وهي مصممة لتعمل stdlib-only على أجهزة P50.

The repository remains a source-export publication. The Conversation Intelligence V5 pack is added as an explicit integration layer; it is not claimed to be wired into the exported runtime files until a source-tree reconstruction/integration commit is applied.
