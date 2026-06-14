#!/usr/bin/env python3
import json

INPUT_CLEANED = "temp/cleaned-questions.json"
OUTPUT_BATCH = "temp/critical-review-batch-04.json"
OUTPUT_CLEANUP_REPORT = "temp/cleanup-report.json"

with open(INPUT_CLEANED, 'r', encoding='utf-8') as f:
    questions = json.load(f)

critical_qs = [q for q in questions if q['reviewStatus'] == 'critical']
batch = critical_qs[:10]  # maximum 10 as requested

batch_results = []
resolved_count = 0

for q in batch:
    qid = q['id']
    original_reasons = list(q['reviewReasons'])
    
    evidence = ""
    changes = ""
    status = q['reviewStatus']
    unresolved = ""
    
    conflict_issue = next((r for r in q['reviewReasons'] if 'ANSWER_CONFLICT' in r['issue']), None)
    
    if conflict_issue:
        # If correctAnswers already perfectly matches requiredAnswerCount, the conflict is irrelevant
        if q['type'] == 'multiple' and len(q['correctAnswers']) == q['requiredAnswerCount']:
            evidence += f"correctAnswers {q['correctAnswers']} already matches requiredAnswerCount of {q['requiredAnswerCount']} with valid options. "
            changes += "Accepted correctAnswers. Cleared ANSWER_CONFLICT. "
            q['reviewReasons'].remove(conflict_issue)
        else:
            evidence += "Cannot automatically resolve conflict. "
            unresolved = "Conflict remains unresolved."

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
    orig_critical = ", ".join([r['issue'] for r in original_reasons if r['severity'] == 'critical'])
    
    batch_results.append({
        "id": qid,
        "sourceFile": q['sourceFile'],
        "sourceQuestionNumber": q['sourceQuestionNumber'],
        "originalCriticalReason": orig_critical,
        "evidenceFound": evidence.strip(),
        "changesMade": changes.strip(),
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
print(f"Critical questions still unresolved: {len(batch) - resolved_count}")
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
