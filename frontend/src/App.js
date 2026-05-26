import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import AdminLogin from './pages/AdminLogin';
import AdminDashboard from './pages/AdminDashboard';
import OfficerLogin from './pages/OfficerLogin';
import OfficerDashboard from './pages/OfficerDashboard';
import VoterLogin from './pages/VoterLogin';
import VoterDashboard from './pages/VoterDashboard';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navigate to="/admin-login" />} />
        <Route path="/admin-login" element={<AdminLogin />} />
        <Route path="/admin-dashboard" element={<AdminDashboard />} />
        <Route path="/officer-login" element={<OfficerLogin />} />
        <Route path="/officer-dashboard" element={<OfficerDashboard />} />
        <Route path="/voter-login" element={<VoterLogin />} />
        <Route path="/voter-dashboard" element={<VoterDashboard />} />
      </Routes>
    </Router>
  );
}

export default App;
