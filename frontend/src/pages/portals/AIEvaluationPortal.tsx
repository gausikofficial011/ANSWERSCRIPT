import React, { useState } from 'react';
import { Cpu, Zap, CheckCircle, AlertTriangle, RefreshCw, Download, ChevronDown, ChevronUp, Brain, Target, BarChart2, BookOpen } from 'lucide-react';
import './PortalStyles.css';

const SCRIPTS = [
  {
    id: 'SS-2025-001', student: 'Arjun Reddy', roll: '24MCA01',
    questions: [
      {
        num: 1, text: 'Explain ACID properties in Database Management Systems.',
        maxMark: 10, aiScore: 9.2, confidence: 94.5,
        modelAnswer: 'ACID properties (Atomicity, Consistency, Isolation, Durability) ensure reliable database transactions...',
        studentAnswer: 'ACID stands for Atomicity, Consistency, Isolation, and Durability. These are four key properties that guarantee database transactions are processed reliably. Atomicity ensures all operations in a transaction complete or none do. Consistency ensures database remains in valid state. Isolation ensures transactions run independently. Durability ensures committed transactions survive system failures.',
        conceptCoverage: { 'Atomicity': 100, 'Consistency': 100, 'Isolation': 90, 'Durability': 85, 'Examples': 70 },
        semanticSim: 0.91,
        evidenceSpans: [
          { text: 'Atomicity ensures all operations in a transaction complete or none do', type: 'keyword' },
          { text: 'Consistency ensures database remains in valid state', type: 'keyword' },
          { text: 'Isolation ensures transactions run independently', type: 'concept' },
        ],
        deductions: [],
      },
      {
        num: 2, text: 'Define Normalization and distinguish between 2NF and 3NF.',
        maxMark: 5, aiScore: 4.5, confidence: 88.2,
        modelAnswer: 'Normalization organizes data to reduce redundancy. 2NF: No partial dependency. 3NF: No transitive dependency.',
        studentAnswer: 'Normalization is the process of organizing a database to reduce redundancy and improve data integrity. 2NF requires that all non-key attributes are fully functionally dependent on the primary key, eliminating partial dependencies. 3NF additionally requires that there are no transitive dependencies.',
        conceptCoverage: { 'Normalization Definition': 100, '2NF Criteria': 90, '3NF Criteria': 85, 'Comparison Table': 60 },
        semanticSim: 0.87,
        evidenceSpans: [
          { text: 'reduce redundancy and improve data integrity', type: 'keyword' },
          { text: 'fully functionally dependent on the primary key', type: 'concept' },
        ],
        deductions: [{ reason: 'No comparison table provided', marks: -0.5 }],
      },
    ],
    totalScore: 13.7,
    maxTotal: 15,
    status: 'completed',
    processingTime: '2.34s',
    modelProfile: 'sentence-bert-base',
  },
  {
    id: 'SS-2025-002', student: 'Priya Singh', roll: '24MCA02',
    questions: [
      {
        num: 1, text: 'Explain ACID properties in Database Management Systems.',
        maxMark: 10, aiScore: 7.8, confidence: 82.3,
        modelAnswer: 'ACID properties ensure reliable database transactions...',
        studentAnswer: 'ACID properties are important for databases. Atomicity means either all parts of transaction complete or none. Consistency keeps the database valid. But I am not entirely sure about Isolation and Durability definitions.',
        conceptCoverage: { 'Atomicity': 90, 'Consistency': 75, 'Isolation': 40, 'Durability': 30, 'Examples': 0 },
        semanticSim: 0.74,
        evidenceSpans: [{ text: 'either all parts of transaction complete or none', type: 'keyword' }],
        deductions: [{ reason: 'Incomplete coverage of Isolation & Durability', marks: -2.0 }, { reason: 'No examples provided', marks: -0.2 }],
      },
    ],
    totalScore: 7.8,
    maxTotal: 10,
    status: 'completed',
    processingTime: '1.91s',
    modelProfile: 'sentence-bert-base',
  },
];

