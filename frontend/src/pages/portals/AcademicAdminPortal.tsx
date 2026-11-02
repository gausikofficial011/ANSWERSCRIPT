import React, { useState } from 'react';
import { Layers, Calendar, Users, BookOpen, Plus, Edit, ChevronRight, Download, Search, Filter, CheckCircle, Clock, AlertTriangle } from 'lucide-react';
import './PortalStyles.css';

const DEPARTMENTS = [
  { code: 'MCA', name: 'Master of Computer Applications', hod: 'Dr. Suresh Iyer', students: 60, faculty: 8, exams: 12, status: 'active' },
  { code: 'MBA', name: 'Master of Business Administration', hod: 'Prof. Meera Krishnan', students: 80, faculty: 10, exams: 9, status: 'active' },
  { code: 'MTech-CS', name: 'M.Tech Computer Science', hod: 'Dr. Anand Sharma', students: 45, faculty: 6, exams: 8, status: 'active' },
  { code: 'BCA', name: 'Bachelor of Computer Applications', hod: 'Dr. Priya Menon', students: 120, faculty: 12, exams: 15, status: 'active' },
  { code: 'BSc-DS', name: 'B.Sc. Data Science', hod: 'Prof. Rajiv Nair', students: 55, faculty: 7, exams: 6, status: 'review' },
];

const CALENDAR = [
  { date: '2026-11-03', event: 'MCA301 Mid-Term Examination', dept: 'MCA', time: '09:00 AM', room: 'Hall A', type: 'exam' },
  { date: '2026-11-04', event: 'MBA Finance Module Paper', dept: 'MBA', time: '10:00 AM', room: 'Hall B', type: 'exam' },
  { date: '2026-11-05', event: 'MTech Algorithm Design Practical', dept: 'MTech-CS', time: '02:00 PM', room: 'Lab 3', type: 'practical' },
  { date: '2026-11-07', event: 'BCA Database Systems Paper', dept: 'BCA', time: '09:00 AM', room: 'Hall C', type: 'exam' },
  { date: '2026-11-10', event: 'Academic Council Meeting', dept: 'All', time: '03:00 PM', room: 'Boardroom', type: 'meeting' },
  { date: '2026-11-14', event: 'End-Semester Practical Viva', dept: 'MCA', time: '10:00 AM', room: 'Lab 1-4', type: 'viva' },
  { date: '2026-11-21', event: 'Result Publication Deadline', dept: 'All', time: '05:00 PM', room: 'Online', type: 'deadline' },
];

const ANNOUNCEMENTS = [
  { id: 1, title: 'Mid-Semester Result Publication', body: 'All department results to be published by Nov 21 2026. AI evaluation and human moderation must be completed by Nov 18.', priority: 'high', date: '2026-10-26' },
  { id: 2, title: 'New OCR Workflow Mandatory', body: 'From Nov 2026, all answer scripts must pass OCR QA review before AI scoring. OCR operators have been briefed.', priority: 'medium', date: '2026-10-24' },
  { id: 3, title: 'Faculty Evaluation Training Session', body: 'A mandatory rubric calibration workshop will be held on Nov 1, 2026 for all evaluating faculty members.', priority: 'low', date: '2026-10-20' },
];

const ENROLMENTS = [
  { id: 'MCA2024-001', name: 'Arjun Reddy',   dept: 'MCA', year: '1st', batch: '2024-26', gpa: 9.1, status: 'enrolled' },
  { id: 'MCA2024-002', name: 'Priya Singh',   dept: 'MCA', year: '1st', batch: '2024-26', gpa: 8.7, status: 'enrolled' },
  { id: 'MBA2024-001', name: 'Rohan Mehta',   dept: 'MBA', year: '1st', batch: '2024-26', gpa: 8.3, status: 'enrolled' },
  { id: 'BCA2023-005', name: 'Kavitha Rao',   dept: 'BCA', year: '3rd', batch: '2023-26', gpa: 9.4, status: 'enrolled' },
  { id: 'MCA2023-009', name: 'Deepak Varma',  dept: 'MCA', year: '2nd', batch: '2023-25', gpa: 7.8, status: 'probation' },
  { id: 'MBA2024-003', name: 'Sneha Pillai',  dept: 'MBA', year: '1st', batch: '2024-26', gpa: 9.0, status: 'enrolled' },
];

const TYPE_COLORS: Record<string, string> = {
  exam: 'blue', practical: 'purple', meeting: 'amber', viva: 'green', deadline: 'red'
};

