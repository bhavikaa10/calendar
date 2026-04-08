import React from 'react';
import { useAuth } from './AuthContext';
import Auth from './components/Auth';
import CalendarUpload from './components/CalendarUpload';

function App() {
  const { user, signOut } = useAuth();

  if (!user) {
    return <Auth />;
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%)',
      padding: '20px'
    }}>
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto'
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '32px',
          padding: '20px 24px',
          background: 'white',
          borderRadius: '16px',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.08)',
          border: '1px solid #e2e8f0'
        }}>
          <div>
            <h1 style={{
              fontSize: '32px',
              fontWeight: '700',
              color: '#0f172a',
              marginBottom: '4px'
            }}>
              📅 Planora
            </h1>
            <p style={{ fontSize: '14px', color: '#64748b' }}>
              Welcome back, {user.email}
            </p>
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

        <div style={{
          background: 'white',
          borderRadius: '16px',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.08)',
          border: '1px solid #e2e8f0'
        }}>
          <CalendarUpload />
        </div>
      </div>
    </div>
  );
}

export default App;
