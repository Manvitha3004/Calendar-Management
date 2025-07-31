import React, { useEffect, useState } from 'react';
import { useCalendarData } from '../../hooks/useCalendarData';
import MeetingCard from './MeetingCard';

const MeetingPrepPage = () => {
  const { events, loading, error } = useCalendarData();
  const [todayEvents, setTodayEvents] = useState([]);

  useEffect(() => {
    if (events && events.length > 0) {
      const startOfDay = new Date();
      startOfDay.setHours(0, 0, 0, 0);
      const endOfDay = new Date();
      endOfDay.setHours(23, 59, 59, 999);

      const filtered = events.filter(event => {
        const eventStart = new Date(event.start);
        return eventStart >= startOfDay && eventStart <= endOfDay;
      });
      setTodayEvents(filtered);
    } else {
      setTodayEvents([]);
    }
  }, [events]);

  const formatDate = (date) => {
    return date.toLocaleDateString(undefined, { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' });
  };

  const today = new Date();

  return (
    <div className="max-w-4xl mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6 text-center text-purple-900">Your Meetings, Fully Prepared</h1>
      <div className="mb-8 text-center text-gray-700">{formatDate(today)}</div>
      {loading && <div className="text-center text-gray-500">Loading meetings...</div>}
      {error && <div className="text-center text-red-600">Error: {error}</div>}
      {!loading && todayEvents.length === 0 && (
        <div className="text-center text-gray-600">No meetings scheduled for today.</div>
      )}
      <div>
        {todayEvents.map(event => (
          <MeetingCard key={event._id || event.id} event={event} />
        ))}
      </div>
    </div>
  );
};

export default MeetingPrepPage;
