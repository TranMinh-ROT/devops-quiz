import React from 'react';

export default function ExplanationPanel({ question, userAnswers, isCorrect }) {
  const { 
    correctAnswers, 
    explanationVietnamese, 
    optionExplanationsVietnamese 
  } = question;

  const userSelectedStr = userAnswers.join(', ') || 'Chưa chọn';
  const correctStr = correctAnswers.join(', ');

  return (
    <div className="explanation-panel">
      <h3 className="section-title">Kết quả</h3>
      <div className="result-summary">
        <p><strong>Đáp án bạn chọn:</strong> {userSelectedStr}</p>
        <p><strong>Đáp án đúng:</strong> {correctStr}</p>
        <p>
          <strong>Đánh giá:</strong> 
          <span className={isCorrect ? 'text-green font-bold' : 'text-red font-bold'}>
            {isCorrect ? ' Chính xác' : ' Chưa chính xác'}
          </span>
        </p>
      </div>

      {explanationVietnamese && (
        <div className="general-explanation">
          <h3 className="section-title">Giải thích chung</h3>
          <p>{explanationVietnamese}</p>
        </div>
      )}

      <div className="option-explanations">
        <h3 className="section-title">Giải thích từng đáp án</h3>
        {question.options.map(opt => {
          const optExp = optionExplanationsVietnamese?.[opt.id]?.explanation;
          const isTrueAnswer = correctAnswers.includes(opt.id);
          
          return (
            <div key={opt.id} className={`opt-exp-item ${isTrueAnswer ? 'is-correct' : 'is-incorrect'}`}>
              <div className="opt-exp-header">
                <strong>Đáp án {opt.id}</strong> - 
                <span className={isTrueAnswer ? 'text-green' : 'text-red'}>
                  {isTrueAnswer ? ' Đáp án đúng' : ' Đáp án sai'}
                </span>
              </div>
              <div className="opt-exp-body">
                {optExp ? <p>{optExp}</p> : <p className="text-muted">Chưa có giải thích tiếng Việt cho đáp án này.</p>}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
