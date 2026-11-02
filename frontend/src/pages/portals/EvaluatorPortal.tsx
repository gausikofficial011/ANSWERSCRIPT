import React, { useState } from 'react';
import { UserCheck, CheckCircle, Edit, Download, AlertTriangle, ChevronDown, ChevronUp, MessageSquare, ThumbsUp, ThumbsDown } from 'lucide-react';
import './PortalStyles.css';

const SCRIPTS_TO_REVIEW = [
  { id: 'SS-2025-001', student: 'Arjun Reddy', roll: '24MCA01', aiScore: 13.7, maxScore: 15, questions: 3, status: 'pending_review', aiConf: 94.2 },
  { id: 'SS-2025-002', student: 'Priya Singh', roll: '24MCA02', aiScore: 7.8, maxScore: 10, questions: 1, status: 'overridden', aiConf: 82.3 },
  { id: 'SS-2025-003', student: 'Rohan Mehta', roll: '24MCA03', aiScore: 12.4, maxScore: 15, questions: 3, status: 'approved', aiConf: 89.7 },
  { id: 'SS-2025-004', student: 'Kavitha Rao', roll: '24MCA04', aiScore: 14.5, maxScore: 15, questions: 3, status: 'approved', aiConf: 97.1 },
  { id: 'SS-2025-005', student: 'Deepak Varma', roll: '24MCA05', aiScore: 9.2, maxScore: 15, questions: 3, status: 'pending_review', aiConf: 76.5 },
];

const SELECTED_DETAIL = {
  questions: [
    { num: 1, text: 'Explain ACID properties.', maxMark: 10, aiScore: 9.2, teacherScore: null as number | null, aiJustification: 'Strong coverage of all 4 ACID properties with appropriate terminology. Minor lack of concrete examples.', rubricCriteria: [{ name: 'Atomicity', ai: 2.5, max: 2.5 }, { name: 'Consistency', ai: 2.5, max: 2.5 }, { name: 'Isolation', ai: 2.3, max: 2.5 }, { name: 'Durability', ai: 1.9, max: 2.5 }] },
    { num: 2, text: 'Define Normalization. Distinguish 2NF vs 3NF.', maxMark: 5, aiScore: 4.5, teacherScore: null as number | null, aiJustification: 'Good conceptual understanding. 2NF criteria clearly explained but 3NF comparison lacked depth.', rubricCriteria: [{ name: 'Normalization', ai: 2.0, max: 2.0 }, { name: '2NF vs 3NF', ai: 2.5, max: 3.0 }] },
  ]
};

