import React from 'react';
import { HashRouter, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import QuizPage from './pages/QuizPage';
import ResultPage from './pages/ResultPage';
import ReviewPage from './pages/ReviewPage';

function App() {
  return (
    <HashRouter>
      <div className="app-container">
        <header className="app-header">
          <h1>DevOps Quiz Practice</h1>
        </header>
        <main className="app-main">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/quiz/:quizId" element={<QuizPage />} />
            <Route path="/result/:quizId" element={<ResultPage />} />
            <Route path="/review/:quizId" element={<ReviewPage />} />
          </Routes>
        </main>
      </div>
    </HashRouter>
  );
}

export default App;
