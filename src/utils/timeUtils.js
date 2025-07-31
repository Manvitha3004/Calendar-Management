import { format, parseISO } from 'date-fns';

export const formatEventTime = (date) => {
  if (!date) return '';
  const parsedDate = typeof date === 'string' ? parseISO(date) : date;
  return format(parsedDate, 'yyyy-MM-dd\'T\'HH:mm');
};

export const formatDisplayTime = (date) => {
  if (!date) return '';
  const parsedDate = typeof date === 'string' ? parseISO(date) : date;
  return format(parsedDate, 'MMM dd, yyyy HH:mm');
};

export const toLocalISOString = (date) => {
  const tzOffset = new Date().getTimezoneOffset() * 60000;
  return new Date(date - tzOffset).toISOString().slice(0, 16);
};

export const fromLocalISOString = (dateString) => {
  if (!dateString) return null;
  const date = new Date(dateString);
  const tzOffset = new Date().getTimezoneOffset() * 60000;
  return new Date(date.getTime() + tzOffset);
};