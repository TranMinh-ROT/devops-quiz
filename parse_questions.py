#!/usr/bin/env python3
"""Step 2 (v2): Parse 500 raw question blocks into structured question objects."""
import os, re, json

INPUT = "temp/raw-question-blocks.json"
OUTPUT = "temp/parsed-questions.json"
REPORT = "temp/parse-report.json"

with open(INPUT, 'r', encoding='utf-8') as f:
    data = json.load(f)
blocks = data["blocks"]

# ============================================================
# Helpers
# ============================================================

def split_bilingual_slash(text):
    """Split 'English / Vietnamese' at ' / '. Careful with URLs."""
    # Don't split URLs
    if text.strip().startswith("http"):
        return text.strip(), ""
    idx = text.find(" / ")
    if idx > 0:
        en = text[:idx].strip()
        vi = text[idx+3:].strip()
        # If 'vi' starts with arrow or known prefix, it's not Vietnamese translation
        if vi.startswith("→") or vi.startswith("->"):
            return text.strip(), ""
        return en, vi
    return text.strip(), ""

def split_bilingual_dash(text):
    """Split 'English - Vietnamese' at ' - '. Used for Files 1/2/3 options.
    Smart: skips dashes that are part of service names like 'AWS Health Dashboard - Service Health'."""
    # Vietnamese characters to detect which side is Vietnamese
    vn_chars = set('àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ')
    
    # Find all " - " positions and pick the best split
    idx = 0
    best_idx = -1
    while True:
        idx = text.find(" - ", idx)
        if idx < 0:
            break
        right = text[idx+3:].strip().lower()
        vn_count = sum(1 for c in right if c in vn_chars)
        if vn_count >= 2:
            best_idx = idx
            break
        idx += 3
    
    if best_idx > 0:
        return text[:best_idx].strip(), text[best_idx+3:].strip()
    return text.strip(), ""

def find_answer_line_idx(lines):
    """Find index of the answer line."""
    for i, line in enumerate(lines):
        s = line.strip()
        # Primary patterns
        if '→ Đáp án' in s or '-> Đáp án' in s:
            return i
        # "Answer: X\n Đáp án: Y" format (some File 1 questions)
        if re.match(r'^Answer:\s', s):
            return i
    return -1

def detect_question_type(text):
    """Detect if question is multiple-answer. Returns (type, requiredCount)."""
    t = text.lower()
    pats = [
        (r'select\s+two|chọn\s+hai|which\s+two|choose\s+two', 2),
        (r'select\s+three|chọn\s+ba|which\s+three|choose\s+three', 3),
        (r'select\s+four|chọn\s+bốn', 4),
        (r'select\s+all\s+that\s+apply', 0),
    ]
    for pat, count in pats:
        if re.search(pat, t):
            return "multiple", count
    return "single", 1

def extract_question_from_header(header):
    """Extract English (and maybe Vietnamese) question from header line."""
    # Remove "Question N:" or "Question N: / Câu hỏi N:" prefix
    m = re.match(r'^Question\s+\d+\s*:?\s*', header)
    if not m:
        return header.strip(), ""
    remainder = header[m.end():].strip()
    if not remainder:
        return "", ""
    # Handle "/ Câu hỏi N:" or "/ Câu N:"
    if remainder.startswith("/"):
        remainder = remainder[1:].strip()
        remainder = re.sub(r'^Câu\s*(hỏi\s*)?\d+\s*:?\s*', '', remainder).strip()
        if not remainder:
            return "", ""
        return "", remainder  # This was Vietnamese only in header
    # Handle bilingual with " / "
    if " / " in remainder:
        en, vi = split_bilingual_slash(remainder)
        vi = re.sub(r'^Câu\s*(hỏi\s*)?\d+\s*:?\s*', '', vi).strip()
        return en, vi
    return remainder, ""