export const AIEvaluationPortal: React.FC = () => {
  const [selectedScript, setSelectedScript] = useState(SCRIPTS[0]);
  const [expandedQ, setExpandedQ] = useState<number | null>(1);
  const [runningBatch, setRunningBatch] = useState(false);
  const [batchDone, setBatchDone] = useState(false);

  const handleBatchRun = () => {
    setRunningBatch(true);
    setTimeout(() => { setRunningBatch(false); setBatchDone(true); }, 3000);
  };

  return (
    <div className="portal-page">
      {/* Header */}
      <div className="portal-header">
        <div className="portal-header-left">
          <div className="portal-badge-row">
            <span className="portal-badge eval">Portal 5: AI Engine</span>
            <span className="live-indicator"><span className="live-dot" />SentenceBERT Active</span>
            <span className="status-chip green"><span className="status-dot" /> Model: minimal_cpu</span>
          </div>
          <h1>AI Evaluation Diagnostics Engine</h1>
          <p>Evidence-grounded semantic scoring with concept coverage analysis, cosine similarity maps, and explainable rubric-aligned evaluation feedback.</p>
        </div>
        <div className="portal-header-actions">
          <button className="btn btn-secondary" onClick={handleBatchRun} disabled={runningBatch} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <RefreshCw size={15} className={runningBatch ? 'pulse-icon' : ''} />
            {runningBatch ? 'Processing Batch...' : 'Run Batch Evaluation'}
          </button>
          <button className="btn btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Download size={15} /> Export AI Report
          </button>
        </div>
      </div>

      {/* KPI Strip */}
      <div className="kpi-strip">
        {[
          { icon: '📄', label: 'Scripts Scored', value: '42', delta: 'MCA301 batch complete' },
          { icon: '🎯', label: 'Avg AI Confidence', value: '91.3%', delta: 'Above 85% baseline' },
          { icon: '⚡', label: 'Avg Score Time', value: '2.1s', delta: 'Per script (local CPU)' },
          { icon: '🧠', label: 'Concept Hit Rate', value: '87.4%', delta: 'Across rubric criteria' },
        ].map((k, i) => (
          <div key={i} className="kpi-card">
            <div className="kpi-icon" style={{ background: 'rgba(109,40,217,0.2)', fontSize: '1.2rem' }}>{k.icon}</div>
            <div className="kpi-value">{k.value}</div>
            <div className="kpi-label">{k.label}</div>
            <div className="kpi-delta flat">{k.delta}</div>
          </div>
        ))}
      </div>

      {batchDone && (
        <div className="portal-alert success">
          <CheckCircle size={16} />
          <strong>Batch evaluation complete!</strong> 6 scripts scored. Average confidence: 89.4%. Ready for human moderation.
        </div>
      )}

      <div className="split-panel left-heavy">
        {/* Script Selector */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div className="portal-section-card">
            <div className="section-card-header">
              <div className="section-card-title"><Cpu size={16} color="#C4B5FD" /> Scored Scripts</div>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {SCRIPTS.map(s => (
                <div key={s.id} className={`candidate-card ${selectedScript.id === s.id ? 'selected' : ''}`} onClick={() => setSelectedScript(s)}>
                  <div className="candidate-avatar">{s.student.charAt(0)}</div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600, color: '#F8FAFC', fontSize: '0.88rem' }}>{s.student}</div>
                    <div style={{ fontSize: '0.72rem', color: '#94A3B8' }}>{s.id} · {s.roll}</div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontWeight: 800, fontSize: '1rem', color: '#86EFAC' }}>{s.totalScore}/{s.maxTotal}</div>
                    <div style={{ fontSize: '0.72rem', color: '#64748B' }}>⏱ {s.processingTime}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Model Info Card */}
          <div className="portal-section-card">
            <div className="section-card-header">
              <div className="section-card-title"><Brain size={15} color="#C4B5FD" /> Active Model Profile</div>
            </div>
            <div style={{ fontSize: '0.85rem', display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
              {[
                ['Model', selectedScript.modelProfile],
                ['Embedding Dims', '768d CLS-pooled'],
                ['Similarity Metric', 'Cosine Similarity'],
                ['Scoring Mode', 'Rubric-Aligned Weighted'],
                ['Processing Time', selectedScript.processingTime],
                ['Threshold (Pass)', '> 0.65 cosine'],
              ].map(([k, v], i) => (
                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid rgba(226,232,240,0.06)', paddingBottom: '0.45rem' }}>
                  <span style={{ color: '#64748B' }}>{k}</span>
                  <code style={{ background: 'rgba(109,40,217,0.15)', color: '#C4B5FD', padding: '1px 6px', borderRadius: 4, fontSize: '0.78rem' }}>{v}</code>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right: Question Breakdown */}
        <div className="portal-section-card">
          <div className="section-card-header">
            <div className="section-card-title">
              <Target size={16} color="#C4B5FD" />
              AI Evaluation Breakdown — {selectedScript.student}
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#86EFAC' }}>
                {selectedScript.totalScore} <span style={{ fontSize: '0.9rem', color: '#94A3B8' }}>/ {selectedScript.maxTotal}</span>
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {selectedScript.questions.map(q => {
              const isExp = expandedQ === q.num;
              const pct = (q.aiScore / q.maxMark) * 100;
              return (
                <div key={q.num} className="accordion-item">
                  <div className="accordion-header" onClick={() => setExpandedQ(isExp ? null : q.num)}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                      <div className="score-badge">{q.num}</div>
                      <div>
                        <div style={{ fontWeight: 600, color: '#F8FAFC', fontSize: '0.88rem' }}>{q.text}</div>
                        <div style={{ marginTop: '4px', width: '200px' }}>
                          <div className="progress-bar-wrap">
                            <div className="progress-bar-fill" style={{ width: `${pct}%`, background: pct > 85 ? 'linear-gradient(90deg, #22C55E, #86EFAC)' : pct > 65 ? 'linear-gradient(90deg, #F59E0B, #FCD34D)' : 'linear-gradient(90deg, #EF4444, #FCA5A5)' }} />
                          </div>
                        </div>
                      </div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                      <div style={{ textAlign: 'right' }}>
                        <div style={{ fontWeight: 800, fontSize: '1.1rem', color: pct > 85 ? '#86EFAC' : '#F59E0B' }}>{q.aiScore}/{q.maxMark}</div>
                        <div style={{ fontSize: '0.72rem', color: '#64748B' }}>Conf: {q.confidence.toFixed(1)}%</div>
                      </div>
                      {isExp ? <ChevronUp size={14} color="#94A3B8" /> : <ChevronDown size={14} color="#94A3B8" />}
                    </div>
                  </div>

                  {isExp && (
                    <div className="accordion-body">
                      {/* Semantic Similarity */}
                      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
                        <div style={{ background: 'rgba(79,70,229,0.1)', padding: '0.6rem 1rem', borderRadius: 8, border: '1px solid rgba(79,70,229,0.25)' }}>
                          <div style={{ fontSize: '0.7rem', color: '#94A3B8', marginBottom: 2 }}>Cosine Similarity</div>
                          <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#818CF8' }}>{q.semanticSim.toFixed(2)}</div>
                        </div>
                        {q.deductions.length > 0 && q.deductions.map((d, di) => (
                          <div key={di} style={{ background: 'rgba(185,28,28,0.1)', padding: '0.6rem 1rem', borderRadius: 8, border: '1px solid rgba(185,28,28,0.25)' }}>
                            <div style={{ fontSize: '0.7rem', color: '#94A3B8', marginBottom: 2 }}>Deduction</div>
                            <div style={{ fontSize: '0.78rem', color: '#FCA5A5' }}>{d.reason} ({d.marks})</div>
                          </div>
                        ))}
                      </div>

                      {/* Concept Coverage */}
                      <div style={{ marginBottom: '1rem' }}>
                        <div style={{ fontSize: '0.78rem', fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', marginBottom: '0.5rem' }}>Concept Coverage</div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                          {Object.entries(q.conceptCoverage).map(([concept, pct]) => (
                            <div key={concept} style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                              <div style={{ width: '130px', fontSize: '0.78rem', color: '#CBD5E1', flexShrink: 0 }}>{concept}</div>
                              <div style={{ flex: 1 }}>
                                <div className="progress-bar-wrap">
                                  <div className="progress-bar-fill" style={{ width: `${pct}%`, background: pct > 80 ? 'linear-gradient(90deg, #22C55E, #86EFAC)' : pct > 50 ? 'linear-gradient(90deg, #F59E0B, #FCD34D)' : 'linear-gradient(90deg, #EF4444, #FCA5A5)' }} />
                                </div>
                              </div>
                              <div style={{ width: '36px', textAlign: 'right', fontSize: '0.75rem', fontWeight: 700, color: '#94A3B8' }}>{pct}%</div>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Evidence Spans */}
                      <div>
                        <div style={{ fontSize: '0.78rem', fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', marginBottom: '0.5rem' }}>Evidence-Grounded Transcript</div>
                        <div className="evidence-card">
                          {/* Render student answer with evidence spans highlighted */}
                          {q.studentAnswer.split(' ').map((word, wi) => {
                            const span = q.evidenceSpans.find(es => es.text.includes(word));
                            return span
                              ? <span key={wi} className={`evidence-span ${span.type}`}>{word} </span>
                              : <span key={wi}>{word} </span>;
                          })}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};
