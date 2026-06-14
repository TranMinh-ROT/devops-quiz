import React from 'react';

export default function ProgressBar({ current, total }) {
  const percentage = Math.round((current / total) * 100);
  
  return (
    <div className="progress-container">
      <div className="progress-info">
        <span className="progress-text">Câu {current} / {total}</span>
        <span className="progress-percent">{percentage}%</span>
      </div>
      <div className="progress-bar-bg">
        <div className="progress-bar-fill" style={{ width: `${percentage}%` }}></div>
      </div>
    </div>
  );
}
