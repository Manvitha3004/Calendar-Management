import React from 'react';

const EmailReminders = ({ reminders, onRefresh }) => {
  const formatDate = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const getTimeUntilReminder = (reminderTime) => {
    const now = new Date();
    const reminder = new Date(reminderTime);
    const diffMs = reminder - now;
    
    if (diffMs < 0) return 'Overdue';
    
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffDays > 0) return `${diffDays} day${diffDays !== 1 ? 's' : ''}`;
    if (diffHours > 0) return `${diffHours} hour${diffHours !== 1 ? 's' : ''}`;
    
    const diffMins = Math.floor(diffMs / (1000 * 60));
    return `${diffMins} minute${diffMins !== 1 ? 's' : ''}`;
  };

  const isOverdue = (reminderTime) => {
    return new Date(reminderTime) < new Date();
  };

  const completeReminder = async (reminderId) => {
    try {
      const response = await fetch(`/api/gmail/reminders/${reminderId}/complete`, {
        method: 'POST'
      });
      const data = await response.json();
      if (data.status === 'success') {
        onRefresh();
      }
    } catch (error) {
      console.error('Error completing reminder:', error);
      alert('Failed to complete reminder');
    }
  };

  return (
    <div className="bg-white rounded-lg shadow">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">Email Reminders</h2>
          <button
            onClick={onRefresh}
            className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            Refresh
          </button>
        </div>
      </div>

      {/* Reminders List */}
      <div className="divide-y divide-gray-200">
        {reminders.length === 0 ? (
          <div className="px-6 py-8 text-center text-gray-500">
            No active reminders
          </div>
        ) : (
          reminders.map((reminder) => (
            <div key={reminder._id} className="px-6 py-4 hover:bg-gray-50">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <span className={`text-lg ${isOverdue(reminder.reminder_time) ? '🔴' : '⏰'}`}>
                      {isOverdue(reminder.reminder_time) ? '🔴' : '⏰'}
                    </span>
                    <div>
                      <h3 className="font-medium text-gray-900">
                        Reply to: {reminder.email?.subject || 'Unknown Email'}
                      </h3>
                      <div className="text-sm text-gray-600">
                        From: {reminder.email?.sender}
                      </div>
                    </div>
                  </div>
                  
                  <div className="ml-8 space-y-1 text-sm text-gray-600">
                    <div>
                      Reminder set for: {formatDate(reminder.reminder_time)}
                    </div>
                    <div>
                      Created: {formatDate(reminder.created_at)}
                    </div>
                    <div className={`font-medium ${
                      isOverdue(reminder.reminder_time) ? 'text-red-600' : 'text-blue-600'
                    }`}>
                      {isOverdue(reminder.reminder_time) ? 'Overdue' : `Due in ${getTimeUntilReminder(reminder.reminder_time)}`}
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2 ml-4">
                  <button
                    onClick={() => completeReminder(reminder._id)}
                    className="bg-green-500 hover:bg-green-600 text-white px-3 py-1 rounded text-sm font-medium transition-colors"
                  >
                    Mark Complete
                  </button>
                  <button
                    onClick={() => {
                      // Navigate to email or open draft
                      console.log('Open email:', reminder.email_id);
                    }}
                    className="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded text-sm font-medium transition-colors"
                  >
                    View Email
                  </button>
                </div>
              </div>

              {/* Email Preview */}
              {reminder.email && (
                <div className="mt-3 ml-8 p-3 bg-gray-50 rounded-lg">
                  <div className="text-sm text-gray-700">
                    <div className="font-medium mb-1">Email Preview:</div>
                    <div className="text-gray-600">
                      {reminder.email.snippet || 'No preview available'}
                    </div>
                  </div>
                </div>
              )}

              {/* Calendar Event Link */}
              {reminder.calendar_event_id && (
                <div className="mt-2 ml-8 text-sm text-blue-600">
                  📅 Calendar reminder created
                </div>
              )}
            </div>
          ))
        )}
      </div>
      
      {/* Footer */}
      <div className="px-6 py-3 bg-gray-50 border-t border-gray-200">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <span>{reminders.length} active reminder{reminders.length !== 1 ? 's' : ''}</span>
          <span>
            {reminders.filter(r => isOverdue(r.reminder_time)).length} overdue
          </span>
        </div>
      </div>
    </div>
  );
};

export default EmailReminders;
