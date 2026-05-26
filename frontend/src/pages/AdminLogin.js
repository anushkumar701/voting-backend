import React, { useState, useRef, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { motion } from 'framer-motion';
import './Login.css';
import API_BASE from '../api';

/* ── Floating particle count ── */
const PARTICLE_COUNT = 50;

export default function AdminLogin() {
  const [email, setEmail]       = useState('');
  const [password, setPassword] = useState('');
  const [error, setError]       = useState('');
  const [loading, setLoading]   = useState(false);
  const nav    = useNavigate();
  const panelRef = useRef(null);

  /* 3-D tilt on mouse move */
  const handleMouseMove = (e) => {
    if (!panelRef.current) return;
    const rect = panelRef.current.getBoundingClientRect();
    const cx = rect.left + rect.width  / 2;
    const cy = rect.top  + rect.height / 2;
    const rotY =  ((e.clientX - cx) / (rect.width  / 2)) * 8;
    const rotX = -((e.clientY - cy) / (rect.height / 2)) * 6;
    panelRef.current.style.transform =
      `perspective(1000px) rotateX(${rotX}deg) rotateY(${rotY}deg) translateZ(0)`;
  };

  const handleMouseLeave = () => {
    if (!panelRef.current) return;
    panelRef.current.style.transform =
      'perspective(1000px) rotateX(0deg) rotateY(0deg) translateZ(0)';
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setError(''); setLoading(true);
    try {
      const res = await axios.post(`${API_BASE}/api/login`, { email, password });
      if (res.data.success && res.data.data.role === 'admin') {
        sessionStorage.setItem('user',   JSON.stringify(res.data.data));
        sessionStorage.setItem('userId', res.data.data.user_id);
        nav('/admin-dashboard');
      } else {
        setError('Admin access only');
      }
    } catch (err) {
      if (err.response)      setError(err.response.data?.message || 'Login failed');
      else if (err.request)  setError('No response from server. Is backend running?');
      else                   setError('Request error: ' + err.message);
    } finally { setLoading(false); }
  };

  const fillTestCredentials = () => {
    setEmail('admin@admin.com');
    setPassword('admin123');
  };

  return (
    <div className="login-container" onMouseMove={handleMouseMove} onMouseLeave={handleMouseLeave}>
      {/* Animated background */}
      <div className="cyber-bg">
        <div className="cyber-grid" />
        <div className="orb orb-1" />
        <div className="orb orb-2" />
        <div className="orb orb-3" />
        <div className="particles">
          {[...Array(PARTICLE_COUNT)].map((_, i) => (
            <div key={i} className="particle" style={{
              left:             `${Math.random() * 100}%`,
              top:              `${Math.random() * 100}%`,
              animationDelay:   `${Math.random() * 10}s`,
              animationDuration:`${8 + Math.random() * 8}s`,
              width:  `${1 + Math.random() * 2}px`,
              height: `${1 + Math.random() * 2}px`,
              opacity: 0.4 + Math.random() * 0.6,
            }} />
          ))}
        </div>
      </div>

      <motion.div
        ref={panelRef}
        initial={{ opacity: 0, y: 60, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
        className="login-panel"
        style={{ transition: 'transform 0.15s ease-out, box-shadow 0.3s' }}
      >
        {/* ── Logo ── */}
        <div className="logo-section">
          <motion.div
            initial={{ scale: 0, rotate: -90 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ delay: 0.3, type: 'spring', stiffness: 200 }}
            className="logo-hex"
          >
            <svg viewBox="0 0 100 100">
              <defs>
                <linearGradient id="adminGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%"   stopColor="#00f2ff" />
                  <stop offset="100%" stopColor="#7000ff" />
                </linearGradient>
              </defs>
              <path d="M50 8 L92 32 L92 68 L50 92 L8 68 L8 32 Z"
                    fill="none" stroke="url(#adminGrad)" strokeWidth="2.5" />
              <path d="M50 20 L80 36 L80 64 L50 80 L20 64 L20 36 Z"
                    fill="none" stroke="url(#adminGrad)" strokeWidth="1" opacity="0.4"/>
              <circle cx="50" cy="50" r="14" fill="url(#adminGrad)" opacity="0.9"/>
              <circle cx="50" cy="50" r="6"  fill="#fff" opacity="0.6"/>
              {/* shield icon lines */}
              <line x1="50" y1="42" x2="50" y2="50" stroke="#fff" strokeWidth="2" strokeLinecap="round"/>
              <circle cx="50" cy="54" r="1.5" fill="#fff"/>
            </svg>
          </motion.div>

          <motion.h1
            className="title"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.45 }}
          >
            ADMIN ACCESS
          </motion.h1>
          <motion.p
            className="subtitle"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.55 }}
          >
            E-Voting · Blockchain · Secure
          </motion.p>
        </div>

        {/* ── Form ── */}
        <form onSubmit={handleLogin} className="login-form">
          {error && (
            <motion.div
              initial={{ x: -20, opacity: 0 }}
              animate={{ x: 0,   opacity: 1 }}
              className="error-box"
            >
              ⚠ {error}
            </motion.div>
          )}

          <div className="input-group">
            <input
              type="email"
              className="input-field"
              placeholder="Email Address"
              value={email}
              onChange={e => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="input-group">
            <input
              type="password"
              className="input-field"
              placeholder="Password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
            />
          </div>

          <motion.button
            type="submit"
            className="submit-btn"
            disabled={loading}
            whileTap={{ scale: 0.97 }}
          >
            {loading ? 'AUTHENTICATING...' : 'ACCESS SYSTEM'}
          </motion.button>

          <button
            type="button"
            onClick={fillTestCredentials}
            style={{
              marginTop: '6px',
              padding: '10px',
              background: 'rgba(0,242,255,0.05)',
              border: '1px dashed rgba(0,242,255,0.2)',
              borderRadius: '12px',
              color: 'rgba(0,242,255,0.5)',
              cursor: 'pointer',
              fontSize: '12px',
              fontFamily: "'Share Tech Mono', monospace",
              letterSpacing: '1px',
              transition: 'all 0.3s',
            }}
            onMouseEnter={e => e.target.style.borderColor = 'rgba(0,242,255,0.45)'}
            onMouseLeave={e => e.target.style.borderColor = 'rgba(0,242,255,0.2)'}
          >
            ⚡ USE TEST CREDENTIALS
          </button>
        </form>

        {/* ── Role links ── */}
        <div className="links">
          <Link to="/officer-login">Officer Login</Link>
          <Link to="/voter-login">Voter Login</Link>
        </div>
      </motion.div>
    </div>
  );
}
