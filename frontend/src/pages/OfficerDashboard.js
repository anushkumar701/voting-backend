import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import './Dashboard.css';
import './SelectStyles.css';
import API_BASE from '../api';

function AnimatedNumber({ value }) {
  const [display, setDisplay] = useState(0);
  useEffect(() => {
    let start = 0;
    const end = parseInt(value, 10) || 0;
    if (start === end) return;
    const step = Math.max(1, Math.floor(end / 40));
    const timer = setInterval(() => {
      start += step;
      if (start >= end) { setDisplay(end); clearInterval(timer); }
      else setDisplay(start);
    }, 20);
    return () => clearInterval(timer);
  }, [value]);
  return <span>{display}</span>;
}

export default function OfficerDashboard() {
  const [user,             setUser]             = useState(null);
  const [stats,            setStats]            = useState({ total:0, active:0, inactive:0 });
  const [voters,           setVoters]           = useState([]);
  const [showAdd,          setShowAdd]          = useState(false);
  const [editingId,        setEditingId]        = useState(null);
  const [formData,         setFormData]         = useState({ user_id:'', name:'', email:'', phone:'', ethereum_address:'' });
  const [error,            setError]            = useState('');
  const [success,          setSuccess]          = useState('');
  const [loading,          setLoading]          = useState(false);
  const [searchQuery,      setSearchQuery]      = useState('');
  const nav = useNavigate();

  useEffect(() => {
    const u = sessionStorage.getItem('user');
    if (!u) return nav('/officer-login');
    const ud = JSON.parse(u);
    setUser(ud);
    fetchData(ud.user_id);
  }, [nav]);

  const generateAddress = async () => {
    try {
      const res = await axios.get(`${API_BASE}/api/generate-eth-address`);
      if (res.data.success) {
        setFormData(prev => ({ ...prev, ethereum_address: res.data.data.address }));
      }
    } catch (err) { console.error(err); }
  };

  const fetchData = async (userId) => {
    try {
      const [sRes, vRes] = await Promise.all([
        axios.get(`${API_BASE}/api/officer/stats`,  { headers: { 'X-User-ID': userId } }),
        axios.get(`${API_BASE}/api/officer/voters`, { headers: { 'X-User-ID': userId } }),
      ]);
      if (sRes.data.success) setStats(sRes.data.data);
      if (vRes.data.success) {
        setVoters(vRes.data.data.voters);
      }
    } catch (err) { console.error(err); }
  };

  const resetForm = () => {
    setFormData({ user_id:'', name:'', email:'', phone:'', ethereum_address:'' });
    setEditingId(null); setShowAdd(false);
  };

  const openAddForm = () => {
    resetForm();
    setShowAdd(true);
    generateAddress();
  };

  const addVoter = async (e) => {
    e.preventDefault(); setError(''); setSuccess(''); setLoading(true);
    try {
      const res = await axios.post(`${API_BASE}/api/officer/add-voter`, formData, { headers: { 'X-User-ID': user.user_id } });
      if (res.data.success) { setSuccess('Voter registered ✓'); resetForm(); fetchData(user.user_id); }
    } catch (err) { setError(err.response?.data?.message || 'Failed'); }
    finally { setLoading(false); }
  };

  const updateVoter = async (e) => {
    e.preventDefault(); setError(''); setSuccess(''); setLoading(true);
    try {
      const res = await axios.put(`${API_BASE}/api/officer/update-voter/${editingId}`,
        { name: formData.name, email: formData.email, phone: formData.phone },
        { headers: { 'X-User-ID': user.user_id } }
      );
      if (res.data.success) { setSuccess('Voter updated ✓'); resetForm(); fetchData(user.user_id); }
    } catch (err) { setError(err.response?.data?.message || 'Failed'); }
    finally { setLoading(false); }
  };

  const deleteVoter = async (voterId) => {
    if (!window.confirm('Delete permanently?')) return;
    setError(''); setSuccess('');
    try {
      const res = await axios.delete(`${API_BASE}/api/officer/delete-voter/${voterId}`, { headers: { 'X-User-ID': user.user_id } });
      if (res.data.success) { setSuccess('Voter deleted'); fetchData(user.user_id); }
    } catch (err) { setError(err.response?.data?.message || 'Failed'); }
  };

  const startEdit = (voter) => {
    setFormData({ user_id: voter.user_id, name: voter.name, email: voter.email, phone: voter.phone || '', ethereum_address: voter.ethereum_address });
    setEditingId(voter.user_id);
    setShowAdd(true);
  };

  useEffect(() => {
    if (!success && !error) return;
    const t = setTimeout(() => { setSuccess(''); setError(''); }, 4000);
    return () => clearTimeout(t);
  }, [success, error]);

  const filteredVoters = voters.filter(v =>
    !searchQuery ||
    v.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    v.email?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    v.user_id?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const statCards = [
    { icon:'👥', label:'Total Voters',  value: stats.total,    color:'#00f2ff' },
    { icon:'◉',  label:'Active',        value: stats.active,   color:'#00ff88' },
    { icon:'⛔', label:'Inactive',      value: stats.inactive, color:'#a060ff' },
  ];

  return (
    <div className="dashboard">
      <div className="dash-bg"><div className="cyber-grid" /></div>

      <header className="dash-header">
        <div className="header-content">
          <div className="header-left">
            <div className="logo-hex">
              <svg viewBox="0 0 100 100">
                <defs><linearGradient id="hg2"><stop offset="0%" stopColor="#00ff88"/><stop offset="100%" stopColor="#00f2ff"/></linearGradient></defs>
                <path d="M50 8 L92 32 L92 68 L50 92 L8 68 L8 32 Z" fill="none" stroke="url(#hg2)" strokeWidth="3"/>
                <circle cx="50" cy="44" r="11" fill="url(#hg2)" opacity="0.85"/>
                <path d="M33 68 Q50 55 67 68" fill="none" stroke="url(#hg2)" strokeWidth="2.5" strokeLinecap="round"/>
              </svg>
            </div>
            <div>
              <h1 className="dash-title" style={{ background:'linear-gradient(135deg,#00ff88,#00f2ff)', WebkitBackgroundClip:'text', WebkitTextFillColor:'transparent', backgroundClip:'text' }}>
                OFFICER PANEL
              </h1>
              <p className="dash-subtitle">Voter Registry Management</p>
            </div>
          </div>
          <div className="header-right">
            <div className="user-info">
              <span className="user-name">{user?.name}</span>
              <span className="user-role" style={{ color:'#00ff88', borderColor:'rgba(0,255,136,0.2)', background:'rgba(0,255,136,0.08)' }}>OFFICER</span>
            </div>
            <button onClick={() => { sessionStorage.clear(); nav('/officer-login'); }} className="logout-btn">⏻ LOGOUT</button>
          </div>
        </div>
      </header>

      <AnimatePresence>
        {(error || success) && (
          <motion.div className="alerts" initial={{opacity:0,y:-10}} animate={{opacity:1,y:0}} exit={{opacity:0}}>
            {error   && <div className="alert error">⚠ {error}</div>}
            {success && <div className="alert success">✓ {success}</div>}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Stats */}
      <div className="stats-grid">
        {statCards.map((s, i) => (
          <motion.div
            key={i}
            initial={{ opacity:0, y:30, scale:0.95 }}
            animate={{ opacity:1, y:0, scale:1 }}
            transition={{ delay: i*0.1, type:'spring', stiffness:180 }}
            className="stat-card"
            whileHover={{ y:-6, scale:1.02 }}
          >
            <div className="stat-icon total" style={{ background:`linear-gradient(135deg,${s.color}22,${s.color}08)`, border:`1px solid ${s.color}33`, fontSize:28 }}>
              {s.icon}
            </div>
            <div className="stat-data">
              <div className="stat-value" style={{ background:`linear-gradient(135deg,${s.color},#fff)`, WebkitBackgroundClip:'text', WebkitTextFillColor:'transparent', backgroundClip:'text' }}>
                <AnimatedNumber value={s.value} />
              </div>
              <div className="stat-label">{s.label}</div>
            </div>
            <div style={{ position:'absolute', bottom:0, left:'20%', right:'20%', height:2, background:`linear-gradient(90deg,transparent,${s.color},transparent)`, borderRadius:1 }} />
          </motion.div>
        ))}
      </div>

      <div className="content">
        <div className="content-header">
          <h2 className="section-title">VOTER REGISTRY</h2>
          <div style={{ display:'flex', gap:12, alignItems:'center' }}>
            {/* Search */}
            <input
              type="text"
              placeholder="⌕ Search voters..."
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              style={{
                padding:'10px 16px',
                background:'rgba(0,255,136,0.04)',
                border:'1px solid rgba(0,255,136,0.18)',
                borderRadius:12, color:'#e0ffe8',
                fontSize:13, fontFamily:"'Rajdhani',sans-serif",
                outline:'none', width:200,
                transition:'all 0.3s',
              }}
            />
            <motion.button
              onClick={() => showAdd ? resetForm() : openAddForm()}
              className="create-btn"
              style={{ background:'linear-gradient(135deg,#00cc88,#00aaff)' }}
              whileTap={{ scale:0.96 }}
            >
              {showAdd ? '✕ CANCEL' : '⊕ ADD VOTER'}
            </motion.button>
          </div>
        </div>

        {/* Add / Edit form */}
        <AnimatePresence>
          {showAdd && (
            <motion.div
              initial={{ height:0, opacity:0 }}
              animate={{ height:'auto', opacity:1 }}
              exit={{ height:0, opacity:0 }}
              transition={{ duration:0.35 }}
              className="create-panel"
              style={{ borderColor:'rgba(0,255,136,0.18)' }}
            >
              <form onSubmit={editingId ? updateVoter : addVoter}>
                <div className="form-grid">
                  {!editingId && (
                    <>
                      <input type="text" className="form-input" placeholder="Voter ID (e.g. V001)" value={formData.user_id} onChange={e => setFormData({...formData,user_id:e.target.value})} required />
                      <div style={{ display:'flex', gap:8, alignItems:'center' }}>
                        <input
                          type="text"
                          className="form-input"
                          placeholder="⛓ ETH Address (auto-generated)"
                          value={formData.ethereum_address}
                          readOnly
                          style={{ flex:1, opacity:0.7, cursor:'default' }}
                        />
                        <button
                          type="button"
                          onClick={generateAddress}
                          title="Generate new address"
                          style={{
                            padding:'10px 14px',
                            background:'rgba(0,255,136,0.08)',
                            border:'1px solid rgba(0,255,136,0.25)',
                            borderRadius:10,
                            color:'#00ff88',
                            cursor:'pointer',
                            fontSize:16,
                            transition:'all 0.3s',
                          }}
                        >⟳</button>
                      </div>
                    </>
                  )}
                  <input type="text"  className="form-input" placeholder="Full Name"    value={formData.name}  onChange={e => setFormData({...formData,name:e.target.value})}  required />
                  <input type="email" className="form-input" placeholder="Email"        value={formData.email} onChange={e => setFormData({...formData,email:e.target.value})} required />
                  <input type="tel"   className="form-input" placeholder="Phone Number" value={formData.phone} onChange={e => setFormData({...formData,phone:e.target.value})} />
                </div>
                <button type="submit" disabled={loading} className="submit-btn" style={{ background:'linear-gradient(135deg,#00cc88,#00aaff)' }}>
                  {loading ? '⟳ SAVING...' : (editingId ? '✎ UPDATE VOTER' : '⊕ ADD VOTER')}
                </button>
              </form>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Table */}
        <div className="table-container" style={{ borderColor:'rgba(0,255,136,0.14)' }}>
          <table className="voters-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredVoters.map((v, i) => (
                <motion.tr
                  key={v.user_id}
                  initial={{ opacity:0, x:-10 }}
                  animate={{ opacity:1, x:0 }}
                  transition={{ delay: i*0.04 }}
                >
                  <td><span style={{ fontFamily:"'Share Tech Mono',monospace", color:'#00f2ff', fontSize:13 }}>{v.user_id}</span></td>
                  <td style={{ fontWeight:600 }}>{v.name}</td>
                  <td style={{ color:'rgba(255,255,255,0.6)', fontSize:13 }}>{v.email}</td>
                  <td style={{ color:'rgba(255,255,255,0.5)', fontSize:13 }}>{v.phone || '—'}</td>
                  <td><span className={`badge ${v.is_active ? 'active' : 'inactive'}`}>{v.is_active ? 'Active' : 'Inactive'}</span></td>
                  <td>
                    <div className="table-actions">
                      <button onClick={() => startEdit(v)} className="icon-btn edit" title="Edit">✎</button>
                      <button onClick={() => deleteVoter(v.user_id)} className="icon-btn deactivate" title="Delete">🗑</button>
                    </div>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
          {filteredVoters.length === 0 && (
            <div className="empty">
              {searchQuery ? `⌕ No results for "${searchQuery}"` : '⬡ No voters registered'}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
