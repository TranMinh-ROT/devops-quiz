import React from 'react';
import { useNavigate } from 'react-router-dom';
import { loadFromStorage } from '../utils/storageUtils';

export default function QuizCard({ quiz }) {
  const navigate = useNavigate();
  const quizId = quiz.id;
  const progressState = loadFromStorage(`quiz_${quizId}`, null);
  
  const status = progressState?.status || 'not-started';
  const score = progressState?.score;
  const totalQuestions = quiz.questions.length;

  let buttonText = 'Bắt đầu luyện tập';
  if (status === 'in-progress') {
    buttonText = 'Tiếp tục';
  } else if (status === 'completed') {
    buttonText = 'Làm lại đề';
  }

  const handleAction = () => {
    navigate(`/quiz/${quizId}`);
  };

  return (
    <div className="quiz-card">
      <div className="quiz-card-header">
        <h3>{quiz.title}</h3>
        <p className="source-file">{quiz.sourceFile}</p>
      </div>
      <div className="quiz-card-body">
        <p><strong>Số lượng câu hỏi:</strong> {totalQuestions}</p>
        <p><strong>Trạng thái:</strong> {status === 'completed' ? 'Đã hoàn thành' : status === 'in-progress' ? 'Đang làm' : 'Chưa bắt đầu'}</p>
        
        {status === 'completed' && score !== null && (
          <p>
            <strong>Điểm số:</strong> {score}/{totalQuestions} ({Math.round((score / totalQuestions) * 100)}%)
          </p>
        )}
      </div>
      <div className="quiz-card-footer">
        <button className={`btn primary ${status}`} onClick={handleAction}>
          {buttonText}
        </button>
      </div>
    </div>
  );
}
