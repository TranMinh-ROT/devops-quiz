import React from 'react';

export default function FilterBar({ currentFilter, onFilterChange }) {
  const filters = [
    { id: 'all', label: 'Tất cả' },
    { id: 'unanswered', label: 'Chưa trả lời' },
    { id: 'answered', label: 'Đã chọn đáp án' },
    { id: 'confirmed', label: 'Đã xác nhận' },
    { id: 'correct', label: 'Trả lời đúng' },
    { id: 'incorrect', label: 'Trả lời sai' },
    { id: 'bookmarked', label: 'Đã đánh dấu' }
  ];

  return (
    <div className="filter-bar">
      <label>Lọc câu hỏi: </label>
      <select 
        value={currentFilter} 
        onChange={(e) => onFilterChange(e.target.value)}
      >
        {filters.map(f => (
          <option key={f.id} value={f.id}>{f.label}</option>
        ))}
      </select>
    </div>
  );
}
