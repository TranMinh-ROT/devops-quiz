#!/usr/bin/env python3
"""Step 1: Read all DOCX files and split into raw question blocks."""
import os, re, json
from docx import Document

SOURCE_DIR = "source-documents"
OUTPUT = "temp/raw-question-blocks.json"

def get_paragraphs(fpath):
    doc = Document(fpath)
    return [(i, p.text) for i, p in enumerate(doc.paragraphs)]

def split_into_blocks(paragraphs, fname):
    """Split paragraphs into question blocks using 'Question N' headers."""
    blocks = []
    current = None
    for idx, text in paragraphs:
        stripped = text.strip()
        if not stripped:
            continue
        # Match "Question N" at start - handles "Question 1:", "Question 1 /", etc.
        m = re.match(r'^Question\s+(\d+)', stripped)
        if m:
            if current is not None:
                blocks.append(current)
            current = {
                "sourceFile": fname,
                "sourceQuestionNumber": int(m.group(1)),
                "headerLine": stripped,
                "paragraphIndex": idx,
                "lines": [stripped]
            }
        elif current is not None:
            current["lines"].append(stripped)
    if current is not None:
        blocks.append(current)
    return blocks

def find_duplicates(blocks):
    """Find duplicate question numbers within a file's blocks."""
    seen = {}
    dupes = []
    for b in blocks:
        qn = b["sourceQuestionNumber"]
        if qn in seen:
            dupes.append(qn)
        seen[qn] = seen.get(qn, 0) + 1
    return dupes

# Main
files = sorted([f for f in os.listdir(SOURCE_DIR) if f.endswith('.docx')])
print(f"Found {len(files)} DOCX files\n")

all_blocks = []
summary = []

for fname in files:
    fpath = os.path.join(SOURCE_DIR, fname)
    paragraphs = get_paragraphs(fpath)
    blocks = split_into_blocks(paragraphs, fname)
    dupes = find_duplicates(blocks)

    print(f"  {fname}")
    print(f"    Paragraphs: {len(paragraphs)}")
    print(f"    Question blocks: {len(blocks)}")
    if dupes:
        print(f"    DUPLICATE question numbers: {dupes}")
    else:
        print(f"    No duplicate question numbers")

    summary.append({
        "file": fname,
        "blockCount": len(blocks),
        "duplicates": dupes
    })
    all_blocks.extend(blocks)

total = len(all_blocks)
print(f"\nTotal raw question blocks: {total}")

# Check for the known duplicate Q40 in file 5 - deduplicate exact copies
deduped = []
seen_keys = set()
removed = 0
for b in all_blocks:
    key = (b["sourceFile"], b["sourceQuestionNumber"], b["lines"][1] if len(b["lines"]) > 1 else "")
    if key in seen_keys:
        removed += 1
        print(f"  Removing exact duplicate: {b['sourceFile']} Q{b['sourceQuestionNumber']}")
        continue
    seen_keys.add(key)
    deduped.append(b)

if removed:
    print(f"  Removed {removed} exact duplicate(s)")
    print(f"  Deduplicated total: {len(deduped)}")

# Save
with open(OUTPUT, 'w', encoding='utf-8') as f:
    json.dump({
        "summary": summary,
        "totalBlocks": len(deduped),
        "blocks": deduped
    }, f, ensure_ascii=False, indent=2)

print(f"\nSaved to {OUTPUT}")
print(f"Done.")
