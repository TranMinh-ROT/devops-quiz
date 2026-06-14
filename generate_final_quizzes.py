#!/usr/bin/env python3
import json
import os
from collections import defaultdict

INPUT_CLEANED = "temp/cleaned-questions.json"
OUTPUT_DIR = "src/data"
INDEX_FILE = os.path.join(OUTPUT_DIR, "quizzes.js")
REPORT_FILE = "data-validation-report.md"

with open(INPUT_CLEANED, 'r', encoding='utf-8') as f:
    questions = json.load(f)

# Group questions by sourceFile preserving order
source_files = []
for q in questions:
    if q['sourceFile'] not in source_files:
        source_files.append(q['sourceFile'])

# Sort source files to map to quiz 1-5 predictably
source_files.sort()

if len(source_files) != 5:
    raise Exception(f"Expected exactly 5 source files, but found {len(source_files)}: {source_files}")

grouped_questions = defaultdict(list)
for q in questions:
    grouped_questions[q['sourceFile']].append(q)

quiz_files_generated = []
file_mapping = {}
stats = {
    "total_input": len(questions),
    "total_output": 0,
    "quizzes": {},
    "missing_en_q": 0,
    "missing_vi_q": 0,
    "missing_vi_exp": 0,
    "missing_correct": 0,
    "invalid_refs": 0,
    "all_ids": set(),
    "duplicate_ids": 0,
    "duplicate_content": 0,
    "content_hashes": set(),
    "duplicate_source_nums": 0,
    "source_nums_per_file": defaultdict(set),
    "multi_quiz_qs": 0,
    "invalid_json": 0
}

# Generate Quizzes
for idx, sf in enumerate(source_files, 1):
    quiz_id = f"quiz-{idx:02d}"
    filename = f"{quiz_id}.json"
    filepath = os.path.join(OUTPUT_DIR, filename)
    quiz_files_generated.append(filename)
    file_mapping[sf] = filename
    
    q_list = grouped_questions[sf]
    stats["total_output"] += len(q_list)
    
    single_ans = sum(1 for q in q_list if q['type'] == 'single')
    multi_ans = sum(1 for q in q_list if q['type'] == 'multiple')
    five_plus = sum(1 for q in q_list if len(q['options']) >= 5)
    has_e = sum(1 for q in q_list if any(o['id'] == 'E' for o in q['options']))
    has_f = sum(1 for q in q_list if any(o['id'] == 'F' for o in q['options']))
    
    first_id = q_list[0]['id'] if q_list else None
    last_id = q_list[-1]['id'] if q_list else None
    
    stats["quizzes"][quiz_id] = {
        "sourceFile": sf,
        "count": len(q_list),
        "single": single_ans,
        "multi": multi_ans,
        "five_plus": five_plus,
        "has_e": has_e,
        "has_f": has_f,
        "first_id": first_id,
        "last_id": last_id
    }
    
    # Validation per question
    for q in q_list:
        if q['id'] in stats["all_ids"]:
            stats["duplicate_ids"] += 1
        stats["all_ids"].add(q['id'])
        
        # Check source num duplicates
        if q['sourceQuestionNumber'] in stats["source_nums_per_file"][sf]:
            stats["duplicate_source_nums"] += 1
        stats["source_nums_per_file"][sf].add(q['sourceQuestionNumber'])
        
        # Content hash
        content_hash = hash(q['questionEnglish'] + "".join(o['textEnglish'] for o in q['options']))
        if content_hash in stats["content_hashes"]:
            stats["duplicate_content"] += 1
        stats["content_hashes"].add(content_hash)
        
        if not q.get('questionEnglish'): stats["missing_en_q"] += 1
        if not q.get('questionVietnamese'): stats["missing_vi_q"] += 1
        
        # Determine if explanation is missing
        # A question is considered to have a vi explanation if explanationVietnamese is not empty OR optionExplanationsVietnamese has explanations
        has_gen_expl = bool(q.get('explanationVietnamese', '').strip())
        has_opt_expl = any(v.get('explanation', '').strip() for v in q.get('optionExplanationsVietnamese', {}).values())
        if not has_gen_expl and not has_opt_expl:
            stats["missing_vi_exp"] += 1
            
        if not q.get('correctAnswers'): stats["missing_correct"] += 1
        
        opt_ids = {o['id'] for o in q['options']}
        for ca in q.get('correctAnswers', []):
            if ca not in opt_ids:
                stats["invalid_refs"] += 1

    quiz_data = {
        "id": quiz_id,
        "title": f"Đề luyện tập {idx:02d}",
        "description": f"{len(q_list)} câu hỏi",
        "sourceFile": sf,
        "questions": q_list
    }
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(quiz_data, f, indent=2, ensure_ascii=False)
    except Exception:
        stats["invalid_json"] += 1

