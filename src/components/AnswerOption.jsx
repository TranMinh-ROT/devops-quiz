import React from 'react';
import classNames from 'classnames';

export default function AnswerOption({ 
  option, 
  type, 
  isSelected, 
  isConfirmed, 
  isCorrectOption, 
  onToggle 
}) {
  const isCheckbox = type === 'multiple';
  
  // Determine styles after confirmation
  const showCorrect = isConfirmed && isCorrectOption;
  const showIncorrect = isConfirmed && isSelected && !isCorrectOption;
  
  const wrapperClass = classNames('answer-option', {
    'selected': isSelected && !isConfirmed,
    'correct': showCorrect,
    'incorrect': showIncorrect,
    'locked': isConfirmed
  });

  return (
    <label className={wrapperClass}>
      <div className="option-control">
        <input 
          type={isCheckbox ? "checkbox" : "radio"}
          checked={isSelected}
          onChange={() => !isConfirmed && onToggle(option.id)}
          disabled={isConfirmed}
        />
        <span className="option-letter">{option.id}.</span>
      </div>
      <div className="option-content">
        {option.textEnglish && <p className="text-en">{option.textEnglish}</p>}
        {option.textVietnamese && <p className="text-vi">{option.textVietnamese}</p>}
      </div>
    </label>
  );
}
