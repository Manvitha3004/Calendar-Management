import React, { useState, useEffect } from 'react';

const defaultEvent = {
  id: null,
  summary: '',
  start: new Date(),
  end: new Date(),
  allDay: false,
  attendees: [],
  recurrence: [],
  reminders: { useDefault: true, overrides: [] },
  location: '',
  hangoutLink: '',
  description: '',
};

function formatRecurrence(recurrence) {
  if (!recurrence || recurrence.length === 0) return '- Not Provided -';
  return recurrence.join('\n');
}

function formatReminders(reminders) {
  if (!reminders || !reminders.overrides || reminders.overrides.length === 0) return '- Not Provided -';
  return reminders.overrides
    .map(r => `${r.minutes} mins before via ${r.method}`)
    .join(', ');
}

function toLocalInputValue(date) {
  if (!date) return '';
  const d = new Date(date);
  d.setMinutes(d.getMinutes() - d.getTimezoneOffset());
  return d.toISOString().slice(0, 16);
}

const EventModal = ({ isOpen, eventData, onSave, onDelete, onClose }) => {
  const [event, setEvent] = useState(defaultEvent);
  const [attendeesInput, setAttendeesInput] = useState('');
  const [remindersInput, setRemindersInput] = useState('');
  const [recurrenceInput, setRecurrenceInput] = useState('');
  const [locationInput, setLocationInput] = useState('');
  const [meetingLinkInput, setMeetingLinkInput] = useState('');
  const [descriptionInput, setDescriptionInput] = useState('');
  const [meetingDescriptionInput, setMeetingDescriptionInput] = useState('');
  const [startInput, setStartInput] = useState('');
  const [endInput, setEndInput] = useState('');

  useEffect(() => {
    if (eventData) {
      setEvent(eventData);
      setStartInput(toLocalInputValue(eventData.start));
      setEndInput(toLocalInputValue(eventData.end));
      setAttendeesInput(
        Array.isArray(eventData.attendees)
          ? eventData.attendees.join(', ')
          : eventData.attendees || ''
      );
      setRemindersInput(
        Array.isArray(eventData.reminders)
          ? eventData.reminders.join(', ')
          : eventData.reminders || ''
      );
      setRecurrenceInput(eventData.recurrence || '');
      setLocationInput(eventData.location || '');
      setMeetingLinkInput(eventData.meetingLink || eventData.hangoutLink || '');
      setDescriptionInput(eventData.description || '');
      setMeetingDescriptionInput(eventData.meetingDescription || eventData.description || '');
    } else {
      setEvent(defaultEvent);
      setStartInput(toLocalInputValue(defaultEvent.start));
      setEndInput(toLocalInputValue(defaultEvent.end));
      setAttendeesInput('');
      setRemindersInput('');
      setRecurrenceInput('');
      setLocationInput('');
      setMeetingLinkInput('');
      setDescriptionInput('');
      setMeetingDescriptionInput('');
    }
  }, [eventData]);

  if (!isOpen) return null;

  const handleChange = (e) => {
    const { name, value } = e.target;
    setEvent((prev) => ({ ...prev, [name]: value }));
  };

  const handleAttendeesChange = (e) => {
    setAttendeesInput(e.target.value);
  };

  const handleRemindersChange = (e) => {
    setRemindersInput(e.target.value);
  };

  const handleRecurrenceChange = (e) => {
    setRecurrenceInput(e.target.value);
  };

  const handleMeetingLinkChange = (e) => {
    setMeetingLinkInput(e.target.value);
  };

  const handleMeetingDescriptionChange = (e) => {
    setMeetingDescriptionInput(e.target.value);
  };

  const handleSave = () => {
    // Convert input value to local time before saving
    const localStart = new Date(startInput);
    const localEnd = new Date(endInput);
    localStart.setMinutes(localStart.getMinutes() - localStart.getTimezoneOffset());
    localEnd.setMinutes(localEnd.getMinutes() - localEnd.getTimezoneOffset());

    const updatedEvent = {
      ...event,
      start: localStart.toISOString(),
      end: localEnd.toISOString(),
      attendees: attendeesInput.split(',').map((a) => a.trim()).filter((a) => a),
      reminders: remindersInput.split(',').map((r) => r.trim()).filter((r) => r),
      recurrence: recurrenceInput,
      location: locationInput,
      meetingLink: meetingLinkInput,
      meetingDescription: meetingDescriptionInput,
      description: descriptionInput,
    };
    onSave(updatedEvent);
  };

  const handleDelete = () => {
    if (event.id) {
      onDelete(event.id);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
      <div className="bg-white rounded-lg shadow-lg p-6 w-full max-w-lg max-h-[90vh] overflow-auto">
        <h2 className="text-2xl font-bold mb-4 text-gray-800">
          {event.id ? 'Edit Event' : 'Create Event'}
        </h2>
        <form>
          <label className="block mb-4">
            <span className="text-gray-700 font-medium">Title</span>
            <input
              type="text"
              name="title"
              value={event.title || ''}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter event title"
            />
          </label>
          <label className="block mb-4">
            <span className="text-gray-700 font-medium">Start</span>
            <input
              type="datetime-local"
              name="start"
              value={startInput || ''}
              onChange={(e) => setStartInput(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </label>
          <label className="block mb-4">
            <span className="text-gray-700 font-medium">End</span>
            <input
              type="datetime-local"
              name="end"
              value={endInput || ''}
              onChange={(e) => setEndInput(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </label>
          <label className="block mb-4">
            <span className="text-gray-700 font-medium">Attendees (comma separated emails)</span>
            <input
              type="text"
              value={attendeesInput || ''}
              onChange={handleAttendeesChange}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., john@example.com, jane@example.com"
            />
          </label>
          <label className="block mb-4">
            <span className="text-gray-700 font-medium">Reminders (comma separated minutes before event)</span>
            <input
              type="text"
              value={remindersInput || ''}
              onChange={handleRemindersChange}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., 10, 30, 60"
            />
          </label>
          <label className="block mb-4">
            <span className="text-gray-700 font-medium">Recurrence (e.g., daily, weekly, monthly)</span>
            <input
              type="text"
              value={recurrenceInput || ''}
              onChange={handleRecurrenceChange}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., daily, weekly"
            />
          </label>
          <label className="block mb-4">
            <span className="text-gray-700 font-medium">Meeting Link</span>
            <input
              type="url"
              value={meetingLinkInput || ''}
              onChange={handleMeetingLinkChange}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="https://zoom.us/..."
            />
          </label>
          <label className="block mb-4">
            <span className="text-gray-700 font-medium">Meeting Description</span>
            <textarea
              value={meetingDescriptionInput || ''}
              onChange={handleMeetingDescriptionChange}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-y"
              rows={4}
              placeholder="Describe the meeting purpose, agenda, etc."
            />
          </label>
          <div className="flex justify-between mt-6">
            <button
              onClick={handleDelete}
              disabled={!event.id}
              className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 disabled:opacity-50"
            >
              Delete
            </button>
            <div>
              <button
                onClick={onClose}
                className="mr-2 px-4 py-2 rounded-lg border border-gray-300 hover:bg-gray-100"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600"
              >
                Save
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EventModal;
