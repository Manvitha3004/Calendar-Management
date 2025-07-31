import React, { useState, useCallback } from 'react';
import { Calendar, momentLocalizer, Views } from 'react-big-calendar';
import moment from 'moment';
import 'react-big-calendar/lib/css/react-big-calendar.css';
// Removed drag and drop imports to fix error
// import withDragAndDrop from 'react-big-calendar/lib/addons/dragAndDrop';
// import 'react-big-calendar/lib/addons/dragAndDrop/styles.css';
import EventModal from './EventModal';
import useStore from '../../state/store';
import { useCalendarData } from '../../hooks/useCalendarData';
import { fetchEvents } from '../../utils/api';
import { getEvent } from '../../utils/googleCalendarApi';

const localizer = momentLocalizer(moment);
// Removed drag and drop calendar wrapper to fix error
// const DragAndDropCalendar = withDragAndDrop(Calendar);

const CalendarView = () => {
  const { user, token } = useStore();
  const {
    calendars,
    events,
    loading,
    error,
    createNewEvent,
    updateExistingEvent,
    deleteExistingEvent,
    // Add a reload function to refresh events
    loadEvents,
  } = useCalendarData(token);

  const [view, setView] = useState(Views.MONTH);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);

  const onSelectEvent = useCallback(async (event) => {
    try {
      const fullEvent = await getEvent(event.id || event._id);
      setSelectedEvent(fullEvent);
    } catch (error) {
      console.error('Failed to fetch full event details:', error);
      // fallback to partial event data if fetch fails
      setSelectedEvent(event);
    }
    setModalOpen(true);
  }, []);

  const onSelectSlot = useCallback(({ start, end }) => {
    setSelectedEvent({
      id: null,
      title: '',
      start,
      end,
      allDay: false,
    });
    setModalOpen(true);
  }, []);

  const onViewChange = useCallback((newView) => {
    setView(newView);
  }, []);

  const moveEvent = useCallback(({ event, start, end, isAllDay: droppedOnAllDaySlot }) => {
    const updatedEvent = { ...event, start, end, allDay: droppedOnAllDaySlot || event.allDay };
    updateExistingEvent(updatedEvent);
  }, [updateExistingEvent]);

  const resizeEvent = useCallback(({ event, start, end }) => {
    const updatedEvent = { ...event, start, end };
    updateExistingEvent(updatedEvent);
  }, [updateExistingEvent]);

  const handleSave = async (event) => {
    if (event.id !== null) {
      await updateExistingEvent(event);
    } else {
      await createNewEvent(event);
    }
    // Reload events to get fresh data
    await loadEvents();
    // Get fresh events from updated state
    const freshEvents = await fetchEvents();
    const freshEvent = freshEvents.find(e => e._id === event.id || e.id === event.id) || event;
    setSelectedEvent(freshEvent);
    setModalOpen(false);
  };

  const handleDelete = (id) => {
    deleteExistingEvent(id);
    setModalOpen(false);
  };

  const handleClose = () => {
    setModalOpen(false);
  };

  if (loading) {
    return <div className="p-4 text-center">Loading calendar data...</div>;
  }

  if (error) {
    return <div className="p-4 text-center text-red-600">Error: {error}</div>;
  }

  return (
    <div className="p-4 bg-white rounded shadow">
      <Calendar
        localizer={localizer}
        events={events}
        startAccessor="start"
        endAccessor="end"
        style={{ height: 600 }}
        view={view}
        onView={onViewChange}
        onSelectEvent={onSelectEvent}
        onSelectSlot={onSelectSlot}
        selectable
        popup
      />
      <EventModal
        isOpen={modalOpen}
        eventData={selectedEvent}
        onSave={handleSave}
        onDelete={handleDelete}
        onClose={handleClose}
      />
    </div>
  );
};

export default CalendarView;