def parse_options_from_lines(lines):
    """Parse option lines into structured options. Auto-assigns letter IDs."""
    options = []
    letters = "ABCDEFGHIJ"
    letter_idx = 0
    has_labeled = any(re.match(r'^[A-F][\.)]\ ', l.strip()) for l in lines if l.strip())
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check for labeled option: "A. text" or "A) text"
        m = re.match(r'^([A-F])[\.\)]\s+(.+)$', line)
        if m:
            opt_id = m.group(1)
            text = m.group(2).strip()
            if " / " in text:
                en, vi = split_bilingual_slash(text)
            elif " - " in text:
                en, vi = split_bilingual_dash(text)
            else:
                en, vi = text, ""
            options.append({"id": opt_id, "textEnglish": en, "textVietnamese": vi})
            # Update letter_idx to match
            if opt_id in letters:
                letter_idx = letters.index(opt_id) + 1
            continue
        
        # If this block has labeled options, skip unlabeled lines
        # (they are likely question continuation text, not options)
        if has_labeled:
            continue
        
        # Unlabeled option
        opt_id = letters[letter_idx] if letter_idx < len(letters) else f"X{letter_idx}"
        letter_idx += 1
        
        if " / " in line:
            en, vi = split_bilingual_slash(line)
        elif " - " in line:
            en, vi = split_bilingual_dash(line)
        else:
            en, vi = line, ""
        
        options.append({"id": opt_id, "textEnglish": en, "textVietnamese": vi})
    
    return options

def parse_answer_text(answer_line, options):
    """Parse the answer line to extract correct answer IDs."""
    text = answer_line.strip()
    
    # Remove various prefixes
    text = re.sub(r'^[→\-]+>?\s*Đáp án\s*(/\s*Answer)?\s*:?\s*', '', text).strip()
    text = re.sub(r'^Answer:\s*', '', text).strip()
    
    # Remove Vietnamese duplicate after " / → Đáp án" or " / → "
    for sep in [' / → Đáp án', '  / → ', ' / → ']:
        if sep in text:
            text = text.split(sep)[0].strip()
            break
    
    # Remove inline explanation
    for sep in [' → Giải thích', ' -> Giải thích']:
        if sep in text:
            text = text.split(sep)[0].strip()
            break
    
    # Remove Vietnamese after "\n Đáp án:" (newline within paragraph)
    if '\n' in text:
        text = text.split('\n')[0].strip()
    
    # Remove trailing Vietnamese description after " - " (e.g. "A + B   - ...")
    m_trail = re.match(r'^([A-F](?:\s*\+\s*[A-F])*)\s+-\s+.+$', text)
    if m_trail:
        text = m_trail.group(1).strip()
    
    # Try letter-based: "A", "A + B", "D + E + F"
    if re.match(r'^[A-F](\s*\+\s*[A-F])*\s*$', text):
        return re.findall(r'[A-F]', text)
    
    # Letter with text: "D. Amazon GuardDuty"
    m = re.match(r'^([A-F])[\.\)]\s+', text)
    if m:
        return [m.group(1)]
    
    # Text-based matching
    text_clean = re.sub(r'\s+', ' ', text).strip().lower()
    
    def sig_words(s):
        return [w for w in re.findall(r'[a-zA-Z]{3,}', s.lower()) if w not in ('the','and','for','are','was','that','this','with','from','into','also','been')]
    
    def word_overlap_score(s1, s2):
        w1 = set(sig_words(s1))
        w2 = set(sig_words(s2))
        if not w1 or not w2:
            return 0
        return len(w1 & w2) / max(len(w1), len(w2))
    
    # Try exact match
    for opt in options:
        if opt["textEnglish"].strip().lower() == text_clean:
            return [opt["id"]]
    
    # Try contains
    matches = []
    for opt in options:
        en = opt["textEnglish"].strip().lower()
        if en and len(en) > 3 and (en in text_clean or text_clean in en):
            matches.append(opt["id"])
    if len(matches) == 1:
        return matches
    
    # Try fuzzy: first N significant words match
    ans_words = sig_words(text)
    if ans_words:
        for opt in options:
            opt_words = sig_words(opt["textEnglish"])
            if opt_words and len(ans_words) >= 3 and ans_words[:3] == opt_words[:3]:
                return [opt["id"]]
    
    # Word overlap scoring - pick best match if score > 0.5
    if ans_words:
        best_score = 0
        best_opt = None
        for opt in options:
            score = word_overlap_score(text, opt["textEnglish"])
            if score > best_score:
                best_score = score
                best_opt = opt["id"]
        if best_score > 0.5 and best_opt:
            return [best_opt]
    
    # Multi-answer with "&" or " and "
    if " & " in text or " and " in text.lower():
        sep = " & " if " & " in text else " and "
        parts = [p.strip() for p in text.split(sep)]
        found = []
        for part in parts:
            part_lower = part.lower()
            part_words = sig_words(part)
            best_score = 0
            best_id = None
            for opt in options:
                en = opt["textEnglish"].strip().lower()
                if en and (part_lower in en or en in part_lower):
                    if opt["id"] not in found:
                        found.append(opt["id"])
                    best_id = None
                    break
                # Fuzzy fallback
                score = word_overlap_score(part, opt["textEnglish"])
                if score > best_score:
                    best_score = score
                    best_id = opt["id"]
            if best_id and best_score > 0.4 and best_id not in found:
                found.append(best_id)
        if found:
            return found
    
    # Last resort: if matches > 1, return all
    if matches:
        return matches
    
    return []

