from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
PART_DIR = ROOT / "source-export"
CI = ROOT / "conversation-intelligence"


def main():
    parts = sorted(PART_DIR.glob("part-*.md"))
    assert len(parts) == 85, f"expected 85 source parts, found {len(parts)}"
    expected = [PART_DIR / f"part-{i:03d}.md" for i in range(1, 86)]
    assert parts == expected, "source part sequence has gaps or unexpected files"
    all_text = "".join(p.read_text(encoding="utf-8") for p in parts)
    matches = re.findall(r"^###\s+`(\d+)/(\d+)`\s+`([^\n]+?)`\s*$", all_text, re.M)
    assert len(matches) == 588, f"expected 588 file markers, found {len(matches)}"
    assert int(matches[0][1]) == 588 and int(matches[-1][0]) == 588
    manifest = json.loads((ROOT / "SOURCE_MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["parts"] == 85
    assert manifest["source_lines"] == 84920
    assert manifest["source_size_bytes"] == 10318019
    required = ["V6_CONVERSATION_INTELLIGENCE.md","intent_taxonomy_v6.json","dialogue_state_schema_v6.json","response_policy_v6.json","corpus_manifest_v6.json","v6_router.py","generate_conversation_corpus_v6.py","test_v6_router.py"]
    assert all((CI / x).exists() for x in required)
    corpus = json.loads((CI / "corpus_manifest_v6.json").read_text(encoding="utf-8"))
    assert corpus["minimum_target_records"] >= 10_000_000
    assert corpus["documented_combinatorial_space"] > corpus["minimum_target_records"]
    print("V6 repository verification passed")
    print(f"source_parts={len(parts)} source_file_markers={len(matches)}")
    print(f"minimum_target_records={corpus['minimum_target_records']}")
    print(f"documented_combinatorial_space={corpus['documented_combinatorial_space']}")


if __name__ == "__main__":
    main()
