import React, { useState } from 'react';
import { Shield, AlertTriangle, CheckCircle, Search, Download, Eye, XCircle, Users } from 'lucide-react';
import './PortalStyles.css';

/* ── Mock Pairwise Collusion Matrix ── */
const STUDENTS = ['24MCA01', '24MCA02', '24MCA03', '24MCA04', '24MCA05', '24MCA06', '24MCA07', '24MCA08'];

// Similarity matrix (0–1 cosine similarity)
const MATRIX: number[][] = [
  [1.00, 0.21, 0.18, 0.34, 0.25, 0.19, 0.16, 0.22],
  [0.21, 1.00, 0.17, 0.22, 0.19, 0.15, 0.18, 0.89],
  [0.18, 0.17, 1.00, 0.20, 0.16, 0.71, 0.18, 0.16],
  [0.34, 0.22, 0.20, 1.00, 0.26, 0.21, 0.17, 0.24],
  [0.25, 0.19, 0.16, 0.26, 1.00, 0.18, 0.15, 0.20],
  [0.19, 0.15, 0.71, 0.21, 0.18, 1.00, 0.16, 0.17],
  [0.16, 0.18, 0.18, 0.17, 0.15, 0.16, 1.00, 0.19],
  [0.22, 0.89, 0.16, 0.24, 0.20, 0.17, 0.19, 1.00],
];

const FLAGS = [
  { pair: '24MCA02 ↔ 24MCA08', similarity: 0.89, questions: [1, 2, 3], severity: 'high',   action: 'Investigation Opened', evidence: 'Identical phrase structures in Q1 & Q3. Verbatim sentences detected in 6 paragraphs. Submitted within 4 minutes of each other.' },
  { pair: '24MCA03 ↔ 24MCA06', similarity: 0.71, questions: [2, 3],    severity: 'medium', action: 'Under Review',          evidence: 'High semantic overlap in Q2 model answer content. Similar argument progression detected. Different handwriting confirmed by OCR.' },
];

const getColor = (val: number, i: number, j: number) => {
  if (i === j) return 'collusion-cell-self';
  if (val > 0.80) return 'collusion-cell-high';
  if (val > 0.60) return 'collusion-cell-mid';
  return 'collusion-cell-low';
};