def extract_quoted(text):
    """Extract quoted text handling both straight and curly quotes."""
    # Try straight quotes first
    results = re.findall(r'"([^"]+)"', text)
    if results:
        return results
    # Try curly/smart quotes
    results = re.findall(r'[\u201c\u201d\u201e\u201f]([^\u201c\u201d\u201e\u201f]+)[\u201c\u201d\u201e\u201f]', text)
    if results:
        return results
    # Try mixed quotes (one curly, one straight)
    results = re.findall(r'[\u201c\u201d\u201e\u201f"]([^\u201c\u201d\u201e\u201f"]+)[\u201c\u201d\u201e\u201f"]', text)
    if results:
        return results
    return []

def parse_explanations_section(lines, options):
    """Parse post-answer lines for explanations, CORRECT/INCORRECT, references."""
    correct_ids = []
    option_explanations = {}
    general_expl_vi = ""
    references = []
    
    for line in lines:
        s = line.strip()
        if not s:
            continue
        
        # Vietnamese general explanation
        if s.startswith("Giải thích đáp án:"):
            general_expl_vi = s[len("Giải thích đáp án:"):].strip()
            continue
        if s.startswith("Giải thích:") and not general_expl_vi:
            general_expl_vi = s[len("Giải thích:"):].strip()
            continue
        
        # "→ Giải thích" line (File 5 style)
        m = re.match(r'^[→\-]+>?\s*Giải thích\s*(/\s*Explanation)?\s*:?\s*(.*)$', s)
        if m and not general_expl_vi:
            remainder = m.group(2).strip()
            if " / " in remainder:
                _, vi = split_bilingual_slash(remainder)
                general_expl_vi = vi if vi else remainder
            else:
                general_expl_vi = remainder
            continue
        
        # CORRECT lines
        if re.match(r'^(CORRECT|ĐÚNG)\s*(/\s*(ĐÚNG|CORRECT))?\s*:', s):
            quoted = extract_quoted(s)
            for q in quoted:
                matched = match_quoted_to_option(q, options)
                if matched and matched not in correct_ids:
                    correct_ids.append(matched)
                    # Extract Vietnamese explanation
                    vi_expl = ""
                    if " / " in s:
                        _, vi_part = split_bilingual_slash(s)
                        vi_expl = vi_part
                    option_explanations[matched] = {"isCorrect": True, "explanation": vi_expl}
            continue
        
        # SAI/ĐÚNG standalone Vietnamese lines
        if s.startswith("ĐÚNG:") or s.startswith("SAI:"):
            quoted = extract_quoted(s)
            is_correct = s.startswith("ĐÚNG:")
            for q in quoted:
                matched = match_quoted_to_option(q, options)
                if matched:
                    if is_correct and matched not in correct_ids:
                        correct_ids.append(matched)
                    vi_expl = s.split(":", 1)[1].strip() if ":" in s else ""
                    if matched not in option_explanations:
                        option_explanations[matched] = {"isCorrect": is_correct, "explanation": vi_expl}
            continue
        
        # INCORRECT lines
        if re.match(r'^INCORRECT\s*(/\s*SAI)?\s*:', s):
            quoted = extract_quoted(s)
            for q in quoted:
                matched = match_quoted_to_option(q, options)
                if matched:
                    vi_expl = ""
                    if " / " in s:
                        _, vi_part = split_bilingual_slash(s)
                        vi_expl = vi_part
                    if matched not in option_explanations:
                        option_explanations[matched] = {"isCorrect": False, "explanation": vi_expl}
            # Handle "Option text: explanation / Vietnamese" format (File 5)
            if not quoted:
                clean = re.sub(r'^INCORRECT\s*(/\s*SAI)?\s*:?\s*', '', s).strip()
                parse_inline_incorrect(clean, options, option_explanations)
            continue
        
        # SAI standalone with option text
        if s.startswith("SAI:"):
            quoted = extract_quoted(s)
            for q in quoted:
                matched = match_quoted_to_option(q, options)
                if matched and matched not in option_explanations:
                    vi_expl = s
                    option_explanations[matched] = {"isCorrect": False, "explanation": vi_expl}
            continue
        
        # Reference lines
        urls = extract_urls(s)
        if urls and (re.match(r'^(Reference|Tài liệu|via\s*[-–]|Nguồn|Save time|Tiết kiệm|https?://)', s, re.I)):
            references.extend(urls)
            continue
    
    return correct_ids, option_explanations, general_expl_vi, references

