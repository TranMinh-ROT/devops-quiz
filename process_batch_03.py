#!/usr/bin/env python3
import json
import ast
import re

INPUT_CLEANED = "temp/cleaned-questions.json"
OUTPUT_BATCH = "temp/critical-review-batch-03.json"
OUTPUT_CLEANUP_REPORT = "temp/cleanup-report.json"

with open(INPUT_CLEANED, 'r', encoding='utf-8') as f:
    questions = json.load(f)

critical_qs = [q for q in questions if q['reviewStatus'] == 'critical']
batch = critical_qs[:25]

batch_results = []
resolved_count = 0

for q in batch:
    qid = q['id']
    original_reasons = list(q['reviewReasons'])
    
    evidence = ""
    changes = ""
    status = q['reviewStatus']
    unresolved = ""
    
    if qid == 397:
        q['correctAnswers'] = ['C', 'E']
        evidence = "Answer line text explicitly lists options C and E. "
        changes = "Set correctAnswers to ['C', 'E']. Cleared COUNT_MISMATCH flag. "
        q['reviewReasons'] = [r for r in q['reviewReasons'] if 'COUNT_MISMATCH' not in r['issue']]

    elif qid == 400:
        q['correctAnswers'] = ['A', 'C']
        evidence = "Answer line text explicitly lists options A and C. "
        changes = "Set correctAnswers to ['A', 'C']. Cleared COUNT_MISMATCH flag. "
        q['reviewReasons'] = [r for r in q['reviewReasons'] if 'COUNT_MISMATCH' not in r['issue']]

    # Handle MISSING_VIETNAMESE_QUESTION
    miss_vi_issue = next((r for r in q['reviewReasons'] if 'MISSING_VIETNAMESE_QUESTION' in r['issue']), None)
    if miss_vi_issue:
        text = q['questionEnglish']
        m = re.search(r'([?.)])\s*/\s*(.*)$', text)
        if m:
            q['questionEnglish'] = text[:m.start(1)+1].strip()
            q['questionVietnamese'] = m.group(2).strip()
            evidence += "Found merged Vietnamese text in questionEnglish. "
            changes += "Split questionEnglish into questionEnglish and questionVietnamese. Cleared MISSING_VIETNAMESE_QUESTION. "
            q['reviewReasons'].remove(miss_vi_issue)
        else:
            parts = text.rsplit('/', 1)
            if len(parts) == 2:
                q['questionEnglish'] = parts[0].strip()
                q['questionVietnamese'] = parts[1].strip()
                evidence += "Found merged Vietnamese text separated by slash. "
                changes += "Split questionEnglish. Cleared MISSING_VIETNAMESE_QUESTION. "
                q['reviewReasons'].remove(miss_vi_issue)
    
    # Handle ANSWER_CONFLICT
    conflict_issue = next((r for r in q['reviewReasons'] if 'ANSWER_CONFLICT' in r['issue']), None)
    if conflict_issue:
        parts = conflict_issue['issue'].split('line=')[1].split(' sections=')
        line_ans = ast.literal_eval(parts[0])
        sec_ans = ast.literal_eval(parts[1])
        
        if q['type'] == 'multiple' and len(sec_ans) == q['requiredAnswerCount']:
            evidence += f"CORRECT sections identify {sec_ans}. "
            if set(q['correctAnswers']) != set(sec_ans):
                q['correctAnswers'] = sec_ans
                changes += f"Set correctAnswers to {sec_ans}. Cleared ANSWER_CONFLICT. "
            else:
                changes += "correctAnswers already matches. Cleared ANSWER_CONFLICT. "
            q['reviewReasons'].remove(conflict_issue)
        elif q['type'] == 'multiple' and len(line_ans) == q['requiredAnswerCount'] and len(sec_ans) < q['requiredAnswerCount']:
            evidence += f"Answer line correctly identifies {line_ans} matching requiredAnswerCount, while sections were incomplete. "
            if set(q['correctAnswers']) != set(line_ans):
                q['correctAnswers'] = line_ans
                changes += f"Set correctAnswers to {line_ans}. Cleared ANSWER_CONFLICT. "
            else:
                changes += "correctAnswers already matches line. Cleared ANSWER_CONFLICT. "
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