export const EvaluatorPortal: React.FC = () => {
  const [selectedScript, setSelectedScript] = useState(SCRIPTS_TO_REVIEW[0]);
  const [expandedQ, setExpandedQ] = useState<number | null>(1);
  const [overrides, setOverrides] = useState<Record<number, number>>({});
  const [comments, setComments] = useState<Record<number, string>>({});
  const [overrideReason, setOverrideReason] = useState<Record<number, string>>({});
  const [approveModal, setApproveModal] = useState(false);
  const [approved, setApproved] = useState(false);

  const setOverride = (qNum: number, val: string) => {
    const n = parseFloat(val);
    if (!isNaN(n)) setOverrides(prev => ({ ...prev, [qNum]: n }));
  };

  const handleApprove = () => { setApproved(true); setApproveModal(false); };

  return (
    <div className="portal-page">
      <div className="portal-header">
        <div className="portal-header-left">
          <div className="portal-badge-row">
            <span className="portal-badge eval">Portal 6: Evaluator</span>
            <span className="status-chip amber"><span className="status-dot" /> 2 Pending Review</span>
          </div>
          <h1>Teacher Evaluator & Moderator Workspace</h1>
          <p>Side-by-side review of AI-scored scripts, score override with mandatory justification, and moderation approval before official publication.</p>
        </div>
        <div className="portal-header-actions">
          <button className="btn btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Download size={15} /> Export Moderation Log
          </button>
          <button className="btn btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }} onClick={() => setApproveModal(true)}>
            <CheckCircle size={15} /> Approve & Publish
          </button>
        </div>
      </div>

      {approved && (
        <div className="portal-alert success">
          <CheckCircle size={15} />
          <strong>Script SS-2025-001 approved and certified!</strong> Student will receive published result notification.
        </div>
      )}

      {/* KPI Strip */}
      <div className="kpi-strip">
        {[
          { icon: '📋', label: 'To Review', value: '2', delta: 'Pending moderation' },
          { icon: '✅', label: 'Approved', value: '28', delta: 'Certified & published' },
          { icon: '🔄', label: 'Overridden', value: '4', delta: 'With documented reason' },
          { icon: '📊', label: 'Agreement Rate', value: '91.2%', delta: 'AI vs Teacher score' },
        ].map((k, i) => (
          <div key={i} className="kpi-card">
            <div className="kpi-icon" style={{ background: 'rgba(79,70,229,0.2)', fontSize: '1.2rem' }}>{k.icon}</div>
            <div className="kpi-value">{k.value}</div>
            <div className="kpi-label">{k.label}</div>
            <div className="kpi-delta flat">{k.delta}</div>
          </div>
        ))}
      </div>

      <div className="split-panel left-heavy">
        {/* Script Queue */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div className="portal-section-card">
            <div className="section-card-header">
              <div className="section-card-title"><UserCheck size={16} color="#86EFAC" /> Moderation Queue</div>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {SCRIPTS_TO_REVIEW.map(s => (
                <div key={s.id} className={`candidate-card ${selectedScript.id === s.id ? 'selected' : ''}`} onClick={() => setSelectedScript(s)}>
                  <div className="candidate-avatar">{s.student.charAt(0)}</div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600, color: '#F8FAFC', fontSize: '0.88rem' }}>{s.student}</div>
                    <div style={{ fontSize: '0.72rem', color: '#94A3B8' }}>{s.id} · AI Conf: {s.aiConf}%</div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontWeight: 800, color: '#86EFAC', fontSize: '0.95rem' }}>{s.aiScore}/{s.maxScore}</div>
                    <span className={`status-chip ${s.status === 'approved' ? 'green' : s.status === 'overridden' ? 'amber' : 'blue'}`} style={{ fontSize: '0.65rem' }}>
                      <span className="status-dot" />{s.status.replace('_', ' ')}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Review Panel */}
        <div className="portal-section-card">
          <div className="section-card-header">
            <div className="section-card-title"><Edit size={16} color="#86EFAC" /> Review: {selectedScript.student} ({selectedScript.id})</div>
          </div>

          {SELECTED_DETAIL.questions.map(q => {
            const isExp = expandedQ === q.num;
            const finalScore = overrides[q.num] !== undefined ? overrides[q.num] : q.aiScore;
            const changed = overrides[q.num] !== undefined && overrides[q.num] !== q.aiScore;
            return (
              <div key={q.num} className="accordion-item" style={{ marginBottom: '0.75rem' }}>
                <div className="accordion-header" onClick={() => setExpandedQ(isExp ? null : q.num)}>
                  <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                    <div className="score-badge">{q.num}</div>
                    <div>
                      <div style={{ fontWeight: 600, color: '#F8FAFC', fontSize: '0.88rem' }}>{q.text}</div>
                      {changed && <span className="status-chip amber" style={{ fontSize: '0.65rem', marginTop: 2 }}>Score overridden</span>}
                    </div>
                  </div>
                  <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontSize: '0.72rem', color: '#64748B' }}>AI: {q.aiScore}</div>
                      <div style={{ fontWeight: 800, color: changed ? '#F59E0B' : '#86EFAC', fontSize: '1rem' }}>{finalScore}/{q.maxMark}</div>
                    </div>
                    {isExp ? <ChevronUp size={14} color="#94A3B8" /> : <ChevronDown size={14} color="#94A3B8" />}
                  </div>
                </div>

                {isExp && (
                  <div className="accordion-body">
                    {/* Rubric Criteria Side-by-Side */}
                    <div style={{ marginBottom: '1rem' }}>
                      <div style={{ fontSize: '0.78rem', color: '#94A3B8', fontWeight: 700, textTransform: 'uppercase', marginBottom: '0.5rem' }}>Rubric Criteria Breakdown</div>
                      <table className="portal-table">
                        <thead><tr><th>Criterion</th><th>AI Score</th><th>Max</th></tr></thead>
                        <tbody>
                          {q.rubricCriteria.map((c, ci) => (
                            <tr key={ci}>
                              <td>{c.name}</td>
                              <td style={{ color: '#86EFAC', fontWeight: 700 }}>{c.ai}</td>
                              <td style={{ color: '#64748B' }}>{c.max}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>

                    {/* AI Justification */}
                    <div style={{ background: 'rgba(79,70,229,0.08)', border: '1px solid rgba(79,70,229,0.2)', borderRadius: 8, padding: '0.75rem', marginBottom: '1rem', fontSize: '0.85rem', color: '#CBD5E1' }}>
                      <strong style={{ color: '#818CF8' }}>AI Justification:</strong> {q.aiJustification}
                    </div>

                    {/* Override Controls */}
                    <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-end', marginBottom: '0.75rem' }}>
                      <div style={{ flex: 1 }}>
                        <label className="portal-form-label" style={{ marginBottom: '0.3rem', display: 'block' }}>Override Score (/{q.maxMark})</label>
                        <input
                          type="number"
                          min={0} max={q.maxMark} step={0.5}
                          className="portal-form-input"
                          defaultValue={q.aiScore}
                          onChange={e => setOverride(q.num, e.target.value)}
                        />
                      </div>
                      <button className="icon-btn" title="Accept AI score" onClick={() => setOverrides(prev => { const n = {...prev}; delete n[q.num]; return n; })}><ThumbsUp size={14} /></button>
                    </div>

                    {changed && (
                      <div className="portal-form-group">
                        <label className="portal-form-label">Override Justification (Required)</label>
                        <textarea
                          className="portal-form-textarea"
                          placeholder="Mandatory: explain reason for score change..."
                          rows={3}
                          value={overrideReason[q.num] || ''}
                          onChange={e => setOverrideReason(prev => ({ ...prev, [q.num]: e.target.value }))}
                        />
                      </div>
                    )}

                    <div className="portal-form-group">
                      <label className="portal-form-label">Faculty Comment (Optional)</label>
                      <textarea
                        className="portal-form-textarea"
                        placeholder="Add feedback for student..."
                        rows={2}
                        value={comments[q.num] || ''}
                        onChange={e => setComments(prev => ({ ...prev, [q.num]: e.target.value }))}
                      />
                    </div>
                  </div>
                )}
              </div>
            );
          })}

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '0.5rem' }}>
            <button className="btn btn-secondary">Save Draft</button>
            <button className="btn btn-primary" onClick={() => setApproveModal(true)}>
              <CheckCircle size={14} /> Certify & Approve
            </button>
          </div>
        </div>
      </div>

      {/* Approve Modal */}
      {approveModal && (
        <div className="portal-modal-overlay" onClick={() => setApproveModal(false)}>
          <div className="portal-modal-card" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <div className="modal-title"><CheckCircle size={18} color="#22C55E" /> Certify & Publish Score</div>
              <button className="modal-close-btn" onClick={() => setApproveModal(false)}>✕</button>
            </div>
            <div className="portal-alert info" style={{ marginBottom: '1.25rem' }}>
              <AlertTriangle size={15} /> This action is <strong>irreversible</strong>. The certified score will be published to the student's academic record.
            </div>
            <p style={{ fontSize: '0.88rem', color: '#94A3B8', marginBottom: '1.25rem' }}>
              Certifying result for <strong style={{ color: '#F8FAFC' }}>{selectedScript.student}</strong> ({selectedScript.id}) with final score <strong style={{ color: '#86EFAC' }}>{selectedScript.aiScore}/{selectedScript.maxScore}</strong>.
            </p>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
              <button className="btn btn-secondary" onClick={() => setApproveModal(false)}>Cancel</button>
              <button className="btn btn-primary" onClick={handleApprove}>Certify & Publish</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
