import React from 'react';
import classNames from 'classnames';

export default function QuestionNavigator({ 
  questions, 
  currentIndex, 
  answers, 
  confirmed, 
  results, 
  bookmarks,
  onNavigate 
}) {
  return (
    <div className="question-navigator">
      <h3 className="navigator-title">Danh sách câu hỏi</h3>
      <div className="navigator-grid">
        {questions.map((q, idx) => {
          const qId = q.id;
          const isCurrent = idx === currentIndex;
          const isAnswered = answers[qId] && answers[qId].length > 0;
          const isConfirmed = confirmed[qId];
          const isCorrect = results[qId] === 'correct';
          const isIncorrect = results[qId] === 'incorrect';
          const isBookmarked = bookmarks[qId];

          const btnClass = classNames('nav-btn', {
            'current': isCurrent,
            'answered': isAnswered && !isConfirmed,
            'correct': isConfirmed && isCorrect,
            'incorrect': isConfirmed && isIncorrect,
            'bookmarked': isBookmarked
          });

          return (
            <button 
              key={qId}
              className={btnClass}
              onClick={() => onNavigate(idx)}
              title={`Câu ${idx + 1}${isBookmarked ? ' (Đã đánh dấu)' : ''}`}
            >
              <span className="nav-number">{idx + 1}</span>
              {isBookmarked && <span className="nav-bookmark-indicator" />}
            </button>
          );
        })}
      </div>
      <div className="navigator-legend">
        <div className="legend-item"><span className="nav-btn current"></span> Hiện tại</div>
        <div className="legend-item"><span className="nav-btn"></span> Chưa trả lời</div>
        <div className="legend-item"><span className="nav-btn answered"></span> Đã chọn</div>
        <div className="legend-item"><span className="nav-btn correct"></span> Đúng</div>
        <div className="legend-item"><span className="nav-btn incorrect"></span> Sai</div>
        <div className="legend-item"><span className="nav-btn bookmarked"></span> Đánh dấu</div>
      </div>
    </div>
  );
}
