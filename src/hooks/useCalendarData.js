import { useState, useEffect } from 'react';
import {
  fetchEvents,
  createEvent,
  updateEvent,
  deleteEvent,
} from '../utils/api';

export function useCalendarData() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function loadEvents() {
    setLoading(true);
    setError(null);
    try {
      const fetchedEvents = await fetchEvents();
      // Normalize _id to id for frontend consistency and ensure dates are Date objects
      const normalizedEvents = fetchedEvents.map(event => ({
        ...event,
        id: event._id,
        start: new Date(event.start),
        end: new Date(event.end),
      }));
      setEvents(normalizedEvents);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadEvents();
  }, []);

  const createNewEvent = async (event) => {
    setLoading(true);
    setError(null);
    try {
      const created = await createEvent(event);
      // Normalize _id to id and ensure dates are Date objects
      const normalizedCreated = { 
        ...created, 
        id: created._id,
        start: new Date(created.start),
        end: new Date(created.end),
      };
      setEvents((prev) => [...prev, normalizedCreated]);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const updateExistingEvent = async (updatedEvent) => {
    setLoading(true);
    setError(null);
    try {
      const updated = await updateEvent(updatedEvent.id || updatedEvent._id, updatedEvent);
      // Normalize _id to id
      const normalizedUpdated = { ...updated, id: updated._id };
      setEvents((prev) =>
        prev.map((e) => (e.id === normalizedUpdated.id ? normalizedUpdated : e))
      );
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const deleteExistingEvent = async (eventId) => {
    setLoading(true);
    setError(null);
    try {
      await deleteEvent(eventId);
      setEvents((prev) => prev.filter((e) => e._id !== eventId));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return {
    events,
    loading,
    error,
    createNewEvent,
    updateExistingEvent,
    deleteExistingEvent,
    loadEvents,
  };
}
