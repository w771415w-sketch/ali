# ALI Studio Pro — Design4

Current project source export: ALI Studio Pro Design4 4.6.0.

## Repository layout
- `source-export/part-001.md` … `source-export/part-085.md`: ordered slices of the full source export.
- `SOURCE_MANIFEST.json`: source metadata and part ordering.
- `scripts/reassemble_source.py`: local reassembly helper.
- `scripts/extract_project.py`: restores the 588-file text source tree locally.

Hermes integration is intentionally inactive in this release and remains a later-phase integration.

## Source completeness
The repository currently contains all 85 ordered source-export parts. The final part contains the `588/588` marker, matching the manifest's 588-file declaration. This is a text source export publication, not the original binary ZIP.

## Conversation Intelligence V5
The repository retains the existing V5 conversation layer.

## Conversation Intelligence V6
V6 extends V5 with a structured dialogue-state layer and a deterministic synthetic corpus generator:
- `conversation-intelligence/V6_CONVERSATION_INTELLIGENCE.md`
- `conversation-intelligence/intent_taxonomy_v6.json`
- `conversation-intelligence/dialogue_state_schema_v6.json`
- `conversation-intelligence/response_policy_v6.json`
- `conversation-intelligence/v6_router.py`
- `conversation-intelligence/generate_conversation_corpus_v6.py`
- `conversation-intelligence/corpus_manifest_v6.json`
- `conversation-intelligence/test_v6_router.py`

The V6 generator is configured for a default target of 10,000,000 JSONL records and uses deterministic compositional axes. The repository stores the generator and manifest rather than a multi-gigabyte generated corpus.

V6 covers intent hierarchy, speech acts, references/pronouns, dialogue state, user-goal modeling, ambiguity and risk, multi-intent planning, corrections/recovery, research and evidence, memory boundaries, tool planning, output-format preferences, Arabic/mixed-language handling, and measurable verification.

The source export remains preserved; V6 is published as an additive integration layer and should be wired into the restored runtime through the documented integration boundary before claiming runtime-wide integration.

## Validation
Use:
`python conversation-intelligence/test_v6_router.py`

For a 10M corpus:
`python conversation-intelligence/generate_conversation_corpus_v6.py --count 10000000`

Generated shards should be kept outside Git history unless a dedicated large-dataset storage/release mechanism is used.

## Conversation Intelligence V6.1

V6.1 expands the existing V6 layer with 132 scenario families and 10 dialogue patterns while retaining the deterministic 10,000,000-record generator. Added coverage includes product/UX research, acceptance criteria, collaboration/handoffs, release/change management, cost/capacity planning, observability/incident response, backup/restore, sandbox execution, source provenance, and additional Arabic/noisy/mixed request variants.

The 10M corpus remains generated on demand in deterministic shards; generator + manifest are stored in the repository so Git history does not contain a multi-gigabyte synthetic dataset.

The repository publication is a complete **text source-export** of the provided 588-file export in 85 ordered parts. It is not a claim that the original 220MB binary ZIP, Windows native binaries, or model-weight binaries were reconstructed from that markdown export.
