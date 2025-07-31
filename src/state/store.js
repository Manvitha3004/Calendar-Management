import create from 'zustand';

const useStore = create((set) => ({
  user: null,
  token: null,
  calendars: [],
  events: [],
  loading: false,
  error: null,
  modalOpen: false,
  selectedEvent: null,
  toastMessage: '',
  toastType: 'info',

  setUser: (user) => set({ user }),
  setToken: (token) => set({ token }),
  setCalendars: (calendars) => set({ calendars }),
  setEvents: (events) => set({ events }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  openModal: (event) => set({ modalOpen: true, selectedEvent: event }),
  closeModal: () => set({ modalOpen: false, selectedEvent: null }),
  addEvent: (event) =>
    set((state) => ({ events: [...state.events, event] })),
  updateEvent: (updatedEvent) =>
    set((state) => ({
      events: state.events.map((ev) =>
        ev.id === updatedEvent.id ? updatedEvent : ev
      ),
    })),
  deleteEvent: (id) =>
    set((state) => ({
      events: state.events.filter((ev) => ev.id !== id),
    })),
  setToast: (message, type = 'info') => set({ toastMessage: message, toastType: type }),
  clearToast: () => set({ toastMessage: '', toastType: 'info' }),
}));

export default useStore;
