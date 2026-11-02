import React, { useState } from 'react';
import { Award, Download, HelpCircle, ChevronDown, ChevronUp, BookOpen, TrendingUp, Star, Bell } from 'lucide-react';
import './PortalStyles.css';

const EXAMS = [
  {
    id: 'MCA301',
    name: 'Advanced Database Management Systems',
    date: '2026-10-20',
    published: '2026-10-26',
    maxScore: 20,
    scored: 19.0,
    grade: 'S',
    status: 'CERTIFIED',
    questions: [
      { num: 1, text: 'Explain ACID properties in DBMS.', max: 10, score: 9.5, feedback: 'Demonstrated complete understanding. All 4 ACID properties correctly applied with apt terminology.', criteria: [{ name: 'Atomicity', mark: '2.5/2.5' }, { name: 'Consistency', mark: '2.5/2.5' }, { name: 'Isolation', mark: '2.5/2.5' }, { name: 'Durability', mark: '2.0/2.5' }] },
      { num: 2, text: 'Define Normalization; distinguish 2NF and 3NF.', max: 5, score: 4.5, feedback: 'Excellent explanation of functional dependencies. Minor gap in 2NF vs 3NF comparison table.', criteria: [{ name: 'Normalization Concept', mark: '2.0/2.0' }, { name: '2NF vs 3NF', mark: '2.5/3.0' }] },
      { num: 3, text: 'Clustered vs Non-Clustered Indexing.', max: 5, score: 5.0, feedback: 'Perfect! Flawless distinction of physical sorting vs B+ tree leaf pointer structures.', criteria: [{ name: 'Storage Layout', mark: '2.5/2.5' }, { name: 'B+ Tree', mark: '2.5/2.5' }] },
    ],
  },
  {
    id: 'MCA302',
    name: 'Operating Systems Fundamentals',
    date: '2026-09-15',
    published: '2026-09-22',
    maxScore: 25,
    scored: 21.5,
    grade: 'A+',
    status: 'CERTIFIED',
    questions: [
      { num: 1, text: 'Explain process scheduling algorithms.', max: 10, score: 8.5, feedback: 'Good coverage of FCFS, SJF, and Round Robin. Priority scheduling required more depth.', criteria: [] },
      { num: 2, text: 'Describe deadlock detection and recovery.', max: 15, score: 13.0, feedback: 'Solid understanding of wait-for graph and resource preemption methods.', criteria: [] },
    ],
  },
];

const CGPA_HISTORY = [
  { sem: 'Sem 1 (2024)', cgpa: 8.4 },
  { sem: 'Sem 2 (2025)', cgpa: 8.9 },
  { sem: 'Sem 3 (2025)', cgpa: 9.1 },
  { sem: 'Current', cgpa: 9.5 },
];

