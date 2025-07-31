import React, { useEffect } from 'react';

const ToastNotification = ({ message, type = 'info', duration = 3000, onClose }) => {
  useEffect(() => {
    if (!message) return;
    const timer = setTimeout(() => {
      onClose();
    }, duration);
    return () => clearTimeout(timer);
  }, [message, duration, onClose]);

  if (!message) return null;

  const bgColor =
    type === 'error' ? 'bg-red-500' :
    type === 'success' ? 'bg-green-500' :
    'bg-blue-500';

  return (
    <div className={`fixed bottom-4 right-4 px-4 py-2 rounded text-white shadow-lg ${bgColor}`}>
      {message}
    </div>
  );
};

export default ToastNotification;
