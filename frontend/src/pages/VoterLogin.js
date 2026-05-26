import React, { useState, useRef } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import './Login.css';
import API_BASE from '../api';

const PARTICLE_COUNT = 50;

export default function VoterLogin() {
  const [step,           setStep]           = useState(1);
  const [voterId,        setVoterId]        = useState('');
  const [phone,          setPhone]          = useState('');
  const [otp,            setOtp]            = useState('');
  const [error,          setError]          = useState('');
  const [success,        setSuccess]        = useState('');
  const [loading,        setLoading]        = useState(false);
  const [otpForTesting,  setOtpForTesting]  = useState('');
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

  const requestOTP = async (e) => {
    e.preventDefault();
    setError(''); setSuccess(''); setLoading(true);
    try {
      const res = await axios.post(`${API_BASE}/api/voter/request-otp`, { voter_id: voterId, phone });
      if (res.data.success) {
        setSuccess(res.data.message);
        setOtpForTesting(res.data.data.otp_for_testing);
        setStep(2);
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to send OTP');
    } finally { setLoading(false); }
  };

  const verifyOTP = async (e) => {
    e.preventDefault();
    setError(''); setSuccess(''); setLoading(true);
    try {
      const res = await axios.post(`${API_BASE}/api/voter/verify-otp`, { voter_id: voterId, otp_code: otp });
      if (res.data.success) {
        sessionStorage.setItem('user', JSON.stringify(res.data.data));
        nav('/voter-dashboard');
      }
    } catch (err) {
      setError(err.response?.data?.message || 'OTP verification failed');
    } finally { setLoading(false); }
  };

  /* OTP digit display helper */
  const otpDigits = otpForTesting ? otpForTesting.split('') : [];

  return (
    <div className="login-container" onMouseMove={handleMouseMove} onMouseLeave={handleMouseLeave}>
      <div className="cyber-bg">
        <div className="cyber-grid" />
        <div className="orb orb-1" style={{ background: 'rgba(180,0,255,0.12)' }} />
        <div className="orb orb-2" style={{ background: 'rgba(255,0,200,0.1)'  }} />
        <div className="orb orb-3" style={{ background: 'rgba(0,100,255,0.08)' }} />
        <div className="particles">
          {[...Array(PARTICLE_COUNT)].map((_, i) => (
            <div key={i} className="particle" style={{
              left:             `${Math.random() * 100}%`,
              top:              `${Math.random() * 100}%`,
              animationDelay:   `${Math.random() * 10}s`,
              animationDuration:`${8 + Math.random() * 8}s`,
              background:       'rgba(255,0,220,0.85)',
              boxShadow:        '0 0 8px rgba(255,0,220,0.6)',
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
          borderColor: 'rgba(200,0,255,0.2)',
          boxShadow: '0 0 0 1px rgba(200,0,255,0.04), 0 20px 60px rgba(0,0,0,0.8), 0 0 80px rgba(180,0,255,0.06)',
        }}
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
                <linearGradient id="voterGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%"   stopColor="#ff00ea" />
                  <stop offset="100%" stopColor="#7000ff" />
                </linearGradient>
              </defs>
              <path d="M50 8 L92 32 L92 68 L50 92 L8 68 L8 32 Z"
                    fill="none" stroke="url(#voterGrad)" strokeWidth="2.5"/>
              <path d="M50 20 L80 36 L80 64 L50 80 L20 64 L20 36 Z"
                    fill="none" stroke="url(#voterGrad)" strokeWidth="1" opacity="0.4"/>
              {/* ballot box icon */}
              <rect x="34" y="38" width="32" height="24" rx="3" fill="url(#voterGrad)" opacity="0.8"/>
              <path d="M44 36 L50 30 L56 36" fill="none" stroke="url(#voterGrad)" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
              <line x1="50" y1="30" x2="50" y2="38" stroke="url(#voterGrad)" strokeWidth="2.5"/>
              <line x1="40" y1="49" x2="46" y2="55" stroke="#fff" strokeWidth="2" strokeLinecap="round"/>
              <line x1="46" y1="55" x2="60" y2="43" stroke="#fff" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </motion.div>

          <motion.h1
            className="title"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.45 }}
            style={{ background: 'linear-gradient(135deg,#ff00ea,#7000ff)', WebkitBackgroundClip:'text', WebkitTextFillColor:'transparent', backgroundClip:'text' }}
          >
            VOTER PORTAL
          </motion.h1>
          <motion.p
            className="subtitle"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.55 }}
          >
            OTP-Based · Secure · Anonymous
          </motion.p>
        </div>

        {/* ── Step indicator ── */}
        <div style={{ display:'flex', gap:8, marginBottom:24, justifyContent:'center' }}>
          {[1,2].map(s => (
            <motion.div
              key={s}
              style={{
                width: step === s ? 32 : 24, height: 8,
                borderRadius: 4,
                transition: 'all 0.4s ease',
                background: step >= s
                  ? 'linear-gradient(135deg,#ff00ea,#7000ff)'
                  : 'rgba(255,255,255,0.08)',
                transform: step === s ? 'scale(1.1)' : 'scale(1)',
              }}
            />
          ))}
        </div>

        <AnimatePresence mode="wait">
          {step === 1 ? (
            <motion.form
              key="step1"
              onSubmit={requestOTP}
              className="login-form"
              initial={{ opacity: 0, x: 30 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -30 }}
              transition={{ duration: 0.3 }}
            >
              {error && (
                <motion.div initial={{x:-20,opacity:0}} animate={{x:0,opacity:1}} className="error-box">
                  ⚠ {error}
                </motion.div>
              )}
              {success && (
                <motion.div initial={{x:-20,opacity:0}} animate={{x:0,opacity:1}} className="success-box">
                  ✓ {success}
                </motion.div>
              )}

              <div className="input-group">
                <input
                  type="text"
                  className="input-field"
                  placeholder="Voter ID (e.g. V001)"
                  value={voterId}
                  onChange={e => setVoterId(e.target.value)}
                  required
                  style={{ borderColor: 'rgba(200,0,255,0.25)' }}
                />
              </div>

              <div className="input-group">
                <input
                  type="tel"
                  className="input-field"
                  placeholder="Mobile Number"
                  value={phone}
                  onChange={e => setPhone(e.target.value)}
                  required
                  style={{ borderColor: 'rgba(200,0,255,0.25)' }}
                />
              </div>

              <motion.button
                type="submit"
                className="submit-btn"
                disabled={loading}
                whileTap={{ scale: 0.97 }}
                style={{ background: 'linear-gradient(135deg,#cc00cc,#5500ff)' }}
              >
                {loading ? 'SENDING OTP...' : 'REQUEST OTP →'}
              </motion.button>
            </motion.form>
          ) : (
            <motion.form
              key="step2"
              onSubmit={verifyOTP}
              className="login-form"
              initial={{ opacity: 0, x: 30 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -30 }}
              transition={{ duration: 0.3 }}
            >
              {error && (
                <motion.div initial={{x:-20,opacity:0}} animate={{x:0,opacity:1}} className="error-box">
                  ⚠ {error}
                </motion.div>
              )}

              {otpDigits.length > 0 && (
                <motion.div
                  className="otp-display"
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  style={{ borderColor: 'rgba(200,0,255,0.3)' }}
                >
                  <p style={{ marginBottom: 6 }}>Your Test OTP</p>
                  <div style={{ display:'flex', justifyContent:'center', gap:8, margin:'8px 0' }}>
                    {otpDigits.map((d,i) => (
                      <motion.span
                        key={i}
                        initial={{ opacity:0, y:10 }}
                        animate={{ opacity:1, y:0 }}
                        transition={{ delay: i * 0.08 }}
                        style={{
                          display:'inline-block',
                          width:38, height:46,
                          background:'rgba(180,0,255,0.15)',
                          border:'1px solid rgba(200,0,255,0.35)',
                          borderRadius:8,
                          fontSize:22, fontWeight:700,
                          fontFamily:"'Share Tech Mono', monospace",
                          color:'#ff44ee',
                          textAlign:'center', lineHeight:'46px',
                          boxShadow:'0 0 12px rgba(180,0,255,0.25)',
                        }}
                      >{d}</motion.span>
                    ))}
                  </div>
                  <small>For testing only — in production, sent via SMS</small>
                </motion.div>
              )}

              <div className="input-group">
                <input
                  type="text"
                  className="input-field"
                  placeholder="Enter 6-digit OTP"
                  value={otp}
                  onChange={e => setOtp(e.target.value)}
                  maxLength="6"
                  required
                  style={{
                    letterSpacing:'8px', fontSize:'22px', textAlign:'center',
                    borderColor:'rgba(200,0,255,0.3)',
                  }}
                />
              </div>

              <motion.button
                type="submit"
                className="submit-btn"
                disabled={loading}
                whileTap={{ scale: 0.97 }}
                style={{ background: 'linear-gradient(135deg,#cc00cc,#5500ff)' }}
              >
                {loading ? 'VERIFYING...' : '✓ VERIFY & LOGIN'}
              </motion.button>

              <button
                type="button"
                onClick={() => { setStep(1); setOtp(''); setError(''); setSuccess(''); }}
                className="back-btn-login"
              >
                ← BACK
              </button>
            </motion.form>
          )}
        </AnimatePresence>

        <div className="links">
          <Link to="/admin-login">Admin Login</Link>
          <Link to="/officer-login">Officer Login</Link>
        </div>
      </motion.div>
    </div>
  );
}
