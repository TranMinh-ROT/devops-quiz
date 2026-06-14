import React, { useState, useEffect } from 'react';
import AnswerOption from './AnswerOption';
import ExplanationPanel from './ExplanationPanel';
import { Bookmark, BookmarkCheck } from 'lucide-react';

export default function QuestionCard({ 
  question, 
  userAnswers, 
  isConfirmed, 
  isCorrect, 
  isBookmarked,
  onSelectAnswer, 
  onConfirmAnswer,
  onToggleBookmark
}) {
  const [localAnswers, setLocalAnswers] = useState(userAnswers || []);

  useEffect(() => {
    setLocalAnswers(userAnswers || []);
  }, [userAnswers, question.id]);

  const handleToggleOption = (optId) => {
    if (isConfirmed) return;
    
    if (question.type === 'single') {
      setLocalAnswers([optId]);
      onSelectAnswer(question.id, [optId]);
    } else {
      setLocalAnswers(prev => {
        let newAnswers;
        if (prev.includes(optId)) {
          newAnswers = prev.filter(id => id !== optId);
        } else {
          // Prevent selecting more than required if known
          if (question.requiredAnswerCount && prev.length >= question.requiredAnswerCount) {
            return prev;
          }
          newAnswers = [...prev, optId];
        }
        onSelectAnswer(question.id, newAnswers);
        return newAnswers;
      });
    }
  };

  const handleConfirm = () => {
    if (isConfirmed) return;
    onConfirmAnswer(question.id, question.correctAnswers);
  };

  const canConfirm = question.type === 'single' 
    ? localAnswers.length === 1 
    : localAnswers.length === (question.requiredAnswerCount || 0);

  let instructionText = "Chọn 1 đáp án.";
  if (question.type === 'multiple') {
    if (question.requiredAnswerCount) {
      instructionText = `Chọn ${question.requiredAnswerCount} đáp án.`;
    } else {
      instructionText = "Chọn tất cả đáp án đúng.";
    }
  }

  return (
    <div className="question-card">
      <div className="question-header-actions">
        <button 
          className={`btn-bookmark ${isBookmarked ? 'active' : ''}`}
          onClick={() => onToggleBookmark(question.id)}
          title={isBookmarked ? "Bỏ đánh dấu" : "Đánh dấu câu hỏi"}
        >
          {isBookmarked ? <BookmarkCheck size={24} /> : <Bookmark size={24} />}
          <span>{isBookmarked ? 'Đã đánh dấu' : 'Đánh dấu'}</span>
        </button>
      </div>

      <div className="question-text-block">
        {question.questionEnglish && (
          <div className="q-en">
            <span className="lang-label">English</span>
            <p>{question.questionEnglish}</p>
          </div>
        )}
        {question.questionVietnamese && (
          <div className="q-vi mt-3">
            <span className="lang-label">Tiếng Việt</span>
            <p>{question.questionVietnamese}</p>
          </div>
        )}
      </div>

      <div className="instruction-text">
        <p>{instructionText}</p>
      </div>

      <div className="options-list">
        {question.options.map(opt => (
          <AnswerOption 
            key={opt.id}
            option={opt}
            type={question.type}
            isSelected={localAnswers.includes(opt.id)}
            isConfirmed={isConfirmed}
            isCorrectOption={question.correctAnswers.includes(opt.id)}
            onToggle={handleToggleOption}
          />
        ))}
      </div>

      {!isConfirmed && (
        <div className="confirm-action">
          {question.type === 'multiple' && question.requiredAnswerCount && localAnswers.length === question.requiredAnswerCount && (
            <p className="limit-reached-msg">Đã chọn đủ số lượng đáp án yêu cầu.</p>
          )}
          <button 
            className="btn primary" 
            onClick={handleConfirm}
            disabled={!canConfirm}
          >
            Xác nhận đáp án
          </button>
        </div>
      )}

      {isConfirmed && (
        <ExplanationPanel 
          question={question} 
          userAnswers={localAnswers} 
          isCorrect={isCorrect} 
        />
      )}
    </div>
  );
}
