import React, { useState } from 'react';
import { fetchMeetingPrep } from '../../utils/api';

const MeetingCard = ({ event }) => {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFetchSummary = async () => {
    if (!event.id && !event._id) {
      setSummary({ purpose: 'No description provided.' });
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const prepSummary = await fetchMeetingPrep(event.id || event._id);
      setSummary(prepSummary);
    } catch (err) {
      setError('Failed to fetch meeting summary.');
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    handleFetchSummary();
  }, [event.id, event._id]);

  const formatTime = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="border rounded-lg p-4 mb-4 shadow bg-white">
      <div className="flex justify-between items-center mb-2">
        <div className="font-semibold text-lg">{event.title || 'Untitled Meeting'}</div>
        <div className="text-sm text-gray-600">{formatTime(event.start)} - {formatTime(event.end)}</div>
      </div>
      {event.meetingLink && (
        <div className="mb-2">
          <a
            href={event.meetingLink}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:underline break-all"
            title="Join Meeting"
          >
            Join Meeting
          </a>
        </div>
      )}
      {loading && <div className="text-gray-500">Generating summary...</div>}
      {error && <div className="text-red-600">{error}</div>}
      {summary && summary.summaryPoints && Array.isArray(summary.summaryPoints) ? (
        <div className="text-gray-700 text-sm whitespace-pre-line ml-5">
          {summary.summaryPoints.map((point, idx) => (
            <div key={idx}>{point}</div>
          ))}
        </div>
      ) : summary && (
        <div className="text-gray-700 text-sm whitespace-pre-line">
          {summary.purpose && <div><strong>Purpose:</strong> {summary.purpose}</div>}
          {summary.background && <div><strong>Background:</strong> {summary.background}</div>}
          {summary.keyPoints && <div><strong>Key Points:</strong> {summary.keyPoints}</div>}
          {summary.actionItems && <div><strong>Action Items:</strong> {summary.actionItems}</div>}
          {summary.stakeholders && <div><strong>Stakeholders:</strong> {summary.stakeholders}</div>}
        </div>
      )}
      {!loading && !summary && (
        <div className="text-gray-500 italic">No meeting description provided.</div>
      )}
      <button
        onClick={handleFetchSummary}
        disabled={loading}
        className="mt-3 px-3 py-1 bg-purple-600 text-white rounded hover:bg-purple-700 disabled:opacity-50"
        title="Regenerate Summary"
      >
        Regenerate Summary
      </button>
    </div>
  );
};

export default MeetingCard;
