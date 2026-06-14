#!/usr/bin/env python3
import json
import ast

INPUT_CLEANED = "temp/cleaned-questions.json"
OUTPUT_BATCH = "temp/critical-review-batch-01.json"
OUTPUT_CLEANUP_REPORT = "temp/cleanup-report.json"

with open(INPUT_CLEANED, 'r', encoding='utf-8') as f:
    questions = json.load(f)

critical_qs = [q for q in questions if q['reviewStatus'] == 'critical']
batch = critical_qs[:25]

batch_results = []
resolved_count = 0

for q in batch:
    original_reasons = list(q['reviewReasons'])
    conflict_issue = next((r for r in original_reasons if 'ANSWER_CONFLICT' in r['issue']), None)
    
    evidence = ""
    changes = ""
    status = q['reviewStatus']
    unresolved = ""
    
    if conflict_issue:
        # e.g., ANSWER_CONFLICT: line=['A'] sections=['A', 'E']
        parts = conflict_issue['issue'].split('line=')[1].split(' sections=')
        line_ans = ast.literal_eval(parts[0])
        sec_ans = ast.literal_eval(parts[1])
        
        if q['type'] == 'multiple' and len(sec_ans) == q['requiredAnswerCount']:
            evidence = f"CORRECT sections clearly identify correct answers {sec_ans}, matching requiredAnswerCount of {q['requiredAnswerCount']}."
            
            # Check if correctAnswers is already correct, if not fix it
            if set(q['correctAnswers']) != set(sec_ans):
                q['correctAnswers'] = sec_ans
                changes = f"Set correctAnswers to {sec_ans} to match CORRECT sections. Cleared ANSWER_CONFLICT flag."
            else:
                changes = f"Confirmed correctAnswers matches CORRECT sections. Cleared ANSWER_CONFLICT flag."
                
            q['reviewReasons'].remove(conflict_issue)
            
            # Check if any critical issues remain
            if any(r['severity'] == 'critical' for r in q['reviewReasons']):
                status = 'critical'
                unresolved = "Other critical issues remain."
            elif any(r['severity'] == 'warning' for r in q['reviewReasons']):
                status = 'warning'
                resolved_count += 1
            else:
                status = 'clean'
                resolved_count += 1
                
            q['reviewStatus'] = status
        else:
            evidence = "CORRECT sections do not match required answer count, or question is not multiple type."
            unresolved = "Cannot safely resolve conflict based on simple rules."
    
    batch_results.append({
        "id": q['id'],
        "sourceFile": q['sourceFile'],
        "sourceQuestionNumber": q['sourceQuestionNumber'],
        "originalCriticalReason": conflict_issue['issue'] if conflict_issue else "Other",
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
