import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { 
  fetchEmails, 
  fetchEmailDrafts, 
  fetchEmailReminders, 
  fetchEmailStats, 
  syncEmails, 
  generateEmailDraft, 
  approveDraft, 
  createEmailReminder 
} from '../../utils/api';
import EmailList from './EmailList';
import EmailDrafts from './EmailDrafts';
import EmailReminders from './EmailReminders';
import EmailStats from './EmailStats';

const EmailDashboard = () => {
  const { token, isAuthenticated } = useAuth();
  const [activeTab, setActiveTab] = useState('inbox');
  const [emails, setEmails] = useState([]);
  const [drafts, setDrafts] = useState([]);
  const [reminders, setReminders] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  useEffect(() => {
    fetchEmailData();
    const interval = setInterval(fetchEmailData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchEmailData = async () => {
    try {
      const userId = 'current_user'; // In production, get from auth

      // Fetch emails using centralized API
      const emailData = await fetchEmails(userId, 50);
      if (emailData.status === 'success') {
        setEmails(emailData.emails || []);
      }

      // Fetch drafts using centralized API
      const draftData = await fetchEmailDrafts(userId);
      if (draftData.status === 'success') {
        setDrafts(draftData.drafts || []);
      }

      // Fetch reminders using centralized API
      const reminderData = await fetchEmailReminders(userId);
      if (reminderData.status === 'success') {
        setReminders(reminderData.reminders || []);
      }

      // Fetch stats using centralized API
      const statsData = await fetchEmailStats(userId);
      if (statsData.status === 'success') {
        setStats(statsData.stats);
      }

      setLoading(false);
    } catch (error) {
      console.error('Error fetching email data:', error);
      setLoading(false);
    }
  };

  const handleSyncEmails = async () => {
    try {
      setLoading(true);
      const data = await syncEmails(token, 50);
      if (data.status === 'success') {
        alert('Email sync started! Check back in a few moments.');
        setTimeout(fetchEmailData, 5000); // Refresh after 5 seconds
      }
    } catch (error) {
      console.error('Error syncing emails:', error);
      alert('Failed to sync emails');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateDraft = async (emailId) => {
    try {
      const data = await generateEmailDraft(emailId, token);
      if (data.status === 'success') {
        alert('Draft generation started! Check the drafts tab in a moment.');
        setTimeout(fetchEmailData, 3000);
      }
    } catch (error) {
      console.error('Error generating draft:', error);
      alert('Failed to generate draft');
    }
  };

  const handleApproveDraft = async (draftId, approved, modifiedContent = null) => {
    try {
      const data = await approveDraft(draftId, token, approved, modifiedContent);
      if (data.status === 'success') {
        alert(approved ? 'Email sent successfully!' : 'Draft rejected');
        fetchEmailData();
      }
    } catch (error) {
      console.error('Error processing draft:', error);
      alert('Failed to process draft');
    }
  };

  const handleCreateReminder = async (emailId, hours = 24) => {
    try {
      const data = await createEmailReminder(emailId, token, hours);
      if (data.status === 'success') {
        alert('Reminder created successfully!');
        fetchEmailData();
      }
    } catch (error) {
      console.error('Error creating reminder:', error);
      alert('Failed to create reminder');
    }
  };

  if (loading && !emails.length) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Email Management</h1>
            <p className="text-gray-600">AI-powered email processing and management</p>
          </div>
          <button
            onClick={handleSyncEmails}
            disabled={loading}
            className="bg-purple-600 hover:bg-purple-700 disabled:bg-purple-400 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center space-x-2"
          >
            {loading && (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            )}
            <span>Sync Emails</span>
          </button>
        </div>
      </div>

      {/* Stats Overview */}
      {stats && <EmailStats stats={stats} />}

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'inbox', name: 'Inbox', count: emails.length },
            { id: 'drafts', name: 'Drafts', count: drafts.length },
            { id: 'reminders', name: 'Reminders', count: reminders.length }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                activeTab === tab.id
                  ? 'border-purple-500 text-purple-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <span>{tab.name}</span>
              {tab.count > 0 && (
                <span className={`px-2 py-1 rounded-full text-xs ${
                  activeTab === tab.id
                    ? 'bg-purple-100 text-purple-600'
                    : 'bg-gray-100 text-gray-600'
                }`}>
                  {tab.count}
                </span>
              )}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'inbox' && (
        <EmailList
          emails={emails}
          onGenerateDraft={handleGenerateDraft}
          onCreateReminder={handleCreateReminder}
          onRefresh={fetchEmailData}
        />
      )}

      {activeTab === 'drafts' && (
        <EmailDrafts
          drafts={drafts}
          onApproveDraft={handleApproveDraft}
          onRefresh={fetchEmailData}
        />
      )}

      {activeTab === 'reminders' && (
        <EmailReminders
          reminders={reminders}
          onRefresh={fetchEmailData}
        />
      )}
    </div>
  );
};

export default EmailDashboard;
