#!/usr/bin/env python3
import json
import ast
import string

INPUT_CLEANED = "temp/cleaned-questions.json"
OUTPUT_BATCH = "temp/critical-review-batch-02.json"
OUTPUT_CLEANUP_REPORT = "temp/cleanup-report.json"

with open(INPUT_CLEANED, 'r', encoding='utf-8') as f:
    questions = json.load(f)

critical_qs = [q for q in questions if q['reviewStatus'] == 'critical']
batch = critical_qs[:25]

batch_results = []
resolved_count = 0

def reletter_options_and_answers(q, drop_indices):
    """Drop specified options (0-indexed), re-letter remaining A,B,C..., update correctAnswers."""
    new_options = []
    letters = "ABCDEFGHIJ"
    
    # Create mapping from old ID to new ID
    old_to_new = {}
    new_idx = 0
    for i, opt in enumerate(q['options']):
        if i in drop_indices:
            continue
        new_id = letters[new_idx]
        old_to_new[opt['id']] = new_id
        
        new_opt = dict(opt)
        new_opt['id'] = new_id
        new_options.append(new_opt)
        new_idx += 1
        
    q['options'] = new_options
    
    # Update correct answers based on mapping
    new_correct = []
    for ca in q['correctAnswers']:
        if ca in old_to_new:
            new_correct.append(old_to_new[ca])
    q['correctAnswers'] = new_correct

for q in batch:
    qid = q['id']
    original_reasons = list(q['reviewReasons'])
    
    evidence = ""
    changes = ""
    status = q['reviewStatus']
    unresolved = ""
    
    # Process known specific fixes first
    if qid == 204:
        # Answers: Amazon S3 Standard + Amazon S3 Intelligent-Tiering -> Options E and A
        q['correctAnswers'] = ['A', 'E']
        evidence = "Answer line text explicitly lists options 'Amazon S3 Standard' and 'Amazon S3 Intelligent-Tiering'."
        changes = "Set correctAnswers to ['A', 'E']. Cleared COUNT_MISMATCH flag."
        q['reviewReasons'] = [r for r in q['reviewReasons'] if 'COUNT_MISMATCH' not in r['issue']]
    
    elif qid == 265:
        # Answers: Set up Auto Scaling groups... & Purchase Amazon EC2 Reserved instances... -> Options B and D
        q['correctAnswers'] = ['B', 'D']
        evidence = "Answer line text explicitly lists options B and D."
        changes = "Set correctAnswers to ['B', 'D']. Cleared COUNT_MISMATCH flag."
        q['reviewReasons'] = [r for r in q['reviewReasons'] if 'COUNT_MISMATCH' not in r['issue']]

    elif qid == 270:
        # Option A is Vietnamese question. Correct answers are Domain registration & Health checks.
        q['questionVietnamese'] = q['options'][0]['textEnglish']
        reletter_options_and_answers(q, [0])
        # Old E, F become D, E
        q['correctAnswers'] = ['D', 'E']
        evidence = "Option A was actually the Vietnamese question. Answer line explicitly lists new options D and E."
        changes = "Moved Option A to questionVietnamese. Re-lettered options. Set correctAnswers to ['D', 'E']. Cleared COUNT_MISMATCH and MISSING_VIETNAMESE_QUESTION flags."
        q['reviewReasons'] = [r for r in q['reviewReasons'] if 'COUNT_MISMATCH' not in r['issue'] and 'MISSING_VIETNAMESE_QUESTION' not in r['issue']]

    elif qid == 280:
        # Option A is Vietnamese question.
        q['questionVietnamese'] = q['options'][0]['textEnglish']
        reletter_options_and_answers(q, [0])
        # Answers were Make frequent... & Anticipate failure -> Old C and E -> New B and D
        q['correctAnswers'] = ['B', 'D']
        evidence = "Option A was actually the Vietnamese question. Answer line explicitly lists new options B and D."
        changes = "Moved Option A to questionVietnamese. Re-lettered options. Set correctAnswers to ['B', 'D']. Cleared COUNT_MISMATCH and MISSING_VIETNAMESE_QUESTION flags."
        q['reviewReasons'] = [r for r in q['reviewReasons'] if 'COUNT_MISMATCH' not in r['issue'] and 'MISSING_VIETNAMESE_QUESTION' not in r['issue']]

    elif qid == 284:
        q['questionVietnamese'] = q['options'][0]['textEnglish']
        reletter_options_and_answers(q, [0])
        # Old correct was C, becomes B
        q['correctAnswers'] = ['B']
        evidence = "Option A was actually the Vietnamese question."
        changes = "Moved Option A to questionVietnamese. Re-lettered options and correctAnswers. Cleared MISSING_VIETNAMESE_QUESTION flag."
        q['reviewReasons'] = [r for r in q['reviewReasons'] if 'MISSING_VIETNAMESE_QUESTION' not in r['issue']]

    elif qid == 289:
        q['questionVietnamese'] = q['options'][0]['textEnglish']
        reletter_options_and_answers(q, [0])
        # Old B, F becomes A, E
        q['correctAnswers'] = ['A', 'E']
        evidence = "Option A was actually the Vietnamese question."
        changes = "Moved Option A to questionVietnamese. Re-lettered options and correctAnswers. Cleared MISSING_VIETNAMESE_QUESTION flag."
        q['reviewReasons'] = [r for r in q['reviewReasons'] if 'MISSING_VIETNAMESE_QUESTION' not in r['issue']]

    elif qid == 291:
        q['questionVietnamese'] = q['options'][0]['textEnglish']
        reletter_options_and_answers(q, [0])
        # Old E becomes D
        q['correctAnswers'] = ['D']
        evidence = "Option A was actually the Vietnamese question."
        changes = "Moved Option A to questionVietnamese. Re-lettered options and correctAnswers. Cleared MISSING_VIETNAMESE_QUESTION flag."
        q['reviewReasons'] = [r for r in q['reviewReasons'] if 'MISSING_VIETNAMESE_QUESTION' not in r['issue']]

    elif qid == 293:
        # Answers: Configuration management & Operating system (OS) configuration -> Options C and D
        q['correctAnswers'] = ['C', 'D']
        evidence = "Answer line text explicitly lists options C and D."
        changes = "Set correctAnswers to ['C', 'D']. Cleared COUNT_MISMATCH flag."
        q['reviewReasons'] = [r for r in q['reviewReasons'] if 'COUNT_MISMATCH' not in r['issue']]

    else:
        # Process generic ANSWER_CONFLICT
        conflict_issue = next((r for r in q['reviewReasons'] if 'ANSWER_CONFLICT' in r['issue']), None)
        if conflict_issue:
            parts = conflict_issue['issue'].split('line=')[1].split(' sections=')
            sec_ans = ast.literal_eval(parts[1])
            
            if q['type'] == 'multiple' and len(sec_ans) == q['requiredAnswerCount']:
                evidence = f"CORRECT sections clearly identify correct answers {sec_ans}, matching requiredAnswerCount of {q['requiredAnswerCount']}."
                if set(q['correctAnswers']) != set(sec_ans):
                    q['correctAnswers'] = sec_ans
                    changes = f"Set correctAnswers to {sec_ans} to match CORRECT sections. Cleared ANSWER_CONFLICT flag."
                else:
                    changes = f"Confirmed correctAnswers matches CORRECT sections. Cleared ANSWER_CONFLICT flag."
                    
                q['reviewReasons'].remove(conflict_issue)
            else:
                evidence = "CORRECT sections do not match required answer count, or question is not multiple type."
                unresolved = "Cannot safely resolve conflict based on simple rules."
    
    # Update status based on remaining issues
    if any(r['severity'] == 'critical' for r in q['reviewReasons']):
        status = 'critical'
        unresolved = unresolved or "Other critical issues remain."
    elif any(r['severity'] == 'warning' for r in q['reviewReasons']):
        status = 'warning'
        resolved_count += 1
    else:
        status = 'clean'
        resolved_count += 1
        
    q['reviewStatus'] = status
    
    # Provide a generic original reason if multiple
    orig_critical = ", ".join([r['issue'] for r in original_reasons if r['severity'] == 'critical'])
    
    batch_results.append({
        "id": q['id'],
        "sourceFile": q['sourceFile'],
        "sourceQuestionNumber": q['sourceQuestionNumber'],
        "originalCriticalReason": orig_critical,
        "evidenceFound": evidence,
        "changesMade": changes,
        "finalReviewStatus": status,
        "unresolvedReason": unresolved if status == 'critical' else ""
    })

