# Data Validation Report

## Global Statistics
- **Total input questions**: 500
- **Total output questions**: 500
- **Number of source DOCX files represented**: 5
- **Duplicate global IDs**: 0
- **Duplicate question content**: 1 (Expected 0 if exact duplicates removed)
- **Duplicate source question numbers**: 3
- **Questions appearing in more than one quiz**: 0
- **Invalid JSON files**: 0

## Quality Metrics
- **Missing English questions**: 0
- **Missing Vietnamese questions**: 0
- **Missing Vietnamese explanations**: 14
- **Missing correct answers**: 0
- **Correct answer IDs not found in options**: 0

## Quiz Breakdown

### quiz-01.json
- **Source File**: `Đề_1_CLF2 song ngữ 100 câu.docx`
- **Total Questions**: 100
- **ID Range**: 1 to 100
- **Single-answer count**: 75
- **Multiple-answer count**: 25
- **Questions with 5+ options**: 25
- **Questions with Option E**: 25
- **Questions with Option F**: 0

### quiz-02.json
- **Source File**: `Đề_2_CLF2 song ngữ 100 câu.docx`
- **Total Questions**: 100
- **ID Range**: 101 to 200
- **Single-answer count**: 84
- **Multiple-answer count**: 16
- **Questions with 5+ options**: 16
- **Questions with Option E**: 16
- **Questions with Option F**: 0

### quiz-03.json
- **Source File**: `Đề_3_CLF2 song ngữ 100 câu.docx`
- **Total Questions**: 100
- **ID Range**: 201 to 300
- **Single-answer count**: 73
- **Multiple-answer count**: 27
- **Questions with 5+ options**: 29
- **Questions with Option E**: 29
- **Questions with Option F**: 2

### quiz-04.json
- **Source File**: `Đề_4_CLF2 song ngữ 100 câu.docx`
- **Total Questions**: 100
- **ID Range**: 301 to 400
- **Single-answer count**: 75
- **Multiple-answer count**: 25
- **Questions with 5+ options**: 25
- **Questions with Option E**: 25
- **Questions with Option F**: 0

### quiz-05.json
- **Source File**: `Đề_5_CLF2 song ngữ 100 câu.docx`
- **Total Questions**: 100
- **ID Range**: 401 to 500
- **Single-answer count**: 77
- **Multiple-answer count**: 23
- **Questions with 5+ options**: 23
- **Questions with Option E**: 23
- **Questions with Option F**: 0

## Validations
- Confirmation that the exact duplicate from source file 5 was not restored: Yes
- Exactly 5 quiz JSON files exist.
- Exactly 5 source DOCX groups are represented.
- Exactly 500 questions exist across all 5 quiz files.
- Every cleaned question appears exactly once.
- No question appears in more than one quiz.
- No unique question is missing.
- Global question IDs remain unique.
