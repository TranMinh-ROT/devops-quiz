# QA Report

## Features Implemented
- **Home Page**: Displays website title, Vietnamese description, global study statistics (completed, correct, incorrect, bookmarked), and 5 distinct quiz cards pulling actual data. Added "Xóa toàn bộ tiến độ" with confirmation.
- **Quiz Page Layout**: Dynamically displays total questions, progress bar, timer, bilingual question text, options, confirm button, and numbered Question Navigator.
- **Bilingual Display**: Consistently displays English text followed by Vietnamese text (if available) with clear visual `English`/`Tiếng Việt` labels.
- **Single/Multiple Answer Logic**: Checkbox vs Radio behavior implemented. Enforces selection limit using `requiredAnswerCount` for multiple-choice questions. 
- **Grading & Confirmation**: `checkAnswer` safely normalizes, deduplicates, and sorts user input vs correct answers to evaluate combinations irrespective of order. No partial credit given.
- **Vietnamese Explanations**: Only Vietnamese explanations are rendered. Missing explanations fallback gracefully to a placeholder.
- **Navigation**: Full numbered index (1 to 100), Prev/Next controls, state color-coding (current, answered, confirmed correct/incorrect, bookmarked).
- **Bookmarks & Filters**: Bookmarks persist. Filtering implemented (All, Unanswered, Answered, Confirmed, Correct, Incorrect, Bookmarked).
- **Submit Flow**: Warns about unanswered questions before transitioning to Result Page. Unanswered evaluated as incorrect.
- **Result Page**: Displays score, percentage, elapsed time, pass/fail status. 
- **Review Page**: Exclusively filters and renders incorrect questions for targeted practice.
- **State Persistence**: `useQuizProgress` cleanly synchronizes with `localStorage`. `clearAllStorage` effectively wipes progress across all keys safely.
- **Accessibility & Design**: Utilizes CSS variables and Modules for a light, responsive theme with accessible contrast and focus semantics.

## Tests Performed
- ✅ Home page displays exactly 5 quiz cards.
- ✅ Every quiz displays 100 questions.
- ✅ Single-answer (radio) restricts selection to 1 option.
- ✅ Multiple-answer (checkbox) enforces the specific `requiredAnswerCount` limit and ignores selection order during grading.
- ✅ Bilingual questions display both languages cleanly without toggles.
- ✅ Explanations panel correctly loads Vietnamese explanations and dynamically handles missing translations.
- ✅ Previous/Next and direct numbering navigation works without losing state.
- ✅ LocalStorage correctly persists state across browser refreshes and page navigation.
- ✅ Reset all progress functions successfully after dialog confirmation.
- ✅ Mobile responsiveness configured successfully for Question Navigator via flex-wrap and responsive sidebars.
- ✅ `npm run build` succeeds without build-breaking errors.

## Build Result
- **Result**: `SUCCESS` (✓ built in 1.08s)

## Bugs Found & Fixed
- *Bug*: Question Navigator originally mapped array indices assuming global question IDs sequential ordering.
- *Fix*: Mapped indices safely using dynamic lookup in the `quiz.questions` array to accurately render 1-100 buttons regardless of global ID values.

## Remaining Unresolved Issues
- None.
