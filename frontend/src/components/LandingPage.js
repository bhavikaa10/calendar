import React, { useRef } from 'react';
import { useAuth } from '../AuthContext';
import CalendarUpload from './CalendarUpload';
import './LandingPage.css';

const LandingPage = () => {
  const { user, signOut } = useAuth();
  const appSectionRef = useRef(null);

  const scrollToApp = () => {
    appSectionRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="landing-page">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">📅 Planora</h1>
          <p className="hero-subtitle">Plan smarter, achieve more</p>
          <p className="hero-description">
            Transform your syllabus PDFs into a unified, interactive calendar. 
            Never miss a deadline, stay organized, and ace your semester with Planora.
          </p>
          <div className="hero-buttons">
            <button className="btn-primary" onClick={scrollToApp}>
              Get Started
            </button>
            <button className="btn-secondary" onClick={scrollToApp}>
              Learn More
            </button>
          </div>
        </div>
        <div className="scroll-indicator" onClick={scrollToApp}>
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <div className="features-container">
          <h2 className="features-title">Why Choose Planora?</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">📄</div>
              <h3 className="feature-title">Multi-Course Support</h3>
              <p className="feature-description">
                Upload multiple syllabus PDFs at once and create a unified calendar 
                for all your courses in seconds.
              </p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🤖</div>
              <h3 className="feature-title">Smart Auto-Parse</h3>
              <p className="feature-description">
                Our AI automatically extracts course codes, dates, and assignments 
                from your PDFs with high accuracy.
              </p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">💾</div>
              <h3 className="feature-title">Save & Sync</h3>
              <p className="feature-description">
                Your calendar data is securely saved. Access it anytime, 
                from any device, without re-uploading.
              </p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📤</div>
              <h3 className="feature-title">Export Anywhere</h3>
              <p className="feature-description">
                Export to Google Calendar, Apple Calendar, ICS format, 
                or download as a PDF for offline access.
              </p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🎨</div>
              <h3 className="feature-title">Beautiful Interface</h3>
              <p className="feature-description">
                Clean, modern design with intuitive navigation. 
                View your semester month-by-month with ease.
              </p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🔒</div>
              <h3 className="feature-title">Secure & Private</h3>
              <p className="feature-description">
                Your data is encrypted and secure. Sign in with email 
                or Google OAuth for safe, reliable access.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* App Section */}
      <section className="app-section" ref={appSectionRef}>
        <div className="app-container">
          <div className="app-header">
            <div>
              <h1>📅 Planora</h1>
              <p>Welcome back, {user.email}</p>
            </div>
            <button
              onClick={signOut}
              style={{
                padding: '10px 20px',
                background: '#475569',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontSize: '14px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'background 0.2s'
              }}
              onMouseOver={(e) => e.target.style.background = '#334155'}
              onMouseOut={(e) => e.target.style.background = '#475569'}
            >
              Sign Out
            </button>
          </div>
          <div className="app-content">
            <CalendarUpload />
          </div>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;