export const StudentPortal: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'results' | 'transcript' | 'appeals' | 'notifications'>('results');
  const [selectedExam, setSelectedExam] = useState(EXAMS[0]);
  const [expandedQ, setExpandedQ] = useState<number | null>(1);
  const [appealModal, setAppealModal] = useState(false);
  const [appealSubmitted, setAppealSubmitted] = useState(false);

  const handleAppeal = (e: React.FormEvent) => {
    e.preventDefault();
    setAppealSubmitted(true);
    setTimeout(() => { setAppealModal(false); setAppealSubmitted(false); }, 2500);
  };

  const pct = Math.round((selectedExam.scored / selectedExam.maxScore) * 100);

  return (
    <div className="portal-page">
      <div className="portal-header">
        <div className="portal-header-left">
          <div className="portal-badge-row">
            <span className="portal-badge student">Portal 8: Student Hub</span>
            <span className="status-chip green"><span className="status-dot" /> Privacy-Safe Certified Academic Transcript</span>
          </div>
          <h1>Student Academic Results Portal</h1>
          <p>Welcome, Candidate 24MCA01 (Master of Computer Applications, 2024–26 Batch). View certified exam results, CGPA progression, feedback, and submit re-evaluation appeals.</p>
        </div>
        <div className="portal-header-actions">
          <button onClick={() => setAppealModal(true)} className="btn btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <HelpCircle size={15} /> Re-evaluation Request
          </button>
          <button className="btn btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Download size={15} /> Download Transcript
          </button>
        </div>
      </div>

      {/* Student KPI Strip */}
      <div className="kpi-strip">
        {[
          { icon: '📊', label: 'Current CGPA',     value: '9.5 / 10', delta: 'Semester 3 — Outstanding', color: '#22C55E' },
          { icon: '📄', label: 'Exams Completed',  value: '2',        delta: 'MCA301 & MCA302', color: '#818CF8' },
          { icon: '🏆', label: 'Best Grade',        value: 'S',        delta: 'MCA301 — 95%', color: '#FCD34D' },
          { icon: '🎯', label: 'Overall Average',   value: '92.4%',    delta: 'Across all subjects', color: '#38BDF8' },
        ].map((k, i) => (
          <div key={i} className="kpi-card">
            <div className="kpi-icon" style={{ background: `${k.color}20`, fontSize: '1.2rem' }}>{k.icon}</div>
            <div className="kpi-value" style={{ color: k.color, fontSize: '1.6rem' }}>{k.value}</div>
            <div className="kpi-label">{k.label}</div>
            <div className="kpi-delta flat">{k.delta}</div>
          </div>
        ))}
      </div>

      <div className="portal-tabs">
        {(['results', 'transcript', 'appeals', 'notifications'] as const).map(t => (
          <button key={t} className={`portal-tab ${activeTab === t ? 'active' : ''}`} onClick={() => setActiveTab(t)}>
            {t === 'results' ? '📄 Exam Results' : t === 'transcript' ? '🎓 Academic Transcript' : t === 'appeals' ? '🔔 My Appeals' : '🔔 Notifications'}
          </button>
        ))}
      </div>

      {/* ── RESULTS ── */}
      {activeTab === 'results' && (
        <div className="split-panel left-heavy">
          {/* Exam list */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <div className="portal-section-card">
              <div className="section-card-header">
                <div className="section-card-title"><BookOpen size={16} color="#FDBA74" /> Published Results</div>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                {EXAMS.map(e => (
                  <div
                    key={e.id}
                    className={`candidate-card ${selectedExam.id === e.id ? 'selected' : ''}`}
                    onClick={() => { setSelectedExam(e); setExpandedQ(null); }}
                  >
                    <div className="candidate-avatar" style={{ background: 'rgba(249,115,22,0.2)', color: '#FDBA74' }}>
                      {e.grade}
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: 600, color: '#F8FAFC', fontSize: '0.9rem' }}>{e.id}</div>
                      <div style={{ fontSize: '0.75rem', color: '#94A3B8', marginTop: 1 }}>{e.name}</div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontWeight: 800, color: '#86EFAC', fontSize: '1rem' }}>{e.scored}/{e.maxScore}</div>
                      <span className="status-chip green" style={{ fontSize: '0.65rem' }}><span className="status-dot" />{e.status}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* CGPA Progression */}
            <div className="portal-section-card">
              <div className="section-card-header">
                <div className="section-card-title"><TrendingUp size={15} color="#FDBA74" /> CGPA Progression</div>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                {CGPA_HISTORY.map((h, i) => (
                  <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <div style={{ width: '90px', fontSize: '0.78rem', color: '#94A3B8', flexShrink: 0 }}>{h.sem}</div>
                    <div style={{ flex: 1 }}>
                      <div className="progress-bar-wrap">
                        <div className="progress-bar-fill" style={{ width: `${h.cgpa * 10}%`, background: h.cgpa >= 9 ? 'linear-gradient(90deg,#22C55E,#86EFAC)' : 'linear-gradient(90deg,#F59E0B,#FCD34D)' }} />
                      </div>
                    </div>
                    <div style={{ width: '32px', textAlign: 'right', fontWeight: 800, fontSize: '0.85rem', color: h.cgpa >= 9 ? '#22C55E' : '#F59E0B' }}>{h.cgpa}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Selected Exam Detail */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            {/* Grade Card */}
            <div style={{ background: 'linear-gradient(135deg, rgba(20,36,58,0.95), rgba(11,20,36,0.9))', border: '1px solid rgba(79,70,229,0.35)', borderRadius: 14, padding: '1.5rem', position: 'relative', overflow: 'hidden' }}>
              <div style={{ position: 'absolute', top: -20, right: -20, width: 130, height: 130, background: 'radial-gradient(circle, rgba(79,70,229,0.25) 0%, transparent 70%)' }} />
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
                <div>
                  <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', color: '#A5B4FC', fontWeight: 700, letterSpacing: '0.06em' }}>Official Certified Result</div>
                  <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#F8FAFC', marginTop: 4 }}>{selectedExam.id}: {selectedExam.name}</div>
                  <div style={{ fontSize: '0.78rem', color: '#64748B', marginTop: 3 }}>Exam: {selectedExam.date} · Published: {selectedExam.published}</div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '3rem', fontWeight: 900, color: '#86EFAC', lineHeight: 1 }}>{selectedExam.scored}</div>
                  <div style={{ color: '#64748B', fontSize: '0.9rem' }}>/ {selectedExam.maxScore}</div>
                  <div style={{ marginTop: 4 }}>
                    <span style={{ background: 'rgba(21,128,61,0.2)', color: '#86EFAC', border: '1px solid rgba(21,128,61,0.4)', padding: '0.25rem 0.75rem', borderRadius: 20, fontWeight: 800, fontSize: '0.85rem' }}>
                      Grade {selectedExam.grade} — {pct}%
                    </span>
                  </div>
                </div>
              </div>

              <div style={{ marginTop: '1rem' }}>
                <div className="progress-bar-wrap" style={{ height: 8 }}>
                  <div className="progress-bar-fill" style={{ width: `${pct}%`, background: 'linear-gradient(90deg, #22C55E, #86EFAC)' }} />
                </div>
              </div>
            </div>

            {/* Q-by-Q Feedback */}
            <div className="portal-section-card">
              <div className="section-card-header">
                <div className="section-card-title"><Star size={15} color="#FDBA74" /> Question-wise Feedback</div>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
                {selectedExam.questions.map(q => {
                  const isExp = expandedQ === q.num;
                  const qPct = Math.round((q.score / q.max) * 100);
                  return (
                    <div key={q.num} className="accordion-item">
                      <div className="accordion-header" onClick={() => setExpandedQ(isExp ? null : q.num)}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                          <div className="score-badge">{q.num}</div>
                          <div>
                            <div style={{ fontWeight: 600, color: '#F8FAFC', fontSize: '0.88rem' }}>{q.text}</div>
                            <div style={{ marginTop: 3, width: '150px' }}>
                              <div className="progress-bar-wrap">
                                <div className="progress-bar-fill" style={{ width: `${qPct}%`, background: qPct >= 90 ? 'linear-gradient(90deg,#22C55E,#86EFAC)' : qPct >= 70 ? 'linear-gradient(90deg,#F59E0B,#FCD34D)' : 'linear-gradient(90deg,#EF4444,#FCA5A5)' }} />
                              </div>
                            </div>
                          </div>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                          <div style={{ fontWeight: 800, fontSize: '1.1rem', color: '#86EFAC' }}>{q.score}/{q.max}</div>
                          {isExp ? <ChevronUp size={14} color="#94A3B8" /> : <ChevronDown size={14} color="#94A3B8" />}
                        </div>
                      </div>
                      {isExp && (
                        <div className="accordion-body">
                          <div style={{ background: 'rgba(79,70,229,0.08)', border: '1px solid rgba(79,70,229,0.2)', borderRadius: 8, padding: '0.75rem', fontSize: '0.85rem', color: '#CBD5E1', marginBottom: '0.75rem' }}>
                            <strong style={{ color: '#818CF8' }}>Faculty Feedback:</strong> {q.feedback}
                          </div>
                          {q.criteria.length > 0 && (
                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(160px,1fr))', gap: '0.5rem' }}>
                              {q.criteria.map((c, ci) => (
                                <div key={ci} style={{ padding: '0.5rem 0.75rem', background: 'rgba(20,36,58,0.6)', borderRadius: 6, display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem' }}>
                                  <span style={{ color: '#94A3B8' }}>{c.name}</span>
                                  <span style={{ color: '#86EFAC', fontWeight: 700 }}>{c.mark}</span>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── TRANSCRIPT ── */}
      {activeTab === 'transcript' && (
        <div className="portal-section-card">
          <div className="section-card-header">
            <div className="section-card-title">🎓 Official Academic Transcript — Arjun Reddy (24MCA01)</div>
            <button className="btn btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem' }}>
              <Download size={13} /> Download PDF
            </button>
          </div>
          <div style={{ overflowX: 'auto' }}>
            <table className="portal-table">
              <thead><tr><th>Course Code</th><th>Course Name</th><th>Credits</th><th>Grade</th><th>Grade Points</th><th>Status</th></tr></thead>
              <tbody>
                {[
                  { code: 'MCA301', name: 'Advanced Database Management Systems', credits: 4, grade: 'S',  gp: 10 },
                  { code: 'MCA302', name: 'Operating Systems Fundamentals',       credits: 4, grade: 'A+', gp: 9  },
                  { code: 'MCA303', name: 'Computer Networks & Security',          credits: 3, grade: 'A',  gp: 8  },
                  { code: 'MCA304', name: 'Data Structures & Algorithms',          credits: 4, grade: 'A+', gp: 9  },
                  { code: 'MCA305', name: 'Artificial Intelligence',               credits: 3, grade: 'S',  gp: 10 },
                ].map((c, i) => (
                  <tr key={i}>
                    <td style={{ fontFamily: 'monospace' }}>{c.code}</td>
                    <td>{c.name}</td>
                    <td style={{ color: '#94A3B8', textAlign: 'center' }}>{c.credits}</td>
                    <td style={{ fontWeight: 800, color: c.gp === 10 ? '#22C55E' : c.gp >= 9 ? '#86EFAC' : '#F59E0B' }}>{c.grade}</td>
                    <td style={{ fontWeight: 700 }}>{c.gp}</td>
                    <td><span className="status-chip green"><span className="status-dot" />Certified</span></td>
                  </tr>
                ))}
                <tr style={{ borderTop: '2px solid rgba(79,70,229,0.4)' }}>
                  <td colSpan={2} style={{ fontWeight: 700, color: '#F8FAFC' }}>CGPA (Current)</td>
                  <td style={{ color: '#94A3B8', textAlign: 'center' }}>18</td>
                  <td colSpan={2} style={{ fontWeight: 900, fontSize: '1.1rem', color: '#22C55E' }}>9.50</td>
                  <td><span className="status-chip blue">Ongoing</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ── APPEALS ── */}
      {activeTab === 'appeals' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div className="portal-section-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ fontWeight: 700, color: '#F8FAFC' }}>No active re-evaluation appeals.</div>
                <div style={{ fontSize: '0.82rem', color: '#94A3B8', marginTop: 2 }}>Submit an appeal if you believe your score requires expert re-review.</div>
              </div>
              <button onClick={() => setAppealModal(true)} className="btn btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <HelpCircle size={14} /> New Appeal
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── NOTIFICATIONS ── */}
      {activeTab === 'notifications' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {[
            { icon: '✅', text: 'MCA301 result certified and published by Prof. Anand Sharma.', time: '2026-10-26 16:30', type: 'success' },
            { icon: '📢', text: 'Mid-term examination schedule for Nov 2026 published by Academic Administration.', time: '2026-10-25 09:00', type: 'info' },
            { icon: '🎯', text: 'MCA302 AI evaluation completed. Pending faculty moderation.', time: '2026-09-22 11:45', type: 'info' },
          ].map((n, i) => (
            <div key={i} className={`portal-alert ${n.type === 'success' ? 'success' : 'info'}`}>
              <span style={{ fontSize: '1rem' }}>{n.icon}</span>
              <div style={{ flex: 1 }}>
                <div>{n.text}</div>
                <div style={{ fontSize: '0.72rem', marginTop: 2, opacity: 0.7 }}>{n.time}</div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Appeal Modal */}
      {appealModal && (
        <div className="portal-modal-overlay" onClick={() => setAppealModal(false)}>
          <div className="portal-modal-card" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <div className="modal-title"><HelpCircle size={18} /> Submit Re-evaluation Appeal</div>
              <button className="modal-close-btn" onClick={() => setAppealModal(false)}>✕</button>
            </div>
            {appealSubmitted ? (
              <div className="portal-alert success">
                <Award size={16} />
                <div><strong>Appeal #APP-2026-{Math.floor(Math.random() * 900) + 100} filed!</strong> Your script will be routed to a secondary independent faculty moderator.</div>
              </div>
            ) : (
              <form onSubmit={handleAppeal}>
                <div className="portal-form-group">
                  <label className="portal-form-label">Select Exam</label>
                  <select className="portal-form-select">
                    {EXAMS.map(e => <option key={e.id}>{e.id}: {e.name}</option>)}
                  </select>
                </div>
                <div className="portal-form-group">
                  <label className="portal-form-label">Select Question</label>
                  <select className="portal-form-select">
                    {selectedExam.questions.map(q => <option key={q.num}>Q{q.num}: {q.text}</option>)}
                  </select>
                </div>
                <div className="portal-form-group">
                  <label className="portal-form-label">Academic Justification (Required)</label>
                  <textarea className="portal-form-textarea" required placeholder="Describe the specific grounds for re-examination..." rows={4} />
                </div>
                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                  <button type="button" className="btn btn-secondary" onClick={() => setAppealModal(false)}>Cancel</button>
                  <button type="submit" className="btn btn-primary">Submit Appeal</button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
