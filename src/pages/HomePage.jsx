import React, { useState, useEffect } from 'react';
import quizzes from '../data/quizzes.js';
import QuizCard from '../components/QuizCard';
import { clearAllStorage, loadFromStorage } from '../utils/storageUtils';

export default function HomePage() {
  const [stats, setStats] = useState({
    completedQuizzes: 0,
    totalCorrect: 0,
    totalIncorrect: 0,
    totalBookmarks: 0
  });

  useEffect(() => {
    let completedCount = 0;
    let correct = 0;
    let incorrect = 0;
    let bookmarks = 0;

    quizzes.forEach(quiz => {
      const state = loadFromStorage(`quiz_${quiz.id}`, null);
      if (state) {
        if (state.status === 'completed') {
          completedCount++;
        }
        if (state.results) {
          Object.values(state.results).forEach(res => {
            if (res === 'correct') correct++;
            if (res === 'incorrect') incorrect++;
          });
        }
        if (state.bookmarks) {
          Object.values(state.bookmarks).forEach(bk => {
            if (bk) bookmarks++;
          });
        }
      }
    });

    setStats({
      completedQuizzes: completedCount,
      totalCorrect: correct,
      totalIncorrect: incorrect,
      totalBookmarks: bookmarks
    });
  }, []);

  const handleClearAll = () => {
    if (window.confirm("Bạn có chắc chắn muốn xóa toàn bộ tiến độ học tập? Thao tác này không thể hoàn tác.")) {
      clearAllStorage();
      window.location.reload();
    }
  };

  return (
    <div className="home-page">
      <div className="hero-section">
        <p className="description">
          Chào mừng bạn đến với hệ thống luyện tập DevOps song ngữ. 
          Website cung cấp các đề luyện tập sát với thực tế, giúp bạn củng cố kiến thức và chuẩn bị tốt nhất cho kỳ thi chứng chỉ AWS.
        </p>
        
        <div className="stats-container">
          <div className="stat-box">
            <span className="stat-value">{stats.completedQuizzes}/{quizzes.length}</span>
            <span className="stat-label">Đề đã làm</span>
          </div>
          <div className="stat-box">
            <span className="stat-value text-green">{stats.totalCorrect}</span>
            <span className="stat-label">Câu đúng</span>
          </div>
          <div className="stat-box">
            <span className="stat-value text-red">{stats.totalIncorrect}</span>
            <span className="stat-label">Câu sai</span>
          </div>
          <div className="stat-box">
            <span className="stat-value text-yellow">{stats.totalBookmarks}</span>
            <span className="stat-label">Đã đánh dấu</span>
          </div>
        </div>
        
        <button className="btn danger clear-all-btn" onClick={handleClearAll}>
          Xóa toàn bộ tiến độ
        </button>
      </div>

      <h2 className="section-title">Danh sách đề thi</h2>
      <div className="quiz-grid">
        {quizzes.map(quiz => (
          <QuizCard key={quiz.id} quiz={quiz} />
        ))}
      </div>
    </div>
  );
}
