#!/usr/bin/env python3
"""
Ablation 1 — Step 1: Paraphrase the 23 few-shot examples in prompt_fewshot_distilled.md.

Keeps all scientific content and JSON outputs identical; rewrites only the
input abstract text with varied phrasing. Saves to prompt_fewshot_paraphrased.md
in the same prompt/ directory.

Usage (from repo root):
    python ablation/ablation1_paraphrase_examples/generate_paraphrased_prompt.py
"""

import os
import re
import sys
from pathlib import Path
from openai import OpenAI

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_PROMPT = REPO_ROOT / "superconductivity" / "prompt" / "prompt_fewshot_distilled.md"
OUTPUT_PROMPT = REPO_ROOT / "superconductivity" / "prompt" / "prompt_fewshot_paraphrased.md"

PARAPHRASE_SYSTEM = (
    "You are a scientific writing assistant. You will be given a physics abstract. "
    "Rewrite it with varied phrasing and sentence structure while preserving all "
    "scientific claims, terminology, entities, and meaning exactly. "
    "Do not add or remove any facts. Return only the rewritten abstract."
)


def load_api_key() -> str:
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if key:
        return key
    # Try superconductivity/utils/openai_key_local.py
    local_key_file = REPO_ROOT / "superconductivity" / "utils" / "openai_key_local.py"
    if local_key_file.exists():
        ns: dict = {}
        exec(local_key_file.read_text(), ns)
        key = ns.get("OPENAI_KEY", "").strip()
        if key:
            return key
    raise RuntimeError(
        "OpenAI API key not found. Set OPENAI_API_KEY or add "
        "superconductivity/utils/openai_key_local.py with OPENAI_KEY='sk-...'"
    )


def paraphrase_abstract(client: OpenAI, abstract: str) -> str:
    resp = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": PARAPHRASE_SYSTEM},
            {"role": "user", "content": abstract},
        ],
    )
    return resp.choices[0].message.content.strip()


def parse_examples(text: str) -> list[dict]:
    """
    Parse the fewshot file into a list of dicts with keys:
        header, input_text, reasoning (optional), output_text
    """
    # Split on example headers  *Example N*
    blocks = re.split(r"(\*Example \d+\*[^\n]*\n)", text)
    examples = []
    i = 1
    while i < len(blocks):
        header = blocks[i].strip()
        body = blocks[i + 1] if i + 1 < len(blocks) else ""
        i += 2

        # Extract Input / Reasoning / Output
        input_match = re.search(r"Input:(.*?)(?=\n\nReasoning:|\n\nOutput:)", body, re.DOTALL)
        reasoning_match = re.search(r"Reasoning:(.*?)(?=\n\nOutput:)", body, re.DOTALL)
        output_match = re.search(r"Output:(.*?)$", body, re.DOTALL)

        if not input_match or not output_match:
            continue

        examples.append({
            "header": header,
            "input_text": input_match.group(1).strip(),
            "reasoning": reasoning_match.group(1).strip() if reasoning_match else None,
            "output_text": output_match.group(1).strip(),
        })
    return examples


def rebuild_example(ex: dict, paraphrased_input: str) -> str:
    lines = [ex["header"], ""]
    lines.append(f"Input: {paraphrased_input}")
    lines.append("")
    if ex["reasoning"]:
        lines.append(f"Reasoning: {ex['reasoning']}")
        lines.append("")
    lines.append(f"Output: {ex['output_text']}")
    lines.append("")
    return "\n".join(lines)


def main():
    client = OpenAI(api_key=load_api_key())

    text = SOURCE_PROMPT.read_text(encoding="utf-8")
    examples = parse_examples(text)
    print(f"Parsed {len(examples)} examples from {SOURCE_PROMPT.name}")

    paraphrased_blocks = []
    for i, ex in enumerate(examples, 1):
        print(f"  Paraphrasing example {i}/{len(examples)}...", end=" ", flush=True)
        try:
            para = paraphrase_abstract(client, ex["input_text"])
            print("done")
        except Exception as e:
            print(f"ERROR: {e} — using original")
            para = ex["input_text"]
        paraphrased_blocks.append(rebuild_example(ex, para))

    output_text = "\n".join(paraphrased_blocks)
    OUTPUT_PROMPT.write_text(output_text, encoding="utf-8")
    print(f"\nSaved paraphrased prompt to {OUTPUT_PROMPT}")


if __name__ == "__main__":
    main()
