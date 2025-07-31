import { useAuth } from '../hooks/useAuth';

const API_BASE = 'https://www.googleapis.com/calendar/v3/calendars/primary/events';

async function authorizedFetch(url, options = {}) {
  // Since this is a utility function outside React components, we cannot use the hook directly.
  // Instead, we will access the token from localStorage or a global variable set by useAuth.
  // Alternatively, we can export a function to set the token here.
  // For now, get token from localStorage (assuming useAuth stores token there).
  const token = localStorage.getItem('token');
  if (!token) {
    throw new Error('No auth token available');
  }
  const headers = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
    ...options.headers,
  };
  const response = await fetch(url, { ...options, headers });
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error.message || 'Google Calendar API error');
  }
  return response.json();
}

export async function listEvents(timeMin, timeMax) {
  const url = new URL(API_BASE);
  url.searchParams.append('timeMin', timeMin.toISOString());
  url.searchParams.append('timeMax', timeMax.toISOString());
  url.searchParams.append('singleEvents', 'true');
  url.searchParams.append('orderBy', 'startTime');
  return authorizedFetch(url.toString());
}

export async function createEvent(event) {
  // event should include extendedProperties.private with meetingLink and meetingDescription
  return authorizedFetch(API_BASE, {
    method: 'POST',
    body: JSON.stringify(event),
  });
}

export async function updateEvent(eventId, event) {
  const url = `${API_BASE}/${eventId}`;
  return authorizedFetch(url, {
    method: 'PUT',
    body: JSON.stringify(event),
  });
}

// Added function to fetch full event details by event ID
export async function getEvent(eventId) {
  const url = `${API_BASE}/${eventId}`;
  return authorizedFetch(url);
}
