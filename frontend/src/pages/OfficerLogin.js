import React, { useState, useRef } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import './Login.css';
import API_BASE from '../api';

const PARTICLE_COUNT = 50;

export default function OfficerLogin() {
  const [email, setEmail]       = useState('');
  const [password, setPassword] = useState('');
  const [error, setError]       = useState('');
  const [loading, setLoading]   = useState(false);
  const nav      = useNavigate();
  const panelRef = useRef(null);

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
      if (res.data.success && res.data.data.role === 'officer') {
        sessionStorage.setItem('user', JSON.stringify(res.data.data));
        nav('/officer-dashboard');
      } else {
        setError('Officer access only');
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Login failed');
    } finally { setLoading(false); }
  };

  const fillTestCredentials = () => {
    setEmail('officer@admin.com');
    setPassword('officer123');
  };

  return (
    <div className="login-container" onMouseMove={handleMouseMove} onMouseLeave={handleMouseLeave}>
      <div className="cyber-bg">
        <div className="cyber-grid" />
        {/* Green-tinted orbs for officer */}
        <div className="orb orb-1" style={{ background: 'rgba(0,255,136,0.1)' }} />
        <div className="orb orb-2" style={{ background: 'rgba(0,200,255,0.12)' }} />
        <div className="orb orb-3" style={{ background: 'rgba(0,100,200,0.08)' }} />
        <div className="particles">
          {[...Array(PARTICLE_COUNT)].map((_, i) => (
            <div key={i} className="particle" style={{
              left:             `${Math.random() * 100}%`,
              top:              `${Math.random() * 100}%`,
              animationDelay:   `${Math.random() * 10}s`,
              animationDuration:`${8 + Math.random() * 8}s`,
              background:       'rgba(0,255,136,0.9)',
              boxShadow:        '0 0 8px rgba(0,255,136,0.7)',
              width:  `${1 + Math.random() * 2}px`,
              height: `${1 + Math.random() * 2}px`,
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
        style={{
          transition: 'transform 0.15s ease-out',
          borderColor: 'rgba(0,255,136,0.2)',
          boxShadow: '0 0 0 1px rgba(0,255,136,0.04), 0 20px 60px rgba(0,0,0,0.8), 0 0 80px rgba(0,255,136,0.05)',
        }}
      >
        <div className="logo-section">
          <motion.div
            initial={{ scale: 0, rotate: -90 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ delay: 0.3, type: 'spring', stiffness: 200 }}
            className="logo-hex"
          >
            <svg viewBox="0 0 100 100">
              <defs>
                <linearGradient id="officerGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%"   stopColor="#00ff88" />
                  <stop offset="100%" stopColor="#00c8ff" />
                </linearGradient>
              </defs>
              <path d="M50 8 L92 32 L92 68 L50 92 L8 68 L8 32 Z"
                    fill="none" stroke="url(#officerGrad)" strokeWidth="2.5"/>
              <path d="M50 20 L80 36 L80 64 L50 80 L20 64 L20 36 Z"
                    fill="none" stroke="url(#officerGrad)" strokeWidth="1" opacity="0.4"/>
              <circle cx="50" cy="44" r="11" fill="url(#officerGrad)" opacity="0.85"/>
              <path d="M34 66 Q50 55 66 66" fill="none" stroke="url(#officerGrad)" strokeWidth="2.5" strokeLinecap="round"/>
            </svg>
          </motion.div>

          <motion.h1
            className="title"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.45 }}
            style={{ background: 'linear-gradient(135deg,#00ff88,#00c8ff)', WebkitBackgroundClip:'text', WebkitTextFillColor:'transparent', backgroundClip:'text' }}
          >
            OFFICER ACCESS
          </motion.h1>
          <motion.p
            className="subtitle"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.55 }}
          >
            Voter Management · Registry Control
          </motion.p>
        </div>

        <form onSubmit={handleLogin} className="login-form">
          <AnimatePresence>
            {error && (
              <motion.div
                initial={{ x: -20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                exit={{ opacity: 0 }}
                className="error-box"
              >
                ⚠ {error}
              </motion.div>
            )}
          </AnimatePresence>

          <div className="input-group">
            <input
              type="email"
              className="input-field"
              placeholder="Email Address"
              value={email}
              onChange={e => setEmail(e.target.value)}
              required
              style={{ borderColor: 'rgba(0,255,136,0.2)' }}
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
              style={{ borderColor: 'rgba(0,255,136,0.2)' }}
            />
          </div>

          <motion.button
            type="submit"
            className="submit-btn"
            disabled={loading}
            whileTap={{ scale: 0.97 }}
            style={{ background: 'linear-gradient(135deg,#00cc88,#00aaff)' }}
          >
            {loading ? 'AUTHENTICATING...' : 'ACCESS SYSTEM'}
          </motion.button>

          <button
            type="button"
            onClick={fillTestCredentials}
            style={{
              marginTop: '6px',
              padding: '10px',
              background: 'rgba(0,255,136,0.05)',
              border: '1px dashed rgba(0,255,136,0.2)',
              borderRadius: '12px',
              color: 'rgba(0,255,136,0.5)',
              cursor: 'pointer',
              fontSize: '12px',
              fontFamily: "'Share Tech Mono', monospace",
              letterSpacing: '1px',
              transition: 'all 0.3s',
            }}
            onMouseEnter={e => e.target.style.borderColor = 'rgba(0,255,136,0.45)'}
            onMouseLeave={e => e.target.style.borderColor = 'rgba(0,255,136,0.2)'}
          >
            ⚡ USE TEST CREDENTIALS
          </button>
        </form>

        <div className="links">
          <Link to="/admin-login">Admin Login</Link>
          <Link to="/voter-login">Voter Login</Link>
        </div>
      </motion.div>
    </div>
  );
}
