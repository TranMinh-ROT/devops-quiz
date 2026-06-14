import React, { useState, useEffect } from 'react';
import { Clock } from 'lucide-react';

export default function QuizTimer({ startTime, status }) {
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    if (!startTime || status === 'completed') return;

    const interval = setInterval(() => {
      setElapsed(Math.floor((Date.now() - startTime) / 1000));
    }, 1000);

    return () => clearInterval(interval);
  }, [startTime, status]);

  const formatTime = (seconds) => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    
    if (h > 0) {
      return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    }
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  return (
    <div className="quiz-timer">
      <Clock size={20} />
      <span>{formatTime(elapsed)}</span>
    </div>
  );
}
