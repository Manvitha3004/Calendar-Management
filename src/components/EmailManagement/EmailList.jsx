import React, { useState } from 'react';

const EmailList = ({ emails, onGenerateDraft, onCreateReminder, onRefresh }) => {
  const [selectedEmail, setSelectedEmail] = useState(null);
  const [filter, setFilter] = useState('all');

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'urgent':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'meeting':
        return '📅';
      case 'task':
        return '✅';
      case 'question':
        return '❓';
      case 'complaint':
        return '⚠️';
      default:
        return '📧';
    }
  };

  const filteredEmails = emails.filter(email => {
    if (filter === 'all') return true;
    if (filter === 'unread') return !email.is_read;
    if (filter === 'priority') return email.context?.priority === 'high' || email.context?.priority === 'urgent';
    return email.context?.category === filter;
  });

  const formatDate = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);

    if (diffHours < 1) return 'Just now';
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="bg-white rounded-lg shadow">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">Email Inbox</h2>
          <button
            onClick={onRefresh}
            className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            Refresh
          </button>
        </div>
        
        {/* Filters */}
        <div className="flex items-center space-x-4 mt-4">
          <div className="flex items-center space-x-2">
            <label className="text-sm font-medium text-gray-700">Filter:</label>
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="border border-gray-300 rounded-md px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="all">All</option>
              <option value="unread">Unread</option>
              <option value="priority">High Priority</option>
              <option value="meeting">Meetings</option>
              <option value="task">Tasks</option>
              <option value="question">Questions</option>
            </select>
          </div>
        </div>
      </div>

      {/* Email List */}
      <div className="divide-y divide-gray-200">
        {filteredEmails.length === 0 ? (
          <div className="px-6 py-8 text-center text-gray-500">
            No emails found
          </div>
        ) : (
          filteredEmails.map((email) => (
            <div
              key={email.message_id}
              className={`px-6 py-4 hover:bg-gray-50 cursor-pointer ${
                !email.is_read ? 'bg-blue-50' : ''
              }`}
              onClick={() => setSelectedEmail(selectedEmail === email.message_id ? null : email.message_id)}
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3">
                    <span className="text-lg">{getCategoryIcon(email.context?.category)}</span>
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <h3 className={`font-medium ${!email.is_read ? 'text-gray-900' : 'text-gray-700'}`}>
                          {email.subject}
                        </h3>
                        {!email.is_read && (
                          <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                        )}
                      </div>
                      <div className="flex items-center space-x-4 text-sm text-gray-600 mt-1">
                        <span>From: {email.sender}</span>
                        <span>{formatDate(email.timestamp)}</span>
                        {email.context?.priority && (
                          <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getPriorityColor(email.context.priority)}`}>
                            {email.context.priority}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  <div className="mt-2 text-sm text-gray-600">
                    {email.snippet}
                  </div>
                  
                  {/* Key Points */}
                  {email.context?.key_points && email.context.key_points.length > 0 && (
                    <div className="mt-2">
                      <div className="text-xs font-medium text-gray-700 mb-1">Key Points:</div>
                      <div className="flex flex-wrap gap-1">
                        {email.context.key_points.slice(0, 3).map((point, index) => (
                          <span
                            key={index}
                            className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded"
                          >
                            {point.length > 30 ? point.substring(0, 30) + '...' : point}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
                
                <div className="flex items-center space-x-2 ml-4">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onGenerateDraft(email.message_id);
                    }}
                    className="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded text-sm font-medium transition-colors"
                  >
                    Draft Reply
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onCreateReminder(email.message_id);
                    }}
                    className="bg-yellow-500 hover:bg-yellow-600 text-white px-3 py-1 rounded text-sm font-medium transition-colors"
                  >
                    Remind Me
                  </button>
                </div>
              </div>
              
              {/* Expanded Email Details */}
              {selectedEmail === email.message_id && (
                <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                  <div className="space-y-3">
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">Email Body:</h4>
                      <div className="text-sm text-gray-700 whitespace-pre-wrap max-h-40 overflow-y-auto">
                        {email.body}
                      </div>
                    </div>
                    
                    {email.context && (
                      <div>
                        <h4 className="font-medium text-gray-900 mb-2">AI Analysis:</h4>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                          <div>
                            <span className="font-medium">Sentiment:</span>
                            <span className={`ml-2 px-2 py-1 rounded text-xs ${
                              email.context.sentiment === 'positive' ? 'bg-green-100 text-green-800' :
                              email.context.sentiment === 'negative' ? 'bg-red-100 text-red-800' :
                              'bg-gray-100 text-gray-800'
                            }`}>
                              {email.context.sentiment}
                            </span>
                          </div>
                          <div>
                            <span className="font-medium">Category:</span>
                            <span className="ml-2">{email.context.category}</span>
                          </div>
                          <div>
                            <span className="font-medium">Priority:</span>
                            <span className={`ml-2 px-2 py-1 rounded text-xs ${getPriorityColor(email.context.priority)}`}>
                              {email.context.priority}
                            </span>
                          </div>
                        </div>
                        
                        {email.context.suggested_actions && email.context.suggested_actions.length > 0 && (
                          <div className="mt-3">
                            <span className="font-medium">Suggested Actions:</span>
                            <ul className="mt-1 list-disc list-inside text-sm text-gray-700">
                              {email.context.suggested_actions.map((action, index) => (
                                <li key={index}>{action}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>
      
      {/* Footer */}
      <div className="px-6 py-3 bg-gray-50 border-t border-gray-200 text-sm text-gray-600">
        Showing {filteredEmails.length} of {emails.length} emails
      </div>
    </div>
  );
};

export default EmailList;
