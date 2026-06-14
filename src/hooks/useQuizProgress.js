import { useState, useEffect, useCallback } from 'react';
import { saveToStorage, loadFromStorage } from '../utils/storageUtils';
import { checkAnswer } from '../utils/answerUtils';

export function useQuizProgress(quizId) {
  const getInitialState = () => {
    return loadFromStorage(`quiz_${quizId}`, {
      answers: {},
      confirmed: {},
      results: {},
      bookmarks: {},
      status: 'not-started', // 'not-started', 'in-progress', 'completed'
      score: null,
      startTime: null,
      endTime: null,
    });
  };

  const [state, setState] = useState(getInitialState);

  // Sync to local storage whenever state changes
  useEffect(() => {
    saveToStorage(`quiz_${quizId}`, state);
  }, [state, quizId]);

  const startQuiz = useCallback(() => {
    setState(prev => ({
      ...prev,
      status: 'in-progress',
      startTime: prev.startTime || Date.now(),
    }));
  }, []);

  const selectAnswer = useCallback((qId, answerArray) => {
    setState(prev => ({
      ...prev,
      answers: { ...prev.answers, [qId]: answerArray }
    }));
  }, []);

  const confirmAnswer = useCallback((qId, correctAnswers) => {
    setState(prev => {
      const userAnswers = prev.answers[qId] || [];
      const isCorrect = checkAnswer(userAnswers, correctAnswers);
      return {
        ...prev,
        confirmed: { ...prev.confirmed, [qId]: true },
        results: { ...prev.results, [qId]: isCorrect ? 'correct' : 'incorrect' }
      };
    });
  }, []);

  const toggleBookmark = useCallback((qId) => {
    setState(prev => ({
      ...prev,
      bookmarks: { ...prev.bookmarks, [qId]: !prev.bookmarks[qId] }
    }));
  }, []);

  const submitQuiz = useCallback(() => {
    setState(prev => {
      let correctCount = 0;
      for (const [qId, result] of Object.entries(prev.results)) {
        if (result === 'correct') correctCount++;
      }
      return {
        ...prev,
        status: 'completed',
        endTime: Date.now(),
        score: correctCount,
      };
    });
  }, []);

  const restartQuiz = useCallback(() => {
    const newState = {
      answers: {},
      confirmed: {},
      results: {},
      bookmarks: {},
      status: 'in-progress',
      score: null,
      startTime: Date.now(),
      endTime: null,
    };
    setState(newState);
    saveToStorage(`quiz_${quizId}`, newState);
  }, [quizId]);

  return {
    state,
    startQuiz,
    selectAnswer,
    confirmAnswer,
    toggleBookmark,
    submitQuiz,
    restartQuiz
  };
}
