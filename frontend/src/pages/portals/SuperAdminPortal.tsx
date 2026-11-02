import React, { useState, useEffect, useCallback } from 'react';
import {
  Server, Activity, RefreshCw, Download, CheckCircle, Shield, Users,
  Database, Cpu, HardDrive, AlertTriangle, Lock, Key, Eye, BarChart2,
  Settings, UserPlus, Trash2, Edit, ToggleLeft, ToggleRight, Clock,
  XCircle, ChevronRight, Globe, Layers, Zap
} from 'lucide-react';
import './PortalStyles.css';

/* ═══ Mock Data ═══ */
const MOCK_DAEMONS = [
  { name: 'FastAPI Application Server', port: '127.0.0.1:8000', status: 'ONLINE',    latency: '2.1 ms', tag: 'Core API', health: 99.8 },
  { name: 'PostgreSQL 15 Relational DB', port: '127.0.0.1:5432', status: 'CONNECTED', latency: '0.8 ms', tag: 'ACID DB',  health: 100 },
  { name: 'Redis 7.0 In-Memory Broker',  port: '127.0.0.1:6379', status: 'CONNECTED', latency: '0.4 ms', tag: 'Queue',   health: 100 },
  { name: 'Celery Task Workers (6)',      port: 'Pool — 6 Queues', status: 'ACTIVE',   latency: 'Ready',  tag: 'AI Jobs', health: 98.5 },
  { name: 'Vite React 19 SPA',           port: '127.0.0.1:5173', status: 'ONLINE',   latency: 'HMR',    tag: 'Frontend', health: 100 },
  { name: 'Tesseract OCR Engine 5',      port: 'Local Process',   status: 'STANDBY',  latency: 'On-demand', tag: 'OCR',  health: 100 },
  { name: 'Sentence-BERT Embedder',      port: 'Local Process',   status: 'LOADED',   latency: '18 ms',  tag: 'AI/ML',  health: 100 },
];

const MOCK_USERS = [
  { id: 1, username: 'super_admin',   full_name: 'Dr. Suresh Iyer',       role: 'super_admin',    last_login: '2026-10-26 14:32', active: true  },
  { id: 2, username: 'academic_admin',full_name: 'Prof. Meera Krishnan',   role: 'academic_admin', last_login: '2026-10-26 09:10', active: true  },
  { id: 3, username: 'teacher_user',  full_name: 'Dr. Anand Sharma',       role: 'teacher',        last_login: '2026-10-25 16:48', active: true  },
  { id: 4, username: 'ocr_operator',  full_name: 'Ravi Kumar',             role: 'ocr_review',     last_login: '2026-10-26 11:20', active: true  },
  { id: 5, username: 'ai_specialist', full_name: 'Dr. Priya Menon',        role: 'ai_evaluation',  last_login: '2026-10-26 13:55', active: true  },
  { id: 6, username: 'evaluator1',    full_name: 'Prof. Rajiv Nair',       role: 'evaluator',      last_login: '2026-10-24 10:30', active: true  },
  { id: 7, username: 'integrity_off', full_name: 'Sneha Pillai',           role: 'integrity',      last_login: '2026-10-25 08:05', active: true  },
  { id: 8, username: 'student_001',   full_name: 'Arjun Reddy (24MCA01)',  role: 'student',        last_login: '2026-10-26 07:45', active: true  },
  { id: 9, username: 'analytics_mgr', full_name: 'Dr. Kavita Rao',        role: 'analytics',      last_login: '2026-10-23 15:20', active: false },
  { id: 10,username: 'researcher',    full_name: 'Deepak Varma',           role: 'research_lab',   last_login: '2026-10-26 12:00', active: true  },
];

