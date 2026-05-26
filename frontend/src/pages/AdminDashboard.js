import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import './Dashboard.css';
import './AdminStyles.css';
import API_BASE from '../api';

/* ── Animated Counter ── */
function AnimatedNumber({ value }) {
  const [display, setDisplay] = useState(0);
  useEffect(() => {
    let start = 0;
    const end = parseInt(value, 10) || 0;
    if (start === end) return;
    const duration = 800;
    const step = Math.max(1, Math.floor(end / (duration / 16)));
    const timer = setInterval(() => {
      start += step;
      if (start >= end) { setDisplay(end); clearInterval(timer); }
      else setDisplay(start);
    }, 16);
    return () => clearInterval(timer);
  }, [value]);
  return <span>{display}</span>;
}

export default function AdminDashboard() {
  const [user,       setUser]       = useState(null);
  const [stats,      setStats]      = useState({ total: 0, active: 0, total_votes: 0 });
  const [elections,  setElections]  = useState([]);
  const [showCreate, setShowCreate] = useState(false);
  const [name,       setName]       = useState('');
  const [desc,       setDesc]       = useState('');
  const [candidates, setCandidates] = useState('');
  const [error,      setError]      = useState('');
  const [success,    setSuccess]    = useState('');
  const [loading,    setLoading]    = useState(false);
  const [filter,     setFilter]     = useState('ALL');
  const nav = useNavigate();

  useEffect(() => {
    const u = sessionStorage.getItem('user');
    if (!u) return nav('/admin-login');
    const ud = JSON.parse(u);
    setUser(ud);
    fetchData(ud.user_id);
  }, [nav]);

  const fetchData = async (userId) => {
    try {
      const [sRes, eRes] = await Promise.all([
        axios.get(`${API_BASE}/api/admin/stats`,     { headers: { 'X-User-ID': userId } }),
        axios.get(`${API_BASE}/api/admin/elections`, { headers: { 'X-User-ID': userId } }),
      ]);
      if (sRes.data.success) setStats(sRes.data.data);
      if (eRes.data.success) setElections(eRes.data.data.elections);
    } catch (e) { console.error(e); }
  };

  const createElection = async (e) => {
    e.preventDefault();
    setError(''); setSuccess(''); setLoading(true);
    try {
      const res = await axios.post(`${API_BASE}/api/admin/create-election`, {
        name, description: desc,
        candidates: candidates.split(',').map(c => c.trim()).filter(Boolean),
      }, { headers: { 'X-User-ID': user.user_id } });
      if (res.data.success) {
        setSuccess('Election created on blockchain ✓');
        setShowCreate(false);
        setName(''); setDesc(''); setCandidates('');
        fetchData(user.user_id);
      }
    } catch (err) { setError(err.response?.data?.message || 'Failed'); }
    finally { setLoading(false); }
  };

  const lifecycle = async (url, successMsg) => {
    setError(''); setSuccess(''); setLoading(true);
    try {
      const res = await axios.post(`${API_BASE}${url}`, {}, { headers: { 'X-User-ID': user.user_id } });
      if (res.data.success) { setSuccess(successMsg); fetchData(user.user_id); }
    } catch (err) { setError(err.response?.data?.message || 'Failed'); }
    finally { setLoading(false); }
  };

  const deleteElection = async (electionId) => {
    if (!window.confirm('Cancel this election?')) return;
    setError(''); setSuccess(''); setLoading(true);
    try {
      const res = await axios.delete(`${API_BASE}/api/admin/delete-election/${electionId}`, { headers: { 'X-User-ID': user.user_id } });
      if (res.data.success) { setSuccess('Cancelled'); fetchData(user.user_id); }
    } catch (err) { setError(err.response?.data?.message || 'Failed'); }
    finally { setLoading(false); }
  };

  /* Auto-clear messages */
  useEffect(() => {
    if (!success && !error) return;
    const t = setTimeout(() => { setSuccess(''); setError(''); }, 4000);
    return () => clearTimeout(t);
  }, [success, error]);

  const shown = filter === 'ALL' ? elections : elections.filter(e => e.status === filter);

  const statCards = [
    { key:'total',       icon:'⬡', label:'Total Elections', value: stats.total,       color:'#00f2ff' },
    { key:'active',      icon:'◉', label:'Active Now',      value: stats.active,      color:'#00ff88' },
    { key:'total_votes', icon:'✦', label:'Total Votes Cast', value: stats.total_votes, color:'#a060ff' },
  ];

  return (
    <div className="dashboard">
      <div className="dash-bg"><div className="cyber-grid" /></div>

      {/* ── Header ── */}
      <header className="dash-header">
        <div className="header-content">
          <div className="header-left">
            <div className="logo-hex">
              <svg viewBox="0 0 100 100">
                <defs><linearGradient id="hg"><stop offset="0%" stopColor="#00f2ff"/><stop offset="100%" stopColor="#7000ff"/></linearGradient></defs>
                <path d="M50 8 L92 32 L92 68 L50 92 L8 68 L8 32 Z" fill="none" stroke="url(#hg)" strokeWidth="3"/>
                <path d="M50 22 L80 38 L80 64 L50 80 L20 64 L20 38 Z" fill="none" stroke="url(#hg)" strokeWidth="1" opacity="0.3"/>
                <circle cx="50" cy="50" r="10" fill="url(#hg)" opacity="0.8"/>
              </svg>
            </div>
            <div>
              <h1 className="dash-title">ADMIN CONTROL</h1>
              <p className="dash-subtitle">Blockchain Voting System</p>
            </div>
          </div>
          <div className="header-right">
            <div className="user-info">
              <span className="user-name">{user?.name}</span>
              <span className="user-role">ADMIN</span>
            </div>
            <button onClick={() => { sessionStorage.clear(); nav('/admin-login'); }} className="logout-btn">
              ⏻ LOGOUT
            </button>
          </div>
        </div>
      </header>

      {/* ── Alerts ── */}
      <AnimatePresence>
        {(error || success) && (
          <motion.div
            className="alerts"
            initial={{ opacity:0, y:-10 }}
            animate={{ opacity:1, y:0 }}
            exit={{ opacity:0, y:-10 }}
          >
            {error   && <div className="alert error">⚠ {error}</div>}
            {success && <div className="alert success">✓ {success}</div>}
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── Stats ── */}
      <div className="stats-grid">
        {statCards.map((s, i) => (
          <motion.div
            key={s.key}
            initial={{ opacity:0, y:30, scale:0.95 }}
            animate={{ opacity:1, y:0, scale:1 }}
            transition={{ delay: i * 0.1, type:'spring', stiffness:180 }}
            className="stat-card"
            whileHover={{ y:-6, scale:1.02 }}
          >
            <div className="stat-icon total" style={{ background:`linear-gradient(135deg,${s.color}22,${s.color}08)`, border:`1px solid ${s.color}33` }}>
              <span style={{ fontSize:26, color:s.color }}>{s.icon}</span>
            </div>
            <div className="stat-data">
              <div className="stat-value" style={{ background:`linear-gradient(135deg,${s.color},#fff)`, WebkitBackgroundClip:'text', WebkitTextFillColor:'transparent', backgroundClip:'text' }}>
                <AnimatedNumber value={s.value} />
              </div>
              <div className="stat-label">{s.label}</div>
            </div>
            {/* mini glow bar at bottom */}
            <div style={{ position:'absolute', bottom:0, left:'20%', right:'20%', height:2, background:`linear-gradient(90deg,transparent,${s.color},transparent)`, borderRadius:1 }} />
          </motion.div>
        ))}
      </div>

      {/* ── Content ── */}
      <div className="content">
        <div className="content-header">
          <h2 className="section-title">ELECTIONS</h2>
          <motion.button
            onClick={() => setShowCreate(!showCreate)}
            className="create-btn"
            whileTap={{ scale: 0.96 }}
          >
            {showCreate ? '✕ CANCEL' : '⊕ CREATE'}
          </motion.button>
        </div>

        {/* Create panel */}
        <AnimatePresence>
          {showCreate && (
            <motion.div
              initial={{ height:0, opacity:0 }}
              animate={{ height:'auto', opacity:1 }}
              exit={{ height:0, opacity:0 }}
              transition={{ duration:0.35, ease:'easeInOut' }}
              className="create-panel"
            >
              <form onSubmit={createElection}>
                <div className="form-grid">
                  <input type="text" className="form-input" placeholder="Election Name" value={name} onChange={e => setName(e.target.value)} required />
                  <input type="text" className="form-input" placeholder="Description (optional)" value={desc} onChange={e => setDesc(e.target.value)} />
                  <input type="text" className="form-input full" placeholder="Candidates — comma separated: Alice, Bob, Charlie" value={candidates} onChange={e => setCandidates(e.target.value)} required />
                </div>
                <button type="submit" disabled={loading} className="submit-btn">
                  {loading ? '⟳ DEPLOYING TO BLOCKCHAIN...' : '⊕ CREATE ELECTION'}
                </button>
              </form>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Filter */}
        <div className="filter-bar">
          {['ALL','CREATED','ACTIVE','CLOSED','ARCHIVED'].map(f => (
            <motion.button
              key={f}
              onClick={() => setFilter(f)}
              className={`filter-btn ${filter === f ? 'active' : ''}`}
              whileTap={{ scale:0.95 }}
            >
              {f}
            </motion.button>
          ))}
        </div>

        {/* Elections Grid */}
        <div className="elections-grid">
          {shown.length === 0 ? (
            <div className="empty">⬡ No elections found</div>
          ) : shown.map((e, i) => (
            <motion.div
              key={e.election_id}
              initial={{ opacity:0, y:30, scale:0.96 }}
              animate={{ opacity:1, y:0,  scale:1 }}
              transition={{ delay: i*0.07, type:'spring', stiffness:160 }}
              className="election-card"
              whileHover={{ y:-6 }}
            >
              <div className="election-header">
                <div>
                  <h3 className="election-name">{e.name}</h3>
                  <p className="election-desc">{e.description || 'No description'}</p>
                </div>
                <div className={`status ${e.status.toLowerCase()}`}>{e.status}</div>
              </div>

              {e.status === 'CREATED' && (
                <div className="action-required">⚡ Activate to allow voting</div>
              )}

              <div className="election-stats">
                <div className="stat-item">
                  <span className="num">{e.total_votes || 0}</span>
                  <span className="txt">Votes</span>
                </div>
                <div className="stat-item">
                  <span className="num">{e.candidates?.length}</span>
                  <span className="txt">Candidates</span>
                </div>
                <div className="stat-item">
                  <span className="num">#{e.election_id}</span>
                  <span className="txt">ID</span>
                </div>
              </div>

              {/* Candidate vote bars or tags */}
              {e.candidates_with_votes && e.candidates_with_votes.length > 0 ? (
                <div className="candidates">
                  {e.candidates_with_votes.map((c, j) => {
                    const pct = (e.total_votes || 0) > 0 ? (c.votes / e.total_votes) * 100 : 0;
                    return (
                      <div key={j} className="candidate">
                        <div className="candidate-info">
                          <span className="cand-name">{c.name}</span>
                          <span className="cand-votes">{c.votes} votes · {Math.round(pct)}%</span>
                        </div>
                        <div className="vote-bar">
                          <motion.div
                            initial={{ width:0 }}
                            animate={{ width:`${pct}%` }}
                            transition={{ duration:1, delay:0.2+j*0.1, ease:'easeOut' }}
                            className="vote-fill"
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="candidates-list-simple">
                  {e.candidates?.map((c, j) => (
                    <span key={j} className="candidate-tag">{c}</span>
                  ))}
                </div>
              )}

              {/* Actions */}
              <div className="actions">
                {e.status === 'CREATED' && (
                  <>
                    <button onClick={() => lifecycle(`/api/admin/activate-election/${e.election_id}`, '⚡ Election activated!')} className="action-btn activate" disabled={loading}>ACTIVATE</button>
                    <button onClick={() => deleteElection(e.election_id)} className="action-btn cancel" disabled={loading}>CANCEL</button>
                  </>
                )}
                {e.status === 'ACTIVE' && (
                  <button onClick={() => lifecycle(`/api/admin/close-election/${e.election_id}`, '✓ Election closed')} className="action-btn close" disabled={loading}>CLOSE</button>
                )}
                {e.status === 'CLOSED' && (
                  <button onClick={() => lifecycle(`/api/admin/archive-election/${e.election_id}`, '✓ Archived')} className="action-btn archive" disabled={loading}>ARCHIVE</button>
                )}
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
