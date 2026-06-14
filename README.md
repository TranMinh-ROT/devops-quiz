# DevOps Quiz Practice

A bilingual DevOps quiz-practice website designed for efficient and accessible studying, focusing on AWS certification preparation and general DevOps principles.

## 🚀 Main Features
- **Bilingual Interface**: Displays both English and Vietnamese questions/options seamlessly.
- **5 Full Quizzes**: Offers 5 complete 100-question practice exams.
- **Dynamic Grading**: Supports both single-answer and exact-match multiple-answer formats.
- **Vietnamese Explanations**: Provides detailed Vietnamese explanations for right and wrong options after confirmation.
- **Progress Tracking**: Tracks correct, incorrect, bookmarked, and unanswered questions via `localStorage`.
- **Review Mode**: Review and re-attempt incorrectly answered questions easily.
- **Responsive Layout**: Works seamlessly on desktop, tablet, and mobile devices.

## 📦 Local Installation

To run this project locally, execute the following commands:

```bash
git clone https://github.com/TranMinh-ROT/devops-quiz.git
cd devops-quiz
npm install
npm run dev
```

## 🛠 Production Verification

To verify the production build locally before deployment:

```bash
npm run build
npm run preview
```

## 🔗 Repository & Deployment

- **Repository URL**: [https://github.com/TranMinh-ROT/devops-quiz.git](https://github.com/TranMinh-ROT/devops-quiz.git)
- **GitHub Pages URL**: [https://tranminh-rot.github.io/devops-quiz/](https://tranminh-rot.github.io/devops-quiz/)

### Deployment Workflow
The project is configured with a GitHub Actions workflow (`.github/workflows/deploy.yml`) that automatically builds and deploys the `main` branch to GitHub Pages upon every push.

**⚠️ Manual GitHub Setting Required:**
For the deployment action to succeed, you must manually configure the Pages source in your GitHub repository:
1. Go to **Repository → Settings → Pages**
2. Under **Build and deployment → Source**, select **GitHub Actions**.

## 💾 localStorage Limitations
All progress (answers, scores, bookmarks, elapsed time) is saved entirely on the client side using the browser's `localStorage`. 
- Progress does not sync across different browsers or devices.
- Clearing your browser data or using incognito mode will reset your progress.
- You can manually clear progress using the "Xóa toàn bộ tiến độ" button on the home page.