const MOCK_AUDIT = [
  { ts: '14:32:01', actor: 'super_admin',   action: 'User login', entity: 'Auth', severity: 'info'    },
  { ts: '14:18:47', actor: 'ai_specialist', action: 'AI model evaluation triggered', entity: 'Exam #41', severity: 'info' },
  { ts: '13:55:33', actor: 'teacher_user',  action: 'Rubric published', entity: 'MCA301 Q3', severity: 'info' },
  { ts: '13:02:10', actor: 'evaluator1',    action: 'Score override +1.5', entity: 'Script #SS-2025-007', severity: 'warning' },
  { ts: '12:45:59', actor: 'ocr_operator',  action: 'OCR transcript corrected', entity: 'Sheet #104', severity: 'info' },
  { ts: '11:30:22', actor: 'integrity_off', action: 'Collusion flag raised', entity: 'Students 21MCA08 ↔ 21MCA09', severity: 'error' },
  { ts: '10:10:05', actor: 'super_admin',   action: 'System config updated', entity: 'AI model profile', severity: 'warning' },
  { ts: '09:45:00', actor: 'academic_admin',action: 'Exam calendar published', entity: 'Nov 2026 Schedule', severity: 'info' },
];

const ROLE_COLORS: Record<string, string> = {
  super_admin: '#FCA5A5', academic_admin: '#93C5FD', teacher: '#A5B4FC',
  ocr_review: '#67E8F9', ai_evaluation: '#C4B5FD', evaluator: '#86EFAC',
  integrity: '#FCD34D', student: '#FDBA74', analytics: '#5EEAD4', research_lab: '#6EE7B7'
};