def match_quoted_to_option(quoted_text, options):
    """Match a quoted text from CORRECT/INCORRECT to an option ID.
    Handles ellipsis (...) and truncated text."""
    q = quoted_text.strip().rstrip('.')
    q_lower = q.lower()
    # Remove trailing ellipsis for prefix matching
    q_prefix = q_lower.rstrip('.').rstrip('…').strip()
    
    for opt in options:
        en = opt["textEnglish"].strip().lower()
        vi = opt["textVietnamese"].strip().lower()
        # Exact match
        if en and (q_lower == en or q_lower == en.rstrip('.')):
            return opt["id"]
        if vi and (q_lower == vi or q_lower == vi.rstrip('.')):
            return opt["id"]
        # Contains match
        if en and len(q_lower) > 5 and (q_lower in en or en in q_lower):
            return opt["id"]
        if vi and len(q_lower) > 5 and (q_lower in vi or vi in q_lower):
            return opt["id"]
        # Prefix match (for ellipsis-truncated text)
        if q_prefix and len(q_prefix) > 10:
            if en and en.startswith(q_prefix):
                return opt["id"]
            if vi and vi.startswith(q_prefix):
                return opt["id"]
    return None

def parse_inline_incorrect(text, options, explanations):
    """Parse 'Option text: explanation / Vietnamese' format."""
    if ": " not in text:
        return
    opt_text = text.split(": ")[0].strip().strip('"')
    explanation = ": ".join(text.split(": ")[1:])
    matched = match_quoted_to_option(opt_text, options)
    if matched and matched not in explanations:
        vi_expl = ""
        if " / " in explanation:
            _, vi_expl = split_bilingual_slash(explanation)
        else:
            vi_expl = explanation
        explanations[matched] = {"isCorrect": False, "explanation": vi_expl}

