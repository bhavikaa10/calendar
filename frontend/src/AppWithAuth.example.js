/**
 * Example: How to integrate Auth + Export into your existing App.js
 *
 * This shows how to wrap your current calendar app with authentication
 * and add export functionality
 */

import React, { useState } from 'react';
import { AuthProvider, useAuth } from './AuthContext';
import Auth from './components/Auth';
import ExportMenu from './components/ExportMenu';
import './App.css';

function CalendarApp() {
  const { user, signOut } = useAuth();
  const [events, setEvents] = useState([]);
  const [semesterInfo, setSemesterInfo] = useState('');

  // If user is not logged in, show Auth component
  if (!user) {
    return <Auth />;
  }

  // User is logged in - show the main app
  return (
    <div className="app-container">
      {/* Header with user info */}
      <header className="app-header">
        <div className="header-left">
          <h1>📚 SyllaSync</h1>
          <span className="user-email">{user.email}</span>
        </div>
        <div className="header-right">
          {/* Show export menu if events exist */}
          {events.length > 0 && (
            <ExportMenu events={events} semesterInfo={semesterInfo} />
          )}
          <button className="sign-out-btn" onClick={signOut}>
            Sign Out
          </button>
        </div>
      </header>

      {/* Your existing calendar upload form */}
      <main className="app-main">
        <div className="upload-section">
          <h2>Upload Syllabus</h2>
          {/* Your existing upload form code here */}

          {/* Example form */}
          <form onSubmit={(e) => {
            e.preventDefault();
            // Your existing form submission logic
            // After successful upload, set events:
            // setEvents(parsedEvents);
            // setSemesterInfo(`${startDate} to ${endDate}`);
          }}>
            <input type="file" accept=".pdf" />
            <input type="date" placeholder="Start Date" />
            <input type="date" placeholder="End Date" />
            <button type="submit">Generate Calendar</button>
          </form>
        </div>

        {/* Calendar Display */}
        {events.length > 0 && (
          <div className="calendar-section">
            <h2>Your Calendar</h2>
            <div className="events-list">
              {events.map((event, index) => (
                <div key={index} className="event-item">
                  <span className="event-date">{event.date}</span>
                  <span className="event-title">{event.title}</span>
                  <span className={`event-type ${event.type}`}>
                    {event.type}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

// Wrap entire app with AuthProvider
function App() {
  return (
    <AuthProvider>
      <CalendarApp />
    </AuthProvider>
  );
}

export default App;

/*
 * CSS Example (add to App.css)

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 40px;
  background: white;
  border-bottom: 1px solid #e2e8f0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-left h1 {
  font-size: 24px;
  margin: 0;
}

.user-email {
  color: #64748b;
  font-size: 14px;
}

.header-right {
  display: flex;
  gap: 12px;
  align-items: center;
}

.sign-out-btn {
  padding: 10px 20px;
  background: white;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.sign-out-btn:hover {
  border-color: #cbd5e1;
  background: #f8fafc;
}

.app-main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

.events-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.event-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: white;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
}

.event-date {
  font-weight: 600;
  color: #667eea;
  min-width: 100px;
}

.event-title {
  flex: 1;
  color: #1e293b;
}

.event-type {
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.event-type.exam {
  background: #fee2e2;
  color: #dc2626;
}

.event-type.assignment {
  background: #dbeafe;
  color: #2563eb;
}

.event-type.class {
  background: #dcfce7;
  color: #16a34a;
}
*/