# Save the batch results
with open(OUTPUT_BATCH, 'w', encoding='utf-8') as f:
    json.dump(batch_results, f, indent=2, ensure_ascii=False)

# Save the updated questions
with open(INPUT_CLEANED, 'w', encoding='utf-8') as f:
    json.dump(questions, f, indent=2, ensure_ascii=False)

# Recalculate stats for the report
clean_count = sum(1 for q in questions if q['reviewStatus'] == 'clean')
warning_count = sum(1 for q in questions if q['reviewStatus'] == 'warning')
critical_count = sum(1 for q in questions if q['reviewStatus'] == 'critical')
ambig = sum(1 for q in questions if any("CONFLICT" in r['issue'] for r in q["reviewReasons"]))
manual_review_rem = sum(1 for q in questions if q["reviewStatus"] != "clean")

# Just load the old report and update the counts
with open(OUTPUT_CLEANUP_REPORT, 'r', encoding='utf-8') as f:
    report = json.load(f)

report['cleanQuestions'] = clean_count
report['warningQuestions'] = warning_count
report['criticalQuestions'] = critical_count
report['ambiguousQuestionsRemaining'] = ambig
report['manualReviewRemaining'] = manual_review_rem

with open(OUTPUT_CLEANUP_REPORT, 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print(f"Critical questions processed: {len(batch)}")
print(f"Critical questions resolved: {resolved_count}")
print(f"Critical questions still unresolved in this batch: {len(batch) - resolved_count}")
print(f"Total critical questions remaining: {critical_count}")
print(f"Total ambiguous questions remaining: {ambig}")
print(f"Whether all 500 questions remain: {len(questions) == 500}")

# Validate JSON
try:
    with open(INPUT_CLEANED, 'r') as f:
        json.load(f)
    print("Whether the JSON is valid: True")
except:
    print("Whether the JSON is valid: False")