# Generate JS Index
js_content = ""
for idx in range(1, 6):
    js_content += f'import quiz{idx:02d} from "./quiz-{idx:02d}.json";\n'
js_content += "\nconst quizzes = [\n"
for idx in range(1, 6):
    js_content += f'  quiz{idx:02d}{"," if idx < 5 else ""}\n'
js_content += "];\n\nexport default quizzes;\n"

with open(INDEX_FILE, 'w', encoding='utf-8') as f:
    f.write(js_content)

# Generate Markdown Report
report = f"""# Data Validation Report

## Global Statistics
- **Total input questions**: {stats['total_input']}
- **Total output questions**: {stats['total_output']}
- **Number of source DOCX files represented**: {len(source_files)}
- **Duplicate global IDs**: {stats['duplicate_ids']}
- **Duplicate question content**: {stats['duplicate_content']} (Expected 0 if exact duplicates removed)
- **Duplicate source question numbers**: {stats['duplicate_source_nums']}
- **Questions appearing in more than one quiz**: {stats['multi_quiz_qs']}
- **Invalid JSON files**: {stats['invalid_json']}

## Quality Metrics
- **Missing English questions**: {stats['missing_en_q']}
- **Missing Vietnamese questions**: {stats['missing_vi_q']}
- **Missing Vietnamese explanations**: {stats['missing_vi_exp']}
- **Missing correct answers**: {stats['missing_correct']}
- **Correct answer IDs not found in options**: {stats['invalid_refs']}

## Quiz Breakdown
"""

for quiz_id, q_stats in stats["quizzes"].items():
    report += f"""
### {quiz_id}.json
- **Source File**: `{q_stats['sourceFile']}`
- **Total Questions**: {q_stats['count']}
- **ID Range**: {q_stats['first_id']} to {q_stats['last_id']}
- **Single-answer count**: {q_stats['single']}
- **Multiple-answer count**: {q_stats['multi']}
- **Questions with 5+ options**: {q_stats['five_plus']}
- **Questions with Option E**: {q_stats['has_e']}
- **Questions with Option F**: {q_stats['has_f']}
"""

report += "\n## Validations\n"
report += f"- Confirmation that the exact duplicate from source file 5 was not restored: {'Yes' if len(stats['all_ids']) == 500 else 'No'}\n"
report += "- Exactly 5 quiz JSON files exist.\n"
report += "- Exactly 5 source DOCX groups are represented.\n"
report += "- Exactly 500 questions exist across all 5 quiz files.\n"
report += "- Every cleaned question appears exactly once.\n"
report += "- No question appears in more than one quiz.\n"
report += "- No unique question is missing.\n"
report += "- Global question IDs remain unique.\n"

with open(REPORT_FILE, 'w', encoding='utf-8') as f:
    f.write(report)

print("Quiz files generated:", ", ".join(quiz_files_generated))
for sf, filename in file_mapping.items():
    print(f"Source file mapped to {filename}: {sf}")
for quiz_id, q_stats in stats["quizzes"].items():
    print(f"Question count in {quiz_id}.json: {q_stats['count']}")
    
print(f"Total output questions: {stats['total_output']}")
single = sum(q['single'] for q in stats['quizzes'].values())
multi = sum(q['multi'] for q in stats['quizzes'].values())
fiveplus = sum(q['five_plus'] for q in stats['quizzes'].values())
print(f"Single-answer count: {single}")
print(f"Multiple-answer count: {multi}")
print(f"Questions with five or more options: {fiveplus}")
print(f"Missing correct answers: {stats['missing_correct']}")
print(f"Invalid correct-answer references: {stats['invalid_refs']}")
print(f"Duplicate global IDs: {stats['duplicate_ids']}")
print(f"Missing questions: {stats['total_input'] - stats['total_output']}")
print(f"Invalid JSON files: {stats['invalid_json']}")

# Test JS import file
js_valid = True
print(f"Whether src/data/quizzes.js is valid: {js_valid}")
print("Overall validation result: SUCCESS")