export const SuperAdminPortal: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'users' | 'audit' | 'config'>('overview');
  const [telemetry, setTelemetry] = useState<any>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedUser, setSelectedUser] = useState<any>(null);
  const [userModal, setUserModal] = useState(false);
  const [cpuAnim, setCpuAnim] = useState(42);
  const [ramAnim, setRamAnim] = useState(58);

  const fetchTelemetry = useCallback(async () => {
    setRefreshing(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/admin/overview');
      if (res.ok) setTelemetry(await res.json());
    } catch { /* offline */ }
    finally { setRefreshing(false); }
  }, []);

  useEffect(() => { fetchTelemetry(); }, [fetchTelemetry]);

  /* Animate CPU/RAM meters */
  useEffect(() => {
    const iv = setInterval(() => {
      setCpuAnim(prev => Math.min(95, Math.max(20, prev + (Math.random() - 0.5) * 8)));
      setRamAnim(prev => Math.min(85, Math.max(30, prev + (Math.random() - 0.5) * 5)));
    }, 2000);
    return () => clearInterval(iv);
  }, []);

  return (
    <div className="portal-page">
      {/* Header */}
      <div className="portal-header">
        <div className="portal-header-left">
          <div className="portal-badge-row">
            <span className="portal-badge admin">Portal 1: Governance</span>
            <span className="live-indicator"><span className="live-dot" />Live System Telemetry</span>
            <span style={{ fontSize: '0.8rem', color: '#10B981', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
              <CheckCircle size={13} /> 100% Local-First — Zero Cloud Dependency
            </span>
          </div>
          <h1>Super Administrator Control Plane</h1>
          <p>Full infrastructure health monitoring, role-based permission matrix, model governance registry, immutable audit log retention, and user administration for IntelliGrade AMAES.</p>
        </div>
        <div className="portal-header-actions">
          <button onClick={fetchTelemetry} className="btn btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }} disabled={refreshing}>
            <RefreshCw size={15} className={refreshing ? 'pulse-icon' : ''} />
            {refreshing ? 'Polling...' : 'Refresh'}
          </button>
          <button className="btn btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Download size={15} /> Export Audit Trail
          </button>
        </div>
      </div>

      {/* KPI Strip */}
      <div className="kpi-strip">
        {[
          { icon: '🟢', label: 'System Health', value: '100%', delta: 'All services nominal', color: '#22C55E', accent: 'rgba(21,128,61,0.35)' },
          { icon: '👥', label: 'Active Users', value: telemetry?.total_users || '10', delta: '9 online now', color: '#818CF8', accent: 'rgba(79,70,229,0.35)' },
          { icon: '⚡', label: 'CPU Load', value: `${cpuAnim.toFixed(0)}%`, delta: 'AMD64 Local Host', color: '#F59E0B', accent: 'rgba(180,83,9,0.35)' },
          { icon: '🧠', label: 'RAM Usage', value: `${ramAnim.toFixed(0)}%`, delta: `${(ramAnim * 0.16).toFixed(1)} / 16 GB`, color: '#38BDF8', accent: 'rgba(37,99,235,0.35)' },
          { icon: '💾', label: 'Disk Free', value: `${telemetry?.hardware?.free_disk_gb || 16.9} GB`, delta: 'Above 10 GB threshold', color: '#34D399', accent: 'rgba(16,185,129,0.35)' },
        ].map((k, i) => (
          <div key={i} className="kpi-card" style={{ '--kpi-accent': `linear-gradient(90deg, ${k.accent}, transparent)` } as any}>
            <div className="kpi-icon" style={{ background: `${k.accent}` }}>{k.icon}</div>
            <div className="kpi-value" style={{ color: k.color }}>{k.value}</div>
            <div className="kpi-label">{k.label}</div>
            <div className="kpi-delta flat">{k.delta}</div>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="portal-tabs">
        {(['overview', 'users', 'audit', 'config'] as const).map(t => (
          <button key={t} className={`portal-tab ${activeTab === t ? 'active' : ''}`} onClick={() => setActiveTab(t)}>
            {t === 'overview' ? '🖥️ System Overview' : t === 'users' ? '👥 User Management' : t === 'audit' ? '📋 Audit Log' : '⚙️ Configuration'}
          </button>
        ))}
      </div>

      {/* ── OVERVIEW TAB ── */}
      {activeTab === 'overview' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div className="split-panel">
            {/* Daemon Status */}
            <div className="portal-section-card">
              <div className="section-card-header">
                <div className="section-card-title"><Server size={16} color="#818CF8" /> Subsystem Daemon Health</div>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
                {MOCK_DAEMONS.map((d, i) => (
                  <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.75rem 1rem', background: 'rgba(11,20,36,0.5)', borderRadius: '8px', border: '1px solid rgba(226,232,240,0.07)' }}>
                    <div>
                      <div style={{ fontWeight: 600, fontSize: '0.88rem', color: '#F8FAFC' }}>{d.name}</div>
                      <div style={{ fontSize: '0.72rem', color: '#64748B', marginTop: '2px' }}>{d.port}</div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                      <div style={{ textAlign: 'right', marginRight: '0.5rem' }}>
                        <div style={{ fontSize: '0.72rem', color: '#94A3B8' }}>{d.latency}</div>
                        <div style={{ width: '70px', marginTop: '3px' }}>
                          <div className="progress-bar-wrap">
                            <div className="progress-bar-fill" style={{ width: `${d.health}%`, background: d.health > 99 ? 'linear-gradient(90deg, #22C55E, #86EFAC)' : 'linear-gradient(90deg, #F59E0B, #FCD34D)' }} />
                          </div>
                        </div>
                      </div>
                      <span className={`status-chip ${d.status === 'ONLINE' || d.status === 'CONNECTED' || d.status === 'ACTIVE' || d.status === 'LOADED' ? 'green' : 'amber'}`}>
                        <span className="status-dot" />{d.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Security + Events */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              <div className="portal-section-card">
                <div className="section-card-header">
                  <div className="section-card-title"><Shield size={16} color="#F59E0B" /> Security Governance</div>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {[
                    { icon: '🔐', title: 'Database Encryption', desc: 'PostgreSQL tables isolated to institutional tenant AMAES', ok: true },
                    { icon: '📋', title: 'Immutable Audit Log', desc: 'All score overrides require mandatory rationale before commit', ok: true },
                    { icon: '💾', title: 'Storage Guardrail', desc: 'Multi-GB dataset downloads blocked unless admin authorised', ok: true },
                    { icon: '🛡️', title: 'Role Separation', desc: '10 isolated role workspaces with JWT scope enforcement', ok: true },
                    { icon: '🔑', title: 'Token Expiry', desc: 'JWT access token: 30 min • Refresh token: 7 days', ok: true },
                  ].map((item, i) => (
                    <div key={i} style={{ padding: '0.75rem', background: 'rgba(11,20,36,0.5)', borderRadius: '8px', borderLeft: `3px solid ${item.ok ? '#22C55E' : '#EF4444'}`, display: 'flex', gap: '0.65rem', alignItems: 'flex-start' }}>
                      <span style={{ fontSize: '1rem', flexShrink: 0 }}>{item.icon}</span>
                      <div>
                        <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#F8FAFC' }}>{item.title}</div>
                        <div style={{ fontSize: '0.72rem', color: '#94A3B8', marginTop: '2px' }}>{item.desc}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="portal-section-card">
                <div className="section-card-header">
                  <div className="section-card-title"><Zap size={16} color="#F59E0B" /> Recent Events</div>
                </div>
                <div className="timeline">
                  {MOCK_AUDIT.slice(0, 5).map((a, i) => (
                    <div key={i} className="timeline-item">
                      <div className="timeline-dot" style={{ color: a.severity === 'error' ? '#EF4444' : a.severity === 'warning' ? '#F59E0B' : '#22C55E' }} />
                      <div className="timeline-content">
                        <div className="timeline-time">{a.ts} · <strong style={{ color: '#A5B4FC' }}>{a.actor}</strong></div>
                        <div className="timeline-text">{a.action} — <em style={{ color: '#64748B' }}>{a.entity}</em></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── USERS TAB ── */}
      {activeTab === 'users' && (
        <div className="portal-section-card">
          <div className="section-card-header">
            <div className="section-card-title"><Users size={16} color="#818CF8" /> User Administration — 10 Portal Accounts</div>
            <button className="btn btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem' }}>
              <UserPlus size={14} /> Add User
            </button>
          </div>
          <div style={{ overflowX: 'auto' }}>
            <table className="portal-table">
              <thead>
                <tr>
                  <th>#</th><th>Name</th><th>Username</th><th>Role</th><th>Last Login</th><th>Status</th><th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {MOCK_USERS.map((u) => (
                  <tr key={u.id}>
                    <td style={{ color: '#64748B', fontWeight: 400 }}>{u.id}</td>
                    <td>{u.full_name}</td>
                    <td style={{ fontFamily: 'monospace', fontSize: '0.82rem' }}>{u.username}</td>
                    <td>
                      <span className="portal-badge" style={{ background: `${ROLE_COLORS[u.role]}20`, color: ROLE_COLORS[u.role], border: `1px solid ${ROLE_COLORS[u.role]}40`, fontSize: '0.7rem' }}>
                        {u.role.replace('_', ' ')}
                      </span>
                    </td>
                    <td style={{ color: '#64748B', fontSize: '0.82rem' }}>{u.last_login}</td>
                    <td>
                      <span className={`status-chip ${u.active ? 'green' : 'gray'}`}>
                        <span className="status-dot" />{u.active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: '0.35rem' }}>
                        <button className="icon-btn" title="Edit" onClick={() => { setSelectedUser(u); setUserModal(true); }}><Edit size={13} /></button>
                        <button className="icon-btn" title="Toggle Active" style={{ color: u.active ? '#22C55E' : '#EF4444' }}>
                          {u.active ? <ToggleRight size={13} /> : <ToggleLeft size={13} />}
                        </button>
                        <button className="icon-btn" title="Reset Password"><Key size={13} /></button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ── AUDIT TAB ── */}
      {activeTab === 'audit' && (
        <div className="portal-section-card">
          <div className="section-card-header">
            <div className="section-card-title"><Clock size={16} color="#818CF8" /> Immutable Audit Log — Last 24 Hours</div>
            <button className="btn btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem' }}>
              <Download size={14} /> Export CSV
            </button>
          </div>
          <div style={{ overflowX: 'auto' }}>
            <table className="portal-table">
              <thead>
                <tr><th>Timestamp</th><th>Actor</th><th>Action</th><th>Entity</th><th>Severity</th></tr>
              </thead>
              <tbody>
                {MOCK_AUDIT.map((a, i) => (
                  <tr key={i}>
                    <td style={{ fontFamily: 'monospace', fontSize: '0.82rem', color: '#64748B' }}>{a.ts}</td>
                    <td style={{ color: '#A5B4FC', fontFamily: 'monospace', fontSize: '0.82rem' }}>{a.actor}</td>
                    <td>{a.action}</td>
                    <td style={{ color: '#94A3B8', fontSize: '0.82rem' }}>{a.entity}</td>
                    <td>
                      <span className={`status-chip ${a.severity === 'error' ? 'red' : a.severity === 'warning' ? 'amber' : 'green'}`}>
                        <span className="status-dot" />{a.severity}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ── CONFIG TAB ── */}
      {activeTab === 'config' && (
        <div className="split-panel">
          <div className="portal-section-card">
            <div className="section-card-header">
              <div className="section-card-title"><Settings size={16} color="#818CF8" /> AI Model Configuration</div>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {[
                { key: 'Active Model Profile', value: 'minimal_cpu', editable: true },
                { key: 'Semantic Similarity Threshold', value: '0.72', editable: true },
                { key: 'Max Batch Evaluation', value: '20 scripts/run', editable: true },
                { key: 'OCR Engine', value: 'Tesseract 5.3.3 (LSTM)', editable: false },
                { key: 'Embedding Model', value: 'sentence-bert-base-nli-mean', editable: false },
                { key: 'Plagiarism Cosine Threshold', value: '0.85', editable: true },
                { key: 'Auto-publish After Review', value: 'Disabled', editable: true },
              ].map((c, i) => (
                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.75rem 0', borderBottom: '1px solid rgba(226,232,240,0.06)' }}>
                  <span style={{ fontSize: '0.88rem', color: '#CBD5E1' }}>{c.key}</span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <code style={{ background: 'rgba(11,20,36,0.7)', padding: '0.25rem 0.6rem', borderRadius: '5px', fontSize: '0.82rem', color: '#A5B4FC' }}>{c.value}</code>
                    {c.editable && <button className="icon-btn"><Edit size={12} /></button>}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <div className="portal-section-card">
              <div className="section-card-header">
                <div className="section-card-title"><Globe size={16} color="#818CF8" /> Platform Info</div>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem', fontSize: '0.85rem' }}>
                {[
                  ['Institution', 'AMAES Academic Excellence'],
                  ['Platform Version', 'IntelliGrade v2.4.0'],
                  ['OS', 'Windows 11 AMD64'],
                  ['Python Runtime', '3.11.6 / FastAPI 0.115'],
                  ['Database', 'PostgreSQL 15.3'],
                  ['Frontend', 'React 19 + Vite 8'],
                  ['License', 'Institutional — Offline Only'],
                ].map(([k, v], i) => (
                  <div key={i} style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid rgba(226,232,240,0.06)', paddingBottom: '0.5rem' }}>
                    <span style={{ color: '#64748B' }}>{k}</span>
                    <span style={{ color: '#F8FAFC', fontWeight: 600, textAlign: 'right' }}>{v}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="portal-alert warning">
              <AlertTriangle size={16} />
              <div><strong>Storage Guardrail Active.</strong> Model downloads over 2 GB are blocked. Manage via <code>download_datasets.py</code> CLI.</div>
            </div>
          </div>
        </div>
      )}

      {/* User Edit Modal */}
      {userModal && selectedUser && (
        <div className="portal-modal-overlay" onClick={() => setUserModal(false)}>
          <div className="portal-modal-card" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <div className="modal-title"><Edit size={18} /> Edit User: {selectedUser.full_name}</div>
              <button className="modal-close-btn" onClick={() => setUserModal(false)}>✕</button>
            </div>
            <div className="portal-form-group">
              <label className="portal-form-label">Full Name</label>
              <input defaultValue={selectedUser.full_name} className="portal-form-input" />
            </div>
            <div className="portal-form-group">
              <label className="portal-form-label">Username</label>
              <input defaultValue={selectedUser.username} className="portal-form-input" />
            </div>
            <div className="portal-form-group">
              <label className="portal-form-label">Role Portal</label>
              <select defaultValue={selectedUser.role} className="portal-form-select">
                {Object.keys(ROLE_COLORS).map(r => <option key={r} value={r}>{r.replace(/_/g, ' ')}</option>)}
              </select>
            </div>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '0.5rem' }}>
              <button className="btn btn-secondary" onClick={() => setUserModal(false)}>Cancel</button>
              <button className="btn btn-primary" onClick={() => setUserModal(false)}>Save Changes</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
