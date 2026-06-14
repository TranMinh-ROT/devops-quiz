// src/utils/answerUtils.js

export function checkAnswer(userAnswers, correctAnswers) {
  if (!userAnswers || !correctAnswers) return false;
  
  // Remove duplicates, normalize to uppercase, and sort
  const uSet = Array.from(new Set(userAnswers.map(a => String(a).trim().toUpperCase()))).sort();
  const cSet = Array.from(new Set(correctAnswers.map(a => String(a).trim().toUpperCase()))).sort();

  if (uSet.length !== cSet.length) return false;

  for (let i = 0; i < uSet.length; i++) {
    if (uSet[i] !== cSet[i]) return false;
  }

  return true;
}
