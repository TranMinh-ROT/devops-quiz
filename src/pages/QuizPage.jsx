import React, { useState, useEffect, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import quizzes from '../data/quizzes.js';
import { useQuizProgress } from '../hooks/useQuizProgress';
import QuestionCard from '../components/QuestionCard';
import QuestionNavigator from '../components/QuestionNavigator';
import ProgressBar from '../components/ProgressBar';
import QuizTimer from '../components/QuizTimer';
import FilterBar from '../components/FilterBar';
import ConfirmDialog from '../components/ConfirmDialog';

export default function QuizPage() {
  const { quizId } = useParams();
  const navigate = useNavigate();
  const quiz = useMemo(() => quizzes.find(q => q.id === quizId), [quizId]);
  
  const {
    state: progress,
    startQuiz,
    selectAnswer,
    confirmAnswer,
    toggleBookmark,
    submitQuiz
  } = useQuizProgress(quizId);

  const [currentIndex, setCurrentIndex] = useState(0);
  const [filter, setFilter] = useState('all');
  const [showSubmitConfirm, setShowSubmitConfirm] = useState(false);

  useEffect(() => {
    if (!quiz) {
      navigate('/');
      return;
    }
    if (progress.status === 'not-started') {
      startQuiz();
    }
  }, [quiz, progress.status, navigate, startQuiz]);

  if (!quiz) return null;

  const totalQuestions = quiz.questions.length;
  const currentQuestion = quiz.questions[currentIndex];

  const handleNext = () => {
    if (currentIndex < totalQuestions - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  };

  const handlePrev = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  };

  const handleSubmitRequest = () => {
    setShowSubmitConfirm(true);
  };

  const handleConfirmSubmit = () => {
    setShowSubmitConfirm(false);
    submitQuiz();
    navigate(`/result/${quizId}`);
  };

  const getFilteredIndices = () => {
    const indices = [];
    quiz.questions.forEach((q, idx) => {
      const qId = q.id;
      let match = false;
      switch (filter) {
        case 'all': match = true; break;
        case 'unanswered': match = (!progress.answers[qId] || progress.answers[qId].length === 0); break;
        case 'answered': match = (progress.answers[qId] && progress.answers[qId].length > 0 && !progress.confirmed[qId]); break;
        case 'confirmed': match = !!progress.confirmed[qId]; break;
        case 'correct': match = progress.results[qId] === 'correct'; break;
        case 'incorrect': match = progress.results[qId] === 'incorrect'; break;
        case 'bookmarked': match = !!progress.bookmarks[qId]; break;
        default: match = true;
      }
      if (match) indices.push(idx);
    });
    return indices;
  };

  const filteredIndices = getFilteredIndices();
  
  // Calculate unanswered count for the confirmation dialog
  const unansweredCount = totalQuestions - Object.keys(progress.answers).length;

  return (
    <div className="quiz-page">
      <div className="quiz-sidebar">
        <div className="sidebar-header">
          <h2>{quiz.title}</h2>
          <QuizTimer startTime={progress.startTime} status={progress.status} />
        </div>
        
        <FilterBar currentFilter={filter} onFilterChange={setFilter} />
        
        <QuestionNavigator 
          questions={quiz.questions}
          currentIndex={currentIndex}
          answers={progress.answers}
          confirmed={progress.confirmed}
          results={progress.results}
          bookmarks={progress.bookmarks}
          onNavigate={setCurrentIndex}
        />
        
        <button className="btn primary submit-btn-sidebar" onClick={handleSubmitRequest}>
          Nộp bài
        </button>
      </div>

      <div className="quiz-content">
        <div className="quiz-content-header">
          <ProgressBar current={currentIndex + 1} total={totalQuestions} />
        </div>
        
        {currentQuestion && (
          <QuestionCard
            key={currentQuestion.id} // forces remount on question change if needed, but we manage state via progress
            question={currentQuestion}
            userAnswers={progress.answers[currentQuestion.id] || []}
            isConfirmed={!!progress.confirmed[currentQuestion.id]}
            isCorrect={progress.results[currentQuestion.id] === 'correct'}
            isBookmarked={!!progress.bookmarks[currentQuestion.id]}
            onSelectAnswer={selectAnswer}
            onConfirmAnswer={confirmAnswer}
            onToggleBookmark={toggleBookmark}
          />
        )}
        
        <div className="quiz-navigation-controls">
          <button 
            className="btn outline" 
            onClick={handlePrev} 
            disabled={currentIndex === 0}
          >
            Câu trước
          </button>
          
          <button 
            className="btn outline" 
            onClick={handleNext} 
            disabled={currentIndex === totalQuestions - 1}
          >
            Câu tiếp theo
          </button>
        </div>
      </div>

      {showSubmitConfirm && (
        <ConfirmDialog 
          title="Nộp bài"
          message={`Bạn có chắc chắn muốn nộp bài? Còn ${unansweredCount} câu hỏi chưa được trả lời.`}
          onConfirm={handleConfirmSubmit}
          onCancel={() => setShowSubmitConfirm(false)}
        />
      )}
    </div>
  );
}
