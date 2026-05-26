import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import './Dashboard.css';
import './VotingStyles.css';
import API_BASE from '../api';

/* Animated success overlay after voting */
function VoteSuccessOverlay({ candidateName, onDone }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      style={{
        position: 'fixed', inset: 0, zIndex: 999,
        background: 'rgba(2,4,8,0.92)',
        display: 'flex', flexDirection: 'column',
        alignItems: 'center', justifyContent: 'center',
        backdropFilter: 'blur(10px)',
      }}
    >
      {/* Chain links animation */}
      <motion.div
        initial={{ scale: 0 }}
        animate={{ scale: [0, 1.3, 1] }}
        transition={{ duration: 0.6, times: [0, 0.6, 1] }}
        style={{ marginBottom: 32 }}
      >
        <svg width="120" height="120" viewBox="0 0 120 120">
          <defs>
            <linearGradient id="svgSuccessGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%"   stopColor="#00ff88"/>
              <stop offset="100%" stopColor="#00f2ff"/>
            </linearGradient>
          </defs>
          <circle cx="60" cy="60" r="54" fill="none" stroke="url(#svgSuccessGrad)" strokeWidth="3" opacity="0.3"/>
          <motion.circle
            cx="60" cy="60" r="54"
            fill="none" stroke="url(#svgSuccessGrad)" strokeWidth="3"
            strokeDasharray="339.3"
            initial={{ strokeDashoffset: 339.3 }}
            animate={{ strokeDashoffset: 0 }}
            transition={{ duration: 0.8, delay: 0.3 }}
            strokeLinecap="round"
            transform="rotate(-90 60 60)"
          />
          <motion.path
            d="M36 60 L52 76 L84 44"
            fill="none" stroke="url(#svgSuccessGrad)" strokeWidth="5"
            strokeLinecap="round" strokeLinejoin="round"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 0.5, delay: 0.7 }}
          />
        </svg>
      </motion.div>

      <motion.h2
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
        style={{
          fontFamily: "'Orbitron',sans-serif", fontSize: 26,
          background: 'linear-gradient(135deg,#00ff88,#00f2ff)',
          WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
          backgroundClip: 'text', letterSpacing: 3, marginBottom: 12,
        }}
      >
        VOTE RECORDED
      </motion.h2>

      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1 }}
        style={{ color:'rgba(255,255,255,0.6)', fontSize:15, marginBottom:8 }}
      >
        Your vote for
      </motion.p>
      <motion.p
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 1.1, type:'spring' }}
        style={{
          color:'#00ff88', fontSize:22, fontWeight:700,
          fontFamily:"'Orbitron',sans-serif", letterSpacing:2,
          marginBottom: 32, textShadow:'0 0 25px rgba(0,255,136,0.6)',
        }}
      >
        {candidateName}
      </motion.p>
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.4 }}
        style={{
          color:'rgba(0,242,255,0.5)', fontSize:11,
          fontFamily:"'Share Tech Mono',monospace", letterSpacing:2,
        }}
      >
        SECURED ON BLOCKCHAIN · IMMUTABLE RECORD
      </motion.p>
    </motion.div>
  );
}