def extract_urls(text):
    """Extract URLs from text."""
    return re.findall(r'https?://[^\s,\'"]+', text)

def is_question_text_line(line):
    """Check if a line is question text (not an option)."""
    s = line.strip()
    if s.startswith("Đề bài:"):
        return True
    if re.match(r'^Câu\s*(hỏi\s*)?\d+', s):
        return True
    return False

def is_filler_line(line):
    """Check if a line is a filler/skip line."""
    s = line.strip()
    filler_starts = [
        "Đáp án:", "Giải thích đáp án:", "Giải thích:", 
        "CORRECT", "ĐÚNG", "INCORRECT", "SAI",
        "Incorrect options:", "Các lựa chọn không đúng:",
        "Reference", "Tài liệu tham khảo", "via ", "Nguồn",
        "Save time", "Tiết kiệm", "http", "Thông tin này",
        "Nội dung này", "Chiến lược này", "----------------------------------------"
    ]
    for f in filler_starts:
        if s.startswith(f):
            return True
    return False

# ============================================================
# Main parser
# ============================================================

def parse_question_block(block, global_id):
    lines = block["lines"]
    source_file = block["sourceFile"]
    source_qn = block["sourceQuestionNumber"]
    issues = []
    
    # 1. Find answer line
    answer_idx = find_answer_line_idx(lines)
    if answer_idx == -1:
        issues.append("NO_ANSWER_LINE")
        answer_idx = len(lines)
    
    # 2. Extract question text
    en_q, vi_q = extract_question_from_header(lines[0])
    
    # 3. Determine option start index
    opt_start = 1
    
    if len(lines) > 1:
        line1 = lines[1].strip()
        
        # Check if line1 is Vietnamese question
        if line1.startswith("Đề bài:"):
            if not vi_q:
                vi_q = line1[len("Đề bài:"):].strip()
            opt_start = 2
        elif re.match(r'^Câu\s*(hỏi\s*)?\d+', line1):
            if not vi_q:
                vi_q = re.sub(r'^Câu\s*(hỏi\s*)?\d+\s*:?\s*', '', line1).strip()
            opt_start = 2
        elif line1.startswith("/ ") or line1.startswith("/\n"):
            # Vietnamese question on separate line starting with "/"
            vi_text = line1[1:].strip()
            vi_text = re.sub(r'^Câu\s*(hỏi\s*)?\d+\s*:?\s*', '', vi_text).strip()
            if not vi_q:
                vi_q = vi_text
            opt_start = 2
        elif not en_q:
            # Header had no question text, line1 IS the question
            if " / " in line1:
                en_q, vi_q = split_bilingual_slash(line1)
                opt_start = 2
                # Check if line2 is also a Vietnamese continuation starting with "/"
                if len(lines) > 2 and lines[2].strip().startswith("/"):
                    vi_text = lines[2].strip()[1:].strip()
                    vi_text = re.sub(r'^Câu\s*(hỏi\s*)?\d+\s*:?\s*', '', vi_text).strip()
                    if vi_text and not vi_q:
                        vi_q = vi_text
                    opt_start = 3
            else:
                en_q = line1
                # Check if line2 is Vietnamese
                if len(lines) > 2:
                    l2 = lines[2].strip()
                    if is_question_text_line(l2) or l2.startswith("/"):
                        vi_q = re.sub(r'^Đề bài:\s*', '', l2)
                        vi_q = re.sub(r'^/\s*', '', vi_q)
                        vi_q = re.sub(r'^Câu\s*(hỏi\s*)?\d+\s*:?\s*', '', vi_q).strip()
                        opt_start = 3
                    else:
                        opt_start = 2
                else:
                    opt_start = 2
    
    # 4. Collect option lines (everything between opt_start and answer_idx)
    raw_option_lines = [l for l in lines[opt_start:answer_idx] if l.strip()]
    
    # 5. Parse options
    options = parse_options_from_lines(raw_option_lines)
    
    if not options:
        issues.append("NO_OPTIONS")
    
    # 6. Parse answer
    correct_answers = []
    if answer_idx < len(lines):
        correct_answers = parse_answer_text(lines[answer_idx], options)
    
    # 7. Parse post-answer section
    post_lines = lines[answer_idx + 1:] if answer_idx < len(lines) else []
    correct_from_sections, opt_explanations, gen_expl_vi, refs = \
        parse_explanations_section(post_lines, options)
    
    # 8. Detect question type
    combined_q = f"{en_q} {vi_q}"
    qtype, req_count = detect_question_type(combined_q)
    
    # 9. Cross-check answers
    if correct_from_sections and correct_answers:
        if set(correct_from_sections) != set(correct_answers):
            issues.append(f"ANSWER_CONFLICT: line={correct_answers} sections={correct_from_sections}")
            # Prefer whichever matches expected count
            if qtype == "multiple" and req_count > 0:
                if len(correct_from_sections) == req_count:
                    correct_answers = correct_from_sections
                elif len(correct_answers) != req_count and len(correct_from_sections) > len(correct_answers):
                    correct_answers = correct_from_sections
            elif qtype == "single":
                if len(correct_from_sections) == 1:
                    correct_answers = correct_from_sections
                elif len(correct_answers) == 1:
                    pass  # keep answer line
    elif correct_from_sections and not correct_answers:
        correct_answers = correct_from_sections
    # For multi-answer: if answer line found fewer than expected, supplement from CORRECT sections
    if qtype == "multiple" and req_count > 0 and correct_from_sections:
        if len(correct_answers) < req_count and len(correct_from_sections) >= req_count:
            correct_answers = correct_from_sections
        elif len(correct_answers) < req_count:
            # Merge: add section answers not already present
            for ca in correct_from_sections:
                if ca not in correct_answers:
                    correct_answers.append(ca)
    
    # Fix requiredAnswerCount
    if qtype == "multiple" and req_count == 0:
        req_count = len(correct_answers) if correct_answers else 2
    if qtype == "single":
        req_count = 1
    if qtype == "multiple" and correct_answers and len(correct_answers) != req_count:
        issues.append(f"COUNT_MISMATCH: required={req_count} got={len(correct_answers)}")
    
    # Ensure all options have explanation entries
    for opt in options:
        if opt["id"] not in opt_explanations:
            opt_explanations[opt["id"]] = {
                "isCorrect": opt["id"] in correct_answers,
                "explanation": ""
            }
        else:
            opt_explanations[opt["id"]]["isCorrect"] = opt["id"] in correct_answers
    
    # Validate
    if not correct_answers:
        issues.append("NO_CORRECT_ANSWERS")
    if not en_q:
        issues.append("MISSING_ENGLISH_QUESTION")
    if not vi_q:
        issues.append("MISSING_VIETNAMESE_QUESTION")
    if not gen_expl_vi:
        issues.append("MISSING_VIETNAMESE_EXPLANATION")
    
    opt_ids = {o["id"] for o in options}
    for ca in correct_answers:
        if ca not in opt_ids:
            issues.append(f"INVALID_ANSWER_ID: {ca}")
    
    return {
        "id": global_id,
        "sourceFile": source_file,
        "sourceQuestionNumber": source_qn,
        "type": qtype,
        "requiredAnswerCount": req_count,
        "questionEnglish": en_q,
        "questionVietnamese": vi_q,
        "options": options,
        "correctAnswers": correct_answers,
        "explanationVietnamese": gen_expl_vi,
        "optionExplanationsVietnamese": opt_explanations,
        "references": refs,
        "_issues": issues
    }

