import React, { useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import quizzes from '../data/quizzes.js';
import { useQuizProgress } from '../hooks/useQuizProgress';

export default function ResultPage() {
  const { quizId } = useParams();
  const navigate = useNavigate();
  const quiz = useMemo(() => quizzes.find(q => q.id === quizId), [quizId]);
  
  const { state: progress, restartQuiz } = useQuizProgress(quizId);

  if (!quiz) return null;

  const totalQuestions = quiz.questions.length;
  const correctCount = progress.score || 0;
  const incorrectCount = Object.values(progress.results).filter(r => r === 'incorrect').length;
  const unansweredCount = totalQuestions - correctCount - incorrectCount;
  
  const percentage = Math.round((correctCount / totalQuestions) * 100);
  const isPassed = percentage >= 70;

  const formatDuration = (start, end) => {
    if (!start || !end) return "Không xác định";
    const seconds = Math.floor((end - start) / 1000);
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m} phút ${s} giây`;
  };

  const handleReviewIncorrect = () => {
    navigate(`/review/${quizId}`);
  };

  const handleRestart = () => {
    if (window.confirm("Bạn có chắc chắn muốn làm lại đề? Toàn bộ tiến độ hiện tại của đề này sẽ bị xóa.")) {
      restartQuiz();
      navigate(`/quiz/${quizId}`);
    }
  };

  const handleGoHome = () => {
    navigate('/');
  };

  return (
    <div className="result-page">
      <div className="result-card">
        <h2 className="result-title">Kết quả: {quiz.title}</h2>
        
        <div className={`result-status ${isPassed ? 'passed' : 'failed'}`}>
          {isPassed ? 'Đạt' : 'Chưa đạt'}
        </div>
        
        <div className="score-circle">
          <div className="score-text">{percentage}%</div>
        </div>

        <div className="result-details">
          <div className="detail-row">
            <span>Tổng số câu:</span>
            <span>{totalQuestions}</span>
          </div>
          <div className="detail-row">
            <span>Trả lời đúng:</span>
            <span className="text-green font-bold">{correctCount}</span>
          </div>
          <div className="detail-row">
            <span>Trả lời sai:</span>
            <span className="text-red font-bold">{incorrectCount}</span>
          </div>
          <div className="detail-row">
            <span>Chưa trả lời:</span>
            <span>{unansweredCount}</span>
          </div>
          <div className="detail-row">
            <span>Thời gian hoàn thành:</span>
            <span>{formatDuration(progress.startTime, progress.endTime)}</span>
          </div>
        </div>

        <div className="result-actions">
          {incorrectCount > 0 && (
            <button className="btn outline" onClick={handleReviewIncorrect}>
              Xem lại câu sai
            </button>
          )}
          <button className="btn primary" onClick={handleRestart}>
            Làm lại toàn bộ đề
          </button>
          <button className="btn outline" onClick={handleGoHome}>
            Quay về trang chủ
          </button>
        </div>
      </div>
    </div>
  );
}