export default function VoterDashboard() {
  const [user,             setUser]             = useState(null);
  const [elections,        setElections]        = useState([]);
  const [selectedElection, setSelectedElection] = useState(null);
  const [selectedCandidate,setSelectedCandidate]= useState(null);
  const [votedElections,   setVotedElections]   = useState([]);
  const [error,            setError]            = useState('');
  const [success,          setSuccess]          = useState('');
  const [loading,          setLoading]          = useState(false);
  const [showSuccessOverlay, setShowSuccessOverlay] = useState(false);
  const [votedName,        setVotedName]        = useState('');
  const nav = useNavigate();

  useEffect(() => {
    const u = sessionStorage.getItem('user');
    if (!u) return nav('/voter-login');
    const ud = JSON.parse(u);
    setUser(ud);
    fetchElections(ud);
  }, [nav]);

  const fetchElections = async (userData) => {
    try {
      const res = await axios.get(`${API_BASE}/api/elections`);
      if (res.data.success) {
        const list = res.data.data.elections;
        setElections(list);
        const voted = [];
        for (const el of list) {
          try {
            const sr = await axios.get(`${API_BASE}/api/voter/check-vote-status/${el.election_id}`, {
              headers: { 'X-User-ID': userData.user_id },
            });
            if (sr.data.success && sr.data.data.has_voted) voted.push(el.election_id);
          } catch {}
        }
        setVotedElections(voted);
      }
    } catch (err) { console.error(err); }
  };

  const loadElectionDetails = async (electionId) => {
    if (votedElections.includes(electionId)) {
      setError('You have already voted in this election');
      return;
    }
    setError('');
    try {
      const res = await axios.get(`${API_BASE}/api/election/${electionId}`);
      if (res.data.success) {
        setSelectedElection(res.data.data);
        setSelectedCandidate(null);
      }
    } catch (err) { setError(err.response?.data?.message || 'Failed to load election'); }
  };

  const castVote = async () => {
    setError(''); setSuccess(''); setLoading(true);
    try {
      const res = await axios.post(`${API_BASE}/api/cast-vote`, {
        election_id: selectedElection.election_id,
        candidate_index: selectedCandidate,
      }, { headers: { 'X-User-ID': user.user_id } });

      if (res.data.success) {
        const name = selectedElection.candidates[selectedCandidate];
        setVotedName(name);
        setShowSuccessOverlay(true);
        setVotedElections(prev => [...prev, selectedElection.election_id]);

        setTimeout(() => {
          setShowSuccessOverlay(false);
          setSelectedElection(null);
          setSelectedCandidate(null);
          fetchElections(user);
        }, 3500);
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to cast vote');
    } finally { setLoading(false); }
  };

  useEffect(() => {
    if (!error) return;
    const t = setTimeout(() => setError(''), 4000);
    return () => clearTimeout(t);
  }, [error]);

  const activeElections = elections.filter(e => e.status === 'ACTIVE');

  return (
    <div className="dashboard voter">
      <div className="dash-bg"><div className="cyber-grid" /></div>

      {/* ── Success Overlay ── */}
      <AnimatePresence>
        {showSuccessOverlay && (
          <VoteSuccessOverlay candidateName={votedName} onDone={() => setShowSuccessOverlay(false)} />
        )}
      </AnimatePresence>

      {/* ── Header ── */}
      <header className="dash-header">
        <div className="header-content">
          <div className="header-left">
            <div className="logo-hex">
              <svg viewBox="0 0 100 100">
                <defs><linearGradient id="hg3"><stop offset="0%" stopColor="#ff00ea"/><stop offset="100%" stopColor="#7000ff"/></linearGradient></defs>
                <path d="M50 8 L92 32 L92 68 L50 92 L8 68 L8 32 Z" fill="none" stroke="url(#hg3)" strokeWidth="3"/>
                <rect x="34" y="38" width="32" height="24" rx="3" fill="url(#hg3)" opacity="0.7"/>
                <path d="M44 36 L50 30 L56 36" fill="none" stroke="url(#hg3)" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
                <line x1="50" y1="30" x2="50" y2="38" stroke="url(#hg3)" strokeWidth="2.5"/>
              </svg>
            </div>
            <div>
              <h1 className="dash-title" style={{ background:'linear-gradient(135deg,#ff00ea,#7000ff)', WebkitBackgroundClip:'text', WebkitTextFillColor:'transparent', backgroundClip:'text' }}>
                VOTER PORTAL
              </h1>
              <p className="dash-subtitle">Blockchain · Secure · Anonymous</p>
            </div>
          </div>
          <div className="header-right">
            <div className="user-info">
              <span className="user-name">{user?.name}</span>
              <span className="user-role" style={{ color:'#ff44ee', borderColor:'rgba(200,0,255,0.2)', background:'rgba(200,0,255,0.08)' }}>VOTER</span>
            </div>
            <button onClick={() => { sessionStorage.clear(); nav('/voter-login'); }} className="logout-btn">⏻ LOGOUT</button>
          </div>
        </div>
      </header>

      {/* ── Alerts ── */}
      <AnimatePresence>
        {error && (
          <motion.div className="alerts" initial={{opacity:0,y:-10}} animate={{opacity:1,y:0}} exit={{opacity:0}}>
            <div className="alert error">⚠ {error}</div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="content">
        <AnimatePresence mode="wait">
          {!selectedElection ? (
            /* ── Election List ── */
            <motion.div
              key="list"
              initial={{ opacity:0, y:20 }}
              animate={{ opacity:1, y:0 }}
              exit={{ opacity:0, y:-20 }}
            >
              <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginBottom:28 }}>
                <h2 className="section-title">ACTIVE ELECTIONS</h2>
                <span style={{
                  fontFamily:"'Share Tech Mono',monospace",
                  fontSize:12, color:'rgba(0,242,255,0.45)',
                  letterSpacing:2, padding:'6px 14px',
                  border:'1px solid rgba(0,242,255,0.12)',
                  borderRadius:8,
                }}>
                  {activeElections.length} OPEN
                </span>
              </div>

              <div className="elections-grid">
                {activeElections.length === 0 ? (
                  <motion.div
                    className="empty"
                    initial={{ opacity:0 }}
                    animate={{ opacity:1 }}
                  >
                    ⬡ No active elections at this time
                  </motion.div>
                ) : (
                  activeElections.map((e, i) => {
                    const hasVoted = votedElections.includes(e.election_id);
                    return (
                      <motion.div
                        key={e.election_id}
                        initial={{ opacity:0, y:30, scale:0.96 }}
                        animate={{ opacity:1, y:0,  scale:1 }}
                        transition={{ delay: i*0.1, type:'spring', stiffness:150 }}
                        className={`election-card ${hasVoted ? 'voted' : 'clickable'}`}
                        onClick={() => !hasVoted && loadElectionDetails(e.election_id)}
                        whileHover={!hasVoted ? { y:-7, scale:1.01 } : {}}
                      >
                        {/* Voted ribbon */}
                        {hasVoted && (
                          <div style={{
                            position:'absolute', top:0, right:0,
                            background:'linear-gradient(135deg,rgba(0,255,136,0.2),rgba(0,200,255,0.2))',
                            border:'1px solid rgba(0,255,136,0.3)',
                            padding:'4px 14px', fontSize:10, color:'#00ff88',
                            borderRadius:'0 22px 0 14px',
                            fontFamily:"'Share Tech Mono',monospace",
                            letterSpacing:1.5,
                          }}>VOTED ✓</div>
                        )}

                        <h3 className="election-name">{e.name}</h3>
                        <p className="election-desc" style={{ marginBottom:16 }}>{e.description || 'Blockchain-secured election'}</p>

                        <div style={{ display:'flex', gap:8, flexWrap:'wrap', marginBottom:16 }}>
                          {e.candidates?.slice(0,3).map((c,j) => (
                            <span key={j} style={{
                              background:'rgba(200,0,255,0.08)',
                              border:'1px solid rgba(200,0,255,0.2)',
                              borderRadius:20, padding:'3px 12px',
                              fontSize:12, color:'rgba(255,80,255,0.8)',
                              fontFamily:"'Rajdhani',sans-serif",
                            }}>{c}</span>
                          ))}
                          {(e.candidates?.length || 0) > 3 && (
                            <span style={{ color:'rgba(255,255,255,0.3)', fontSize:12, padding:'3px 8px' }}>
                              +{e.candidates.length - 3} more
                            </span>
                          )}
                        </div>

                        {hasVoted ? (
                          <div className="status voted">✓ VOTE RECORDED</div>
                        ) : (
                          <motion.button
                            className="vote-btn"
                            style={{ background:'linear-gradient(135deg,#cc00cc,#5500ff)', marginTop:0 }}
                            whileHover={{ scale:1.02 }}
                            whileTap={{ scale:0.97 }}
                          >
                            CAST YOUR VOTE →
                          </motion.button>
                        )}
                      </motion.div>
                    );
                  })
                )}
              </div>
            </motion.div>
          ) : (
            /* ── Voting Booth ── */
            <motion.div
              key="booth"
              className="voting-section"
              initial={{ opacity:0, x:40 }}
              animate={{ opacity:1, x:0 }}
              exit={{ opacity:0, x:-40 }}
              transition={{ duration:0.35, ease:'easeOut' }}
            >
              <button
                onClick={() => { setSelectedElection(null); setSelectedCandidate(null); }}
                className="back-btn"
              >
                ← BACK TO ELECTIONS
              </button>

              <div className="vote-container">
                <div className="vote-header">
                  <h2>{selectedElection.name}</h2>
                  <p>{selectedElection.description || 'Select your candidate below'}</p>
                </div>

                <div className="candidates-list">
                  {selectedElection.candidates?.map((candidate, i) => (
                    <motion.div
                      key={i}
                      initial={{ opacity:0, x:-25 }}
                      animate={{ opacity:1, x:0 }}
                      transition={{ delay: i*0.08, type:'spring', stiffness:200 }}
                      className={`candidate-card ${selectedCandidate === i ? 'selected' : ''}`}
                      onClick={() => setSelectedCandidate(i)}
                      whileTap={{ scale:0.98 }}
                    >
                      <div className="candidate-number">{i + 1}</div>
                      <div className="candidate-name">{candidate}</div>
                      {selectedCandidate === i && (
                        <motion.div className="selected-check">✓</motion.div>
                      )}
                    </motion.div>
                  ))}
                </div>

                {/* Confirm panel */}
                <AnimatePresence>
                  {selectedCandidate !== null && (
                    <motion.div
                      className="vote-confirm"
                      initial={{ opacity:0, y:20, scale:0.96 }}
                      animate={{ opacity:1, y:0,  scale:1 }}
                      exit={{ opacity:0, y:10, scale:0.97 }}
                      transition={{ type:'spring', stiffness:250 }}
                    >
                      <p>You are voting for</p>
                      <strong>{selectedElection.candidates[selectedCandidate]}</strong>

                      <p style={{ fontSize:12, color:'rgba(255,255,255,0.35)', marginTop:10, marginBottom:18, fontFamily:"'Share Tech Mono',monospace", letterSpacing:1 }}>
                        This action is permanent and recorded on the blockchain
                      </p>

                      <div className="vote-actions">
                        <motion.button
                          onClick={() => setSelectedCandidate(null)}
                          className="btn-cancel"
                          whileTap={{ scale:0.96 }}
                        >
                          CANCEL
                        </motion.button>
                        <motion.button
                          onClick={castVote}
                          disabled={loading}
                          className="btn-vote"
                          style={{ background:'linear-gradient(135deg,#cc00cc,#5500ff)' }}
                          whileTap={{ scale:0.96 }}
                          whileHover={{ scale:1.02 }}
                        >
                          {loading ? '⟳ CASTING...' : '⛓ CONFIRM & CAST'}
                        </motion.button>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
