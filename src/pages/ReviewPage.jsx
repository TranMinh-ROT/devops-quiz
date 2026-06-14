import React, { useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import quizzes from '../data/quizzes.js';
import { useQuizProgress } from '../hooks/useQuizProgress';
import QuestionCard from '../components/QuestionCard';

export default function ReviewPage() {
  const { quizId } = useParams();
  const navigate = useNavigate();
  const quiz = useMemo(() => quizzes.find(q => q.id === quizId), [quizId]);
  const { state: progress } = useQuizProgress(quizId);

  if (!quiz) return null;

  // Filter only incorrect questions
  const incorrectQuestions = quiz.questions.filter(q => progress.results[q.id] === 'incorrect');

  return (
    <div className="review-page">
      <div className="review-header">
        <h2>Ôn tập câu sai: {quiz.title}</h2>
        <button className="btn outline" onClick={() => navigate(`/result/${quizId}`)}>
          Quay lại kết quả
        </button>
      </div>

      {incorrectQuestions.length === 0 ? (
        <div className="review-success">
          <p>Chúc mừng! Bạn không có câu trả lời sai nào trong đề này.</p>
        </div>
      ) : (
        <div className="review-list">
          {incorrectQuestions.map((q, index) => (
            <div key={q.id} className="review-item">
              <h3>Câu {quiz.questions.findIndex(x => x.id === q.id) + 1}</h3>
              <QuestionCard 
                question={q}
                userAnswers={progress.answers[q.id] || []}
                isConfirmed={true}
                isCorrect={false}
                isBookmarked={!!progress.bookmarks[q.id]}
                onSelectAnswer={() => {}}
                onConfirmAnswer={() => {}}
                onToggleBookmark={() => {}}
              />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