# ============================================================
# Run
# ============================================================
questions = []
all_issues = []

for i, block in enumerate(blocks):
    q = parse_question_block(block, i + 1)
    questions.append(q)
    if q["_issues"]:
        all_issues.append({"id": q["id"], "source": q["sourceFile"],
                          "qn": q["sourceQuestionNumber"], "issues": q["_issues"]})

with open(OUTPUT, 'w', encoding='utf-8') as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)

# Stats
single = sum(1 for q in questions if q["type"] == "single")
multi = sum(1 for q in questions if q["type"] == "multiple")
sel2 = sum(1 for q in questions if q["type"] == "multiple" and q["requiredAnswerCount"] == 2)
sel3 = sum(1 for q in questions if q["type"] == "multiple" and q["requiredAnswerCount"] == 3)
five_plus = sum(1 for q in questions if len(q["options"]) >= 5)
no_opts = sum(1 for q in questions if not q["options"])
few_opts = sum(1 for q in questions if 0 < len(q["options"]) < 4)
miss_en = sum(1 for q in questions if not q["questionEnglish"])
miss_vi = sum(1 for q in questions if not q["questionVietnamese"])
miss_ans = sum(1 for q in questions if not q["correctAnswers"])
miss_expl = sum(1 for q in questions if not q["explanationVietnamese"])
ambig = sum(1 for q in questions if any("CONFLICT" in i for i in q["_issues"]))
inv_ids = sum(1 for q in questions if any("INVALID_ANSWER_ID" in i for i in q["_issues"]))
review = sum(1 for q in questions if q["_issues"])

