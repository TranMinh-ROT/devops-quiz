import React from 'react';

export default function ConfirmDialog({ title, message, onConfirm, onCancel, confirmText = "Xác nhận", cancelText = "Hủy" }) {
  return (
    <div className="modal-backdrop">
      <div className="modal-content">
        <h3 className="modal-title">{title}</h3>
        <p className="modal-message">{message}</p>
        <div className="modal-actions">
          <button className="btn outline" onClick={onCancel}>{cancelText}</button>
          <button className="btn primary" onClick={onConfirm}>{confirmText}</button>
        </div>
      </div>
    </div>
  );
}
