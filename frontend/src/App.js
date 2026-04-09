import React from 'react';
import { useAuth } from './AuthContext';
import Auth from './components/Auth';
import LandingPage from './components/LandingPage';

function App() {
  const { user } = useAuth();

  if (!user) {
    return <Auth />;
  }

  return <LandingPage />;
}

export default App;