export const AcademicAdminPortal: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'departments' | 'calendar' | 'enrolments' | 'announcements'>('departments');
  const [searchQ, setSearchQ] = useState('');
  const [newAnnModal, setNewAnnModal] = useState(false);

  return (
    <div className="portal-page">
      {/* Header */}
      <div className="portal-header">
        <div className="portal-header-left">
          <div className="portal-badge-row">
            <span className="portal-badge admin">Portal 2: Academic Admin</span>
            <span className="status-chip green"><span className="status-dot" /> Active Session</span>
          </div>
          <h1>Academic Administration Office</h1>
          <p>Manage departments, examination calendar, student enrolments, faculty assignments, and official institutional announcements.</p>
        </div>
        <div className="portal-header-actions">
          <button className="btn btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Download size={15} /> Export Report
          </button>
          <button className="btn btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }} onClick={() => setNewAnnModal(true)}>
            <Plus size={15} /> New Announcement
          </button>
        </div>
      </div>

      {/* KPI Strip */}
      <div className="kpi-strip">
        {[
          { icon: '🏛️', label: 'Departments', value: '5', delta: '4 active · 1 review' },
          { icon: '👨‍🎓', label: 'Total Students', value: '360', delta: '+12 this semester' },
          { icon: '👩‍🏫', label: 'Faculty Members', value: '43', delta: 'Across 5 programmes' },
          { icon: '📄', label: 'Scheduled Exams', value: '50', delta: 'Nov–Dec 2026 Batch' },
        ].map((k, i) => (
          <div key={i} className="kpi-card">
            <div className="kpi-icon" style={{ background: 'rgba(79,70,229,0.2)', fontSize: '1.2rem' }}>{k.icon}</div>
            <div className="kpi-value">{k.value}</div>
            <div className="kpi-label">{k.label}</div>
            <div className="kpi-delta flat">{k.delta}</div>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="portal-tabs">
        {(['departments', 'calendar', 'enrolments', 'announcements'] as const).map(t => (
          <button key={t} className={`portal-tab ${activeTab === t ? 'active' : ''}`} onClick={() => setActiveTab(t)}>
            {t === 'departments' ? '🏛️ Departments' : t === 'calendar' ? '📅 Exam Calendar' : t === 'enrolments' ? '👨‍🎓 Enrolments' : '📢 Announcements'}
          </button>
        ))}
      </div>

      {/* ── DEPARTMENTS ── */}
      {activeTab === 'departments' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {DEPARTMENTS.map((d, i) => (
            <div key={i} className="portal-section-card" style={{ cursor: 'pointer' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
                <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                  <div style={{ width: 52, height: 52, borderRadius: 12, background: 'rgba(79,70,229,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 800, fontSize: '0.85rem', color: '#818CF8' }}>{d.code}</div>
                  <div>
                    <div style={{ fontSize: '1rem', fontWeight: 700, color: '#F8FAFC' }}>{d.name}</div>
                    <div style={{ fontSize: '0.8rem', color: '#94A3B8', marginTop: 2 }}>HoD: {d.hod}</div>
                  </div>
                </div>
                <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'center' }}>
                  {[
                    { label: 'Students', val: d.students, icon: '👥' },
                    { label: 'Faculty', val: d.faculty, icon: '👩‍🏫' },
                    { label: 'Exams', val: d.exams, icon: '📄' },
                  ].map((s, si) => (
                    <div key={si} style={{ textAlign: 'center' }}>
                      <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#F8FAFC' }}>{s.val}</div>
                      <div style={{ fontSize: '0.7rem', color: '#64748B' }}>{s.icon} {s.label}</div>
                    </div>
                  ))}
                  <span className={`status-chip ${d.status === 'active' ? 'green' : 'amber'}`}><span className="status-dot" />{d.status}</span>
                  <button className="icon-btn"><ChevronRight size={14} /></button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ── CALENDAR ── */}
      {activeTab === 'calendar' && (
        <div className="portal-section-card">
          <div className="section-card-header">
            <div className="section-card-title"><Calendar size={16} color="#818CF8" /> Examination Calendar — November 2026</div>
            <button className="btn btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem' }}>
              <Plus size={13} /> Schedule Event
            </button>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
            {CALENDAR.map((ev, i) => (
              <div key={i} style={{ display: 'flex', gap: '1rem', padding: '0.9rem 1.1rem', background: 'rgba(11,20,36,0.5)', borderRadius: 8, border: '1px solid rgba(226,232,240,0.07)', alignItems: 'center' }}>
                <div style={{ width: 52, flexShrink: 0, textAlign: 'center' }}>
                  <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#818CF8' }}>{ev.date.split('-')[2]}</div>
                  <div style={{ fontSize: '0.68rem', color: '#64748B', textTransform: 'uppercase' }}>Nov</div>
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 600, color: '#F8FAFC', fontSize: '0.9rem' }}>{ev.event}</div>
                  <div style={{ fontSize: '0.75rem', color: '#94A3B8', marginTop: 2 }}>{ev.time} · {ev.room} · {ev.dept}</div>
                </div>
                <span className={`status-chip ${TYPE_COLORS[ev.type] || 'blue'}`}>{ev.type}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── ENROLMENTS ── */}
      {activeTab === 'enrolments' && (
        <div className="portal-section-card">
          <div className="section-card-header">
            <div className="section-card-title"><Users size={16} color="#818CF8" /> Student Enrolment Register</div>
            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
              <div style={{ position: 'relative' }}>
                <Search size={14} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: '#64748B' }} />
                <input
                  className="portal-form-input"
                  style={{ paddingLeft: '2rem', width: '220px' }}
                  placeholder="Search student..."
                  value={searchQ}
                  onChange={e => setSearchQ(e.target.value)}
                />
              </div>
            </div>
          </div>
          <div style={{ overflowX: 'auto' }}>
            <table className="portal-table">
              <thead><tr><th>Roll No.</th><th>Student Name</th><th>Programme</th><th>Year</th><th>Batch</th><th>CGPA</th><th>Status</th><th>Actions</th></tr></thead>
              <tbody>
                {ENROLMENTS.filter(s => s.name.toLowerCase().includes(searchQ.toLowerCase())).map((s, i) => (
                  <tr key={i}>
                    <td style={{ fontFamily: 'monospace' }}>{s.id}</td>
                    <td>{s.name}</td>
                    <td><span className="portal-badge teacher">{s.dept}</span></td>
                    <td style={{ color: '#94A3B8' }}>{s.year}</td>
                    <td style={{ color: '#94A3B8' }}>{s.batch}</td>
                    <td style={{ fontWeight: 800, color: s.gpa >= 9 ? '#22C55E' : s.gpa >= 8 ? '#F59E0B' : '#EF4444' }}>{s.gpa}</td>
                    <td><span className={`status-chip ${s.status === 'enrolled' ? 'green' : 'amber'}`}><span className="status-dot" />{s.status}</span></td>
                    <td><button className="icon-btn"><Edit size={12} /></button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ── ANNOUNCEMENTS ── */}
      {activeTab === 'announcements' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {ANNOUNCEMENTS.map(a => (
            <div key={a.id} className="portal-section-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', gap: '0.65rem', alignItems: 'center', marginBottom: '0.5rem' }}>
                    <span className={`status-chip ${a.priority === 'high' ? 'red' : a.priority === 'medium' ? 'amber' : 'green'}`}>
                      <span className="status-dot" />{a.priority} priority
                    </span>
                    <span style={{ fontSize: '0.75rem', color: '#64748B' }}>Published: {a.date}</span>
                  </div>
                  <div style={{ fontSize: '1rem', fontWeight: 700, color: '#F8FAFC', marginBottom: '0.4rem' }}>{a.title}</div>
                  <div style={{ fontSize: '0.88rem', color: '#94A3B8', lineHeight: 1.55 }}>{a.body}</div>
                </div>
                <button className="icon-btn"><Edit size={13} /></button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* New Announcement Modal */}
      {newAnnModal && (
        <div className="portal-modal-overlay" onClick={() => setNewAnnModal(false)}>
          <div className="portal-modal-card" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <div className="modal-title">📢 New Announcement</div>
              <button className="modal-close-btn" onClick={() => setNewAnnModal(false)}>✕</button>
            </div>
            <div className="portal-form-group">
              <label className="portal-form-label">Title</label>
              <input className="portal-form-input" placeholder="Announcement title..." />
            </div>
            <div className="portal-form-group">
              <label className="portal-form-label">Priority Level</label>
              <select className="portal-form-select">
                <option>High</option><option>Medium</option><option>Low</option>
              </select>
            </div>
            <div className="portal-form-group">
              <label className="portal-form-label">Target Audience</label>
              <select className="portal-form-select">
                <option>All Portals</option><option>Students Only</option><option>Faculty Only</option>
              </select>
            </div>
            <div className="portal-form-group">
              <label className="portal-form-label">Message Body</label>
              <textarea className="portal-form-textarea" placeholder="Write announcement content..." rows={5} />
            </div>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
              <button className="btn btn-secondary" onClick={() => setNewAnnModal(false)}>Cancel</button>
              <button className="btn btn-primary" onClick={() => setNewAnnModal(false)}>Publish Announcement</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
