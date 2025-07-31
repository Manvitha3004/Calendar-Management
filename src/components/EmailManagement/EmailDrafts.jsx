import React, { useState } from 'react';

const EmailDrafts = ({ drafts, onApproveDraft, onRefresh }) => {
  const [editingDraft, setEditingDraft] = useState(null);
  const [editedContent, setEditedContent] = useState('');

  const handleEditDraft = (draft) => {
    setEditingDraft(draft._id);
    setEditedContent(draft.draft_content);
  };

  const handleSaveEdit = (draftId) => {
    onApproveDraft(draftId, true, editedContent);
    setEditingDraft(null);
    setEditedContent('');
  };

  const handleCancelEdit = () => {
    setEditingDraft(null);
    setEditedContent('');
  };

  const formatDate = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'approved':
        return 'bg-blue-100 text-blue-800';
      case 'sent':
        return 'bg-green-100 text-green-800';
      case 'rejected':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">Email Drafts</h2>
          <button
            onClick={onRefresh}
            className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            Refresh
          </button>
        </div>
      </div>

      {/* Drafts List */}
      <div className="divide-y divide-gray-200">
        {drafts.length === 0 ? (
          <div className="px-6 py-8 text-center text-gray-500">
            No drafts available
          </div>
        ) : (
          drafts.map((draft) => (
            <div key={draft._id} className="px-6 py-4">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="font-medium text-gray-900">
                      Re: {draft.email?.subject || 'Unknown Subject'}
                    </h3>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(draft.status)}`}>
                      {draft.status}
                    </span>
                  </div>
                  
                  <div className="text-sm text-gray-600 space-y-1">
                    <div>Original from: {draft.email?.sender}</div>
                    <div>Generated: {formatDate(draft.generated_at)}</div>
                    <div>AI Confidence: {Math.round((draft.ai_confidence || 0) * 100)}%</div>
                  </div>
                </div>
                
                {draft.status === 'pending' && (
                  <div className="flex items-center space-x-2 ml-4">
                    <button
                      onClick={() => handleEditDraft(draft)}
                      className="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded text-sm font-medium transition-colors"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => onApproveDraft(draft._id, true)}
                      className="bg-green-500 hover:bg-green-600 text-white px-3 py-1 rounded text-sm font-medium transition-colors"
                    >
                      Send
                    </button>
                    <button
                      onClick={() => onApproveDraft(draft._id, false)}
                      className="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded text-sm font-medium transition-colors"
                    >
                      Reject
                    </button>
                  </div>
                )}
              </div>

              {/* Draft Content */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 mb-2">Draft Content:</h4>
                
                {editingDraft === draft._id ? (
                  <div className="space-y-3">
                    <textarea
                      value={editedContent}
                      onChange={(e) => setEditedContent(e.target.value)}
                      className="w-full h-40 p-3 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                      placeholder="Edit your draft here..."
                    />
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handleSaveEdit(draft._id)}
                        className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded text-sm font-medium transition-colors"
                      >
                        Save & Send
                      </button>
                      <button
                        onClick={handleCancelEdit}
                        className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded text-sm font-medium transition-colors"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="text-sm text-gray-700 whitespace-pre-wrap">
                    {draft.draft_content}
                  </div>
                )}
              </div>

              {/* Original Email Context */}
              {draft.email && (
                <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                  <h4 className="font-medium text-blue-900 mb-2">Original Email:</h4>
                  <div className="text-sm text-blue-800">
                    <div className="font-medium">{draft.email.subject}</div>
                    <div className="mt-1 text-blue-600">
                      {draft.email.snippet}
                    </div>
                  </div>
                </div>
              )}

              {/* Error Message */}
              {draft.error && (
                <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700">
                  Error: {draft.error}
                </div>
              )}
            </div>
          ))
        )}
      </div>
      
      {/* Footer */}
      <div className="px-6 py-3 bg-gray-50 border-t border-gray-200 text-sm text-gray-600">
        {drafts.length} draft{drafts.length !== 1 ? 's' : ''} total
      </div>
    </div>
  );
};

export default EmailDrafts;
