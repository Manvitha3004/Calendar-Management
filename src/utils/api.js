const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:4000/api';

// Get auth token from localStorage
const getAuthToken = () => {
  return localStorage.getItem('auth_token') || localStorage.getItem('google_token');
};

// Create headers with authentication
const createHeaders = (includeAuth = true) => {
  const headers = {
    'Content-Type': 'application/json',
  };
  
  if (includeAuth) {
    const token = getAuthToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
  }
  
  return headers;
};

// Generic API call handler with error handling
const apiCall = async (url, options = {}) => {
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        ...createHeaders(),
        ...options.headers,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API call failed for ${url}:`, error);
    throw error;
  }
};

// Events API
export const fetchEvents = async () => {
  return apiCall(`${API_BASE_URL}/events`);
};

import { toLocalISOString, fromLocalISOString } from './timeUtils';

export const createEvent = async (eventData) => {
  try {
    // Convert times to UTC before sending to server
    const formattedData = {
      ...eventData,
      start: fromLocalISOString(eventData.start),
      end: fromLocalISOString(eventData.end),
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
    };

    const response = await fetch(`${API_BASE_URL}/events`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formattedData),
    });
    
    if (!response.ok) {
      throw new Error('Failed to create event');
    }
    
    const data = await response.json();
    // Convert times back to local time
    return {
      ...data,
      start: toLocalISOString(new Date(data.start)),
      end: toLocalISOString(new Date(data.end))
    };
  } catch (error) {
    console.error('Error creating event:', error);
    throw error;
  }
};

export const updateEvent = async (eventId, eventData) => {
  try {
    const response = await fetch(`${API_BASE_URL}/events/${eventId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(eventData),
    });
    if (!response.ok) {
      throw new Error('Failed to update event');
    }
    return await response.json();
  } catch (error) {
    console.error('Error updating event:', error);
    throw error;
  }
};

export const deleteEvent = async (eventId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/events/${eventId}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      throw new Error('Failed to delete event');
    }
    return await response.json();
  } catch (error) {
    console.error('Error deleting event:', error);
    throw error;
  }
};

export const fetchAgenda = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/agenda`);
    if (!response.ok) {
      throw new Error('Failed to fetch agenda');
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching agenda:', error);
    throw error;
  }
};

export const fetchMeetingPrep = async (eventId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/events/${eventId}/prep`);
    if (!response.ok) {
      throw new Error('Failed to fetch meeting prep');
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching meeting prep:', error);
    throw error;
  }
};

export const regenerateSummary = async (eventId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/events/${eventId}/regenerate-summary`, {
      method: 'POST',
    });
    if (!response.ok) {
      throw new Error('Failed to regenerate summary');
    }
    return await response.json();
  } catch (error) {
    console.error('Error regenerating summary:', error);
    throw error;
  }
};

// Email API functions
export const fetchEmails = async (userId, limit = 50) => {
  try {
    const response = await fetch(`${API_BASE_URL}/gmail/emails/list?user_id=${userId}&limit=${limit}`);
    if (!response.ok) {
      throw new Error('Failed to fetch emails');
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching emails:', error);
    throw error;
  }
};

export const fetchEmailDrafts = async (userId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/gmail/drafts?user_id=${userId}`);
    if (!response.ok) {
      throw new Error('Failed to fetch drafts');
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching drafts:', error);
    throw error;
  }
};

export const fetchEmailReminders = async (userId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/gmail/reminders?user_id=${userId}`);
    if (!response.ok) {
      throw new Error('Failed to fetch reminders');
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching reminders:', error);
    throw error;
  }
};

export const fetchEmailStats = async (userId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/gmail/stats?user_id=${userId}`);
    if (!response.ok) {
      throw new Error('Failed to fetch email stats');
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching email stats:', error);
    throw error;
  }
};

export const syncEmails = async (userToken, maxResults = 50) => {
  try {
    const response = await fetch(`${API_BASE_URL}/gmail/sync?user_token=${userToken}&max_results=${maxResults}`, {
      method: 'POST'
    });
    if (!response.ok) {
      throw new Error('Failed to sync emails');
    }
    return await response.json();
  } catch (error) {
    console.error('Error syncing emails:', error);
    throw error;
  }
};

export const generateEmailDraft = async (emailId, userToken) => {
  try {
    const response = await fetch(`${API_BASE_URL}/gmail/emails/${emailId}/draft?user_token=${userToken}`, {
      method: 'POST'
    });
    if (!response.ok) {
      throw new Error('Failed to generate draft');
    }
    return await response.json();
  } catch (error) {
    console.error('Error generating draft:', error);
    throw error;
  }
};

export const approveDraft = async (draftId, userToken, approved, modifiedContent = null) => {
  try {
    const response = await fetch(`${API_BASE_URL}/gmail/drafts/${draftId}/approve?user_token=${userToken}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        approved,
        modified_content: modifiedContent
      }),
    });
    if (!response.ok) {
      throw new Error('Failed to process draft');
    }
    return await response.json();
  } catch (error) {
    console.error('Error processing draft:', error);
    throw error;
  }
};

export const createEmailReminder = async (emailId, userToken, hours = 24) => {
  try {
    const response = await fetch(`${API_BASE_URL}/gmail/emails/${emailId}/reminder?user_token=${userToken}&reminder_hours=${hours}`, {
      method: 'POST'
    });
    if (!response.ok) {
      throw new Error('Failed to create reminder');
    }
    return await response.json();
  } catch (error) {
    console.error('Error creating reminder:', error);
    throw error;
  }
};