export const IntegrityPortal: React.FC = () => {
  const [selectedFlag, setSelectedFlag] = useState<typeof FLAGS[0] | null>(null);
  const [activeTab, setActiveTab] = useState<'matrix' | 'flags' | 'report'>('matrix');
  const [hoveredCell, setHoveredCell] = useState<{i: number; j: number} | null>(null);

  return (
    <div className="portal-page">
      <div className="portal-header">
        <div className="portal-header-left">
          <div className="portal-badge-row">
            <span className="portal-badge integrity">Portal 7: Academic Integrity</span>
            <span className="status-chip red"><span className="status-dot" /> 2 Active Flags</span>
          </div>
          <h1>Academic Integrity & Collusion Detection</h1>
          <p>Pairwise cosine similarity heatmap, suspicious cluster identification, document-level evidence extraction, and investigation case management.</p>
        </div>
        <div className="portal-header-actions">
          <button className="btn btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Download size={15} /> Export Integrity Report
          </button>
        </div>
      </div>

      {/* KPI Strip */}
      <div className="kpi-strip">
        {[
          { icon: '🔍', label: 'Scripts Analysed', value: '42',   delta: 'MCA301 Exam Batch', color: '#818CF8' },
          { icon: '🚨', label: 'High Severity',    value: '1',    delta: '>80% cosine similarity', color: '#EF4444' },
          { icon: '⚠️', label: 'Medium Severity',  value: '1',    delta: '60–80% similarity', color: '#F59E0B' },
          { icon: '🛡️', label: 'Clean Scripts',    value: '40',   delta: 'Below 60% threshold', color: '#22C55E' },
        ].map((k, i) => (
          <div key={i} className="kpi-card">
            <div className="kpi-icon" style={{ background: `${k.color}20`, fontSize: '1.2rem' }}>{k.icon}</div>
            <div className="kpi-value" style={{ color: k.color }}>{k.value}</div>
            <div className="kpi-label">{k.label}</div>
            <div className="kpi-delta flat">{k.delta}</div>
          </div>
        ))}
      </div>

      <div className="portal-tabs">
        {(['matrix', 'flags', 'report'] as const).map(t => (
          <button key={t} className={`portal-tab ${activeTab === t ? 'active' : ''}`} onClick={() => setActiveTab(t)}>
            {t === 'matrix' ? '🗺️ Collusion Heatmap' : t === 'flags' ? '🚨 Flagged Pairs' : '📋 Investigation Reports'}
          </button>
        ))}
      </div>

      {/* ── MATRIX ── */}
      {activeTab === 'matrix' && (
        <div className="portal-section-card">
          <div className="section-card-header">
            <div className="section-card-title"><Shield size={16} color="#FCD34D" /> Pairwise Cosine Similarity Matrix — MCA301</div>
            <div style={{ display: 'flex', gap: '1rem', fontSize: '0.78rem', color: '#94A3B8' }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}><span style={{ width: 10, height: 10, background: 'rgba(185,28,28,0.4)', borderRadius: 2, display: 'inline-block' }} />High &gt;0.80</span>
              <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}><span style={{ width: 10, height: 10, background: 'rgba(245,158,11,0.4)', borderRadius: 2, display: 'inline-block' }} />Medium &gt;0.60</span>
              <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}><span style={{ width: 10, height: 10, background: 'rgba(21,128,61,0.2)', borderRadius: 2, display: 'inline-block' }} />Normal &lt;0.60</span>
            </div>
          </div>

          {hoveredCell && (
            <div style={{ marginBottom: '0.75rem', padding: '0.5rem 0.85rem', background: 'rgba(11,20,36,0.8)', borderRadius: 8, fontSize: '0.85rem', color: '#CBD5E1', border: '1px solid rgba(226,232,240,0.1)' }}>
              {STUDENTS[hoveredCell.i]} ↔ {STUDENTS[hoveredCell.j]} · Similarity: <strong style={{ color: MATRIX[hoveredCell.i][hoveredCell.j] > 0.80 ? '#FCA5A5' : MATRIX[hoveredCell.i][hoveredCell.j] > 0.60 ? '#FCD34D' : '#86EFAC' }}>{MATRIX[hoveredCell.i][hoveredCell.j].toFixed(2)}</strong>
            </div>
          )}

          <div className="heatmap-wrap">
            <table className="heatmap-table">
              <thead>
                <tr>
                  <th style={{ fontSize: '0.7rem', color: '#64748B', padding: '4px' }} />
                  {STUDENTS.map(s => (
                    <th key={s} style={{ fontSize: '0.68rem', color: '#94A3B8', fontWeight: 700, padding: '4px', textAlign: 'center' }}>{s.slice(-3)}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {MATRIX.map((row, i) => (
                  <tr key={i}>
                    <td style={{ fontSize: '0.68rem', color: '#94A3B8', fontWeight: 700, padding: '4px', whiteSpace: 'nowrap' }}>{STUDENTS[i].slice(-3)}</td>
                    {row.map((val, j) => (
                      <td
                        key={j}
                        className={`heatmap-cell ${getColor(val, i, j)}`}
                        onMouseEnter={() => i !== j && setHoveredCell({ i, j })}
                        onMouseLeave={() => setHoveredCell(null)}
                        title={`${STUDENTS[i]} ↔ ${STUDENTS[j]}: ${val.toFixed(2)}`}
                      >
                        {i === j ? '—' : val.toFixed(2)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ── FLAGS ── */}
      {activeTab === 'flags' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {FLAGS.map((flag, i) => (
            <div key={i} className="portal-section-card" style={{ cursor: 'pointer', borderColor: flag.severity === 'high' ? 'rgba(239,68,68,0.35)' : 'rgba(245,158,11,0.35)' }} onClick={() => setSelectedFlag(selectedFlag?.pair === flag.pair ? null : flag)}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '1rem' }}>
                <div style={{ display: 'flex', gap: '0.85rem', alignItems: 'flex-start' }}>
                  <div style={{ width: 44, height: 44, borderRadius: 10, background: flag.severity === 'high' ? 'rgba(239,68,68,0.15)' : 'rgba(245,158,11,0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.2rem', flexShrink: 0 }}>
                    {flag.severity === 'high' ? '🚨' : '⚠️'}
                  </div>
                  <div>
                    <div style={{ fontWeight: 700, color: '#F8FAFC', fontSize: '0.95rem' }}>{flag.pair}</div>
                    <div style={{ fontSize: '0.8rem', color: '#94A3B8', marginTop: 2 }}>Questions: Q{flag.questions.join(', Q')} · Similarity: <strong style={{ color: flag.severity === 'high' ? '#FCA5A5' : '#FCD34D' }}>{flag.similarity.toFixed(2)}</strong></div>
                  </div>
                </div>
                <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                  <span className={`status-chip ${flag.severity === 'high' ? 'red' : 'amber'}`}><span className="status-dot" />{flag.severity}</span>
                  <span style={{ fontSize: '0.78rem', color: '#64748B' }}>{flag.action}</span>
                </div>
              </div>

              {selectedFlag?.pair === flag.pair && (
                <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid rgba(226,232,240,0.08)' }}>
                  <div style={{ fontSize: '0.78rem', fontWeight: 700, color: '#94A3B8', marginBottom: '0.5rem', textTransform: 'uppercase' }}>Evidence Summary</div>
                  <div className="evidence-card">{flag.evidence}</div>
                  <div style={{ display: 'flex', gap: '0.75rem', marginTop: '1rem' }}>
                    <button className="btn btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.82rem' }}><Eye size={13} /> View Scripts</button>
                    <button className="btn btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.82rem', color: '#FCA5A5' }}><XCircle size={13} /> Escalate to Dean</button>
                    <button className="btn btn-primary" style={{ fontSize: '0.82rem' }}>Close Case — No Violation</button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* ── REPORT ── */}
      {activeTab === 'report' && (
        <div className="portal-section-card">
          <div className="section-card-header">
            <div className="section-card-title">📋 Integrity Audit Report — MCA301 Mid-Term 2026</div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', fontSize: '0.88rem', color: '#CBD5E1' }}>
            <div style={{ padding: '1rem', background: 'rgba(11,20,36,0.6)', borderRadius: 8, lineHeight: 1.7 }}>
              <strong style={{ color: '#F8FAFC', display: 'block', marginBottom: '0.5rem' }}>Executive Summary</strong>
              42 answer scripts from MCA301 Advanced Database Management Systems (Mid-Term 2026) were processed through the IntelliGrade Collusion Detection Engine. The system employed pairwise cosine similarity scoring on SentenceBERT embeddings (768-dimensional) at question-level granularity.
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              {[
                { label: 'Exam', value: 'MCA301 — Mid-Term 2026' },
                { label: 'Total Scripts', value: '42' },
                { label: 'Analysis Method', value: 'Cosine Similarity (SentenceBERT)' },
                { label: 'High Severity Flags', value: '1 pair (>0.80)' },
                { label: 'Medium Severity Flags', value: '1 pair (0.60–0.80)' },
                { label: 'Clean Scripts', value: '40 (95.2%)' },
                { label: 'Report Generated', value: '2026-10-26 14:35' },
                { label: 'Investigating Officer', value: 'Sneha Pillai (integrity_off)' },
              ].map(({ label, value }, i) => (
                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem 0.75rem', background: 'rgba(11,20,36,0.4)', borderRadius: 6 }}>
                  <span style={{ color: '#64748B' }}>{label}</span>
                  <span style={{ color: '#F8FAFC', fontWeight: 600 }}>{value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
