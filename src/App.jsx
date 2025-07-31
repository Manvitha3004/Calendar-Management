import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import CalendarView from './components/Calendar/CalendarView';
import MeetingPrepPage from './components/MeetingPrep/MeetingPrepPage';
import AgentDashboard from './components/AgentDashboard/AgentDashboard';
import EmailDashboard from './components/EmailManagement/EmailDashboard';
import useStore from './state/store';
import ToastNotification from './components/UI/ToastNotification';
import GoogleLoginButton from './components/Auth/GoogleLoginButton';

function App() {
  const { toastMessage, toastType, clearToast } = useStore();

  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-r from-pink-50 via-purple-50 to-blue-50">
        <header className="bg-purple-200 shadow p-6 flex justify-between items-center rounded-b-lg">
          <h1 className="text-3xl font-semibold text-purple-900">AI Calendar Assistant</h1>
          <nav className="flex items-center space-x-6">
            <Link to="/" className="text-purple-800 hover:underline">Calendar</Link>
            <Link to="/meeting-prep" className="text-purple-800 hover:underline">Meeting Prep</Link>
            <Link to="/agents" className="text-purple-800 hover:underline">Agent Dashboard</Link>
            <Link to="/emails" className="text-purple-800 hover:underline">Email Management</Link>
            <GoogleLoginButton />
          </nav>
        </header>
        <main className="p-6">
          <Routes>
            <Route path="/" element={<CalendarView />} />
            <Route path="/meeting-prep" element={<MeetingPrepPage />} />
            <Route path="/agents" element={<AgentDashboard />} />
            <Route path="/emails" element={<EmailDashboard />} />
          </Routes>
        </main>
        <ToastNotification
          message={toastMessage}
          type={toastType}
          onClose={clearToast}
        />
      </div>
    </Router>
  );
}

export default App;