# Validations
vals = []
vals.append(("Exactly 500 questions", len(questions) == 500))
ids = [q["id"] for q in questions]
vals.append(("Unique IDs 1-500", sorted(ids) == list(range(1, 501))))
vals.append(("All have >= 2 options", all(len(q["options"]) >= 2 for q in questions)))
vals.append(("Option IDs unique per Q", all(len(set(o["id"] for o in q["options"])) == len(q["options"]) for q in questions)))
vals.append(("Correct answers in options", all(all(ca in {o["id"] for o in q["options"]} for ca in q["correctAnswers"]) for q in questions if q["correctAnswers"])))
vals.append(("Single has 1 correct", all(len(q["correctAnswers"]) == 1 for q in questions if q["type"] == "single" and q["correctAnswers"])))
vals.append(("Multiple has >= 2 correct", all(len(q["correctAnswers"]) >= 2 for q in questions if q["type"] == "multiple" and q["correctAnswers"])))
vals.append(("reqCount matches answers", all(q["requiredAnswerCount"] == len(q["correctAnswers"]) for q in questions if q["correctAnswers"])))

report = {
    "totalParsed": len(questions), "singleAnswer": single, "multipleAnswer": multi,
    "selectTwo": sel2, "selectThree": sel3, "fivePlusOptions": five_plus,
    "noOptions": no_opts, "fewerThan4Options": few_opts,
    "missingEnglishQuestion": miss_en, "missingVietnameseQuestion": miss_vi,
    "missingCorrectAnswers": miss_ans, "missingVietnameseExplanation": miss_expl,
    "ambiguousAnswers": ambig, "invalidAnswerIds": inv_ids,
    "needsManualReview": review,
    "validations": {n: p for n, p in vals},
    "issueDetails": all_issues
}
with open(REPORT, 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print(f"Total parsed: {len(questions)}")
print(f"Single-answer: {single}")
print(f"Multiple-answer: {multi}")
print(f"  Select TWO: {sel2}")
print(f"  Select THREE: {sel3}")
print(f"5+ options: {five_plus}")
print(f"Missing correct answers: {miss_ans}")
print(f"Ambiguous answers: {ambig}")
print(f"Invalid answer IDs: {inv_ids}")
print(f"Needs review: {review}")
print(f"\nValidations:")
for n, p in vals:
    print(f"  {'✓' if p else '✗'} {n}")
print(f"\nSaved to {OUTPUT} and {REPORT}")
