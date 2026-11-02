import React, { useState } from 'react';
import { BarChart2, TrendingUp, TrendingDown, Download, Filter, PieChart, Activity } from 'lucide-react';
import './PortalStyles.css';

const SCORE_DIST = [
  { range: '0–30%',  count: 1, pct: 2.4,  color: '#EF4444' },
  { range: '31–50%', count: 3, pct: 7.1,  color: '#F97316' },
  { range: '51–60%', count: 5, pct: 11.9, color: '#F59E0B' },
  { range: '61–70%', count: 9, pct: 21.4, color: '#EAB308' },
  { range: '71–80%', count: 12, pct: 28.6, color: '#84CC16' },
  { range: '81–90%', count: 8, pct: 19.0, color: '#22C55E' },
  { range: '91–100%',count: 4, pct: 9.5,  color: '#10B981' },
];

const QUESTION_STATS = [
  { num: 1, topic: 'ACID Properties',         avgScore: 8.1, maxScore: 10, difficulty: 0.81, disc: 0.68, attempts: 42, conceptHit: 88 },
  { num: 2, topic: 'Normalization 2NF vs 3NF', avgScore: 3.7, maxScore: 5,  difficulty: 0.74, disc: 0.72, attempts: 42, conceptHit: 76 },
  { num: 3, topic: 'Clustered vs Non-clustered Indexing', avgScore: 4.2, maxScore: 5, difficulty: 0.84, disc: 0.61, attempts: 41, conceptHit: 82 },
];

const DEPT_STATS = [
  { dept: 'MCA 1st Year', students: 20, avg: 79.3, pass: 95, distinction: 25 },
  { dept: 'MCA 2nd Year', students: 18, avg: 74.1, pass: 89, distinction: 16 },
  { dept: 'MBA Section A', students: 25, avg: 71.8, pass: 84, distinction: 12 },
  { dept: 'BCA 3rd Year', students: 30, avg: 68.4, pass: 80, distinction: 10 },
];

export const AnalyticsPortal: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'distribution' | 'questions' | 'departments' | 'psychometrics'>('distribution');
  const [examFilter, setExamFilter] = useState('MCA301');

  const maxCount = Math.max(...SCORE_DIST.map(d => d.count));

  return (
    <div className="portal-page">
      <div className="portal-header">
        <div className="portal-header-left">
          <div className="portal-badge-row">
            <span className="portal-badge analytics">Portal 9: Analytics</span>
            <span className="status-chip green"><span className="status-dot" /> Live Cohort Data</span>
          </div>
          <h1>Academic Analytics & QA Dashboard</h1>
          <p>Score distributions, difficulty & discrimination indices, concept hit rates, department-level benchmarking, and psychometric test quality analysis.</p>
        </div>
        <div className="portal-header-actions">
          <select className="portal-form-select" style={{ width: 'auto' }} value={examFilter} onChange={e => setExamFilter(e.target.value)}>
            <option>MCA301</option><option>MBA Finance</option><option>BCA Database</option>
          </select>
          <button className="btn btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Download size={15} /> Export Analytics
          </button>
        </div>
      </div>

      {/* KPI Strip */}
      <div className="kpi-strip">
        {[
          { icon: '📊', label: 'Class Average',    value: '74.8%', delta: '+2.3% vs last batch',  color: '#818CF8' },
          { icon: '✅', label: 'Pass Rate',         value: '90.5%', delta: '38 of 42 students',    color: '#22C55E' },
          { icon: '🏆', label: 'Distinction Rate',  value: '14.3%', delta: '6 students ≥85%',      color: '#F59E0B' },
          { icon: '📉', label: 'Avg Difficulty',    value: '0.76',  delta: 'Moderate exam level',  color: '#38BDF8' },
          { icon: '🎯', label: 'Discrimination Idx',value: '0.67',  delta: 'Good differentiation', color: '#34D399' },
        ].map((k, i) => (
          <div key={i} className="kpi-card">
            <div className="kpi-icon" style={{ background: `${k.color}20`, fontSize: '1.1rem' }}>{k.icon}</div>
            <div className="kpi-value" style={{ color: k.color }}>{k.value}</div>
            <div className="kpi-label">{k.label}</div>
            <div className="kpi-delta flat">{k.delta}</div>
          </div>
        ))}
      </div>

      <div className="portal-tabs">
        {(['distribution', 'questions', 'departments', 'psychometrics'] as const).map(t => (
          <button key={t} className={`portal-tab ${activeTab === t ? 'active' : ''}`} onClick={() => setActiveTab(t)}>
            {t === 'distribution' ? '📊 Score Distribution' : t === 'questions' ? '❓ Question Analysis' : t === 'departments' ? '🏛️ Department Bench.' : '🔬 Psychometrics'}
          </button>
        ))}
      </div>

      {/* ── DISTRIBUTION ── */}
      {activeTab === 'distribution' && (
        <div className="split-panel">
          <div className="portal-section-card">
            <div className="section-card-header">
              <div className="section-card-title"><BarChart2 size={16} color="#5EEAD4" /> Score Distribution — {examFilter}</div>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
              {SCORE_DIST.map((d, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
                  <div style={{ width: '65px', fontSize: '0.78rem', color: '#94A3B8', flexShrink: 0 }}>{d.range}</div>
                  <div style={{ flex: 1, position: 'relative', height: '26px', background: 'rgba(255,255,255,0.04)', borderRadius: 5, overflow: 'hidden' }}>
                    <div style={{ position: 'absolute', left: 0, top: 0, bottom: 0, borderRadius: 5, background: d.color, width: `${(d.count / maxCount) * 100}%`, opacity: 0.7, transition: 'width 0.6s cubic-bezier(0.34,1.56,0.64,1)' }} />
                  </div>
                  <div style={{ width: '70px', textAlign: 'right', fontSize: '0.8rem', color: '#F8FAFC', fontWeight: 700 }}>{d.count} <span style={{ color: '#64748B', fontWeight: 400 }}>({d.pct}%)</span></div>
                </div>
              ))}
            </div>
          </div>

          <div className="portal-section-card">
            <div className="section-card-header">
              <div className="section-card-title">🎓 Grade Summary</div>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {[
                { grade: 'S (Outstanding)', range: '90–100%', count: 4,  color: '#22C55E' },
                { grade: 'A+ (Excellent)',  range: '80–89%',  count: 8,  color: '#84CC16' },
                { grade: 'A (Very Good)',   range: '70–79%',  count: 12, color: '#EAB308' },
                { grade: 'B+ (Good)',       range: '60–69%',  count: 9,  color: '#F97316' },
                { grade: 'B (Average)',     range: '50–59%',  count: 5,  color: '#FB923C' },
                { grade: 'F (Fail)',        range: '<50%',    count: 4,  color: '#EF4444' },
              ].map((g, i) => (
                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.6rem 0.85rem', background: 'rgba(11,20,36,0.5)', borderRadius: 7, borderLeft: `3px solid ${g.color}` }}>
                  <div>
                    <div style={{ fontWeight: 600, color: '#F8FAFC', fontSize: '0.88rem' }}>{g.grade}</div>
                    <div style={{ fontSize: '0.72rem', color: '#64748B' }}>{g.range}</div>
                  </div>
                  <div style={{ fontWeight: 800, fontSize: '1.15rem', color: g.color }}>{g.count}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ── QUESTIONS ── */}
      {activeTab === 'questions' && (
        <div className="portal-section-card">
          <div className="section-card-header">
            <div className="section-card-title">❓ Per-Question Item Analysis</div>
          </div>
          <div style={{ overflowX: 'auto' }}>
            <table className="portal-table">
              <thead>
                <tr>
                  <th>Q#</th><th>Topic</th><th>Avg Score</th><th>Difficulty Index (P)</th><th>Discrimination (D)</th><th>Concept Hit Rate</th><th>Attempts</th>
                </tr>
              </thead>
              <tbody>
                {QUESTION_STATS.map(q => (
                  <tr key={q.num}>
                    <td>Q{q.num}</td>
                    <td>{q.topic}</td>
                    <td style={{ fontWeight: 700 }}>{q.avgScore} / {q.maxScore}</td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <div style={{ width: '60px' }}>
                          <div className="progress-bar-wrap">
                            <div className="progress-bar-fill" style={{ width: `${q.difficulty * 100}%` }} />
                          </div>
                        </div>
                        <span style={{ color: q.difficulty > 0.7 ? '#22C55E' : q.difficulty > 0.4 ? '#F59E0B' : '#EF4444' }}>{q.difficulty.toFixed(2)}</span>
                      </div>
                    </td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <div style={{ width: '60px' }}>
                          <div className="progress-bar-wrap">
                            <div className="progress-bar-fill" style={{ width: `${q.disc * 100}%`, background: q.disc > 0.6 ? 'linear-gradient(90deg,#22C55E,#86EFAC)' : 'linear-gradient(90deg,#F59E0B,#FCD34D)' }} />
                          </div>
                        </div>
                        <span>{q.disc.toFixed(2)}</span>
                      </div>
                    </td>
                    <td>
                      <span style={{ color: q.conceptHit > 85 ? '#22C55E' : q.conceptHit > 70 ? '#F59E0B' : '#EF4444', fontWeight: 700 }}>{q.conceptHit}%</span>
                    </td>
                    <td style={{ color: '#94A3B8' }}>{q.attempts}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div style={{ marginTop: '1.25rem' }}>
            <div className="portal-alert info">
              <Activity size={14} />
              <div><strong>Psychometric Note:</strong> All questions show discrimination index D &gt; 0.60, indicating good differentiation between high and low performers. No items require revision.</div>
            </div>
          </div>
        </div>
      )}

      {/* ── DEPARTMENTS ── */}
      {activeTab === 'departments' && (
        <div className="portal-section-card">
          <div className="section-card-header">
            <div className="section-card-title">🏛️ Department-Level Benchmark Comparison</div>
          </div>
          <div style={{ overflowX: 'auto' }}>
            <table className="portal-table">
              <thead>
                <tr><th>Programme</th><th>Students</th><th>Class Average</th><th>Pass Rate</th><th>Distinction %</th><th>Performance</th></tr>
              </thead>
              <tbody>
                {DEPT_STATS.map((d, i) => (
                  <tr key={i}>
                    <td>{d.dept}</td>
                    <td style={{ color: '#94A3B8' }}>{d.students}</td>
                    <td style={{ fontWeight: 800, color: d.avg > 75 ? '#22C55E' : d.avg > 65 ? '#F59E0B' : '#EF4444' }}>{d.avg}%</td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <div style={{ width: '60px' }}>
                          <div className="progress-bar-wrap"><div className="progress-bar-fill" style={{ width: `${d.pass}%`, background: 'linear-gradient(90deg,#22C55E,#86EFAC)' }} /></div>
                        </div>
                        <span style={{ color: '#86EFAC', fontWeight: 700 }}>{d.pass}%</span>
                      </div>
                    </td>
                    <td style={{ color: '#FCD34D', fontWeight: 700 }}>{d.distinction}%</td>
                    <td>
                      <span className={`status-chip ${d.avg > 75 ? 'green' : d.avg > 65 ? 'amber' : 'red'}`}>
                        <span className="status-dot" />{d.avg > 75 ? 'Above Target' : d.avg > 65 ? 'On Track' : 'Below Target'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ── PSYCHOMETRICS ── */}
      {activeTab === 'psychometrics' && (
        <div className="split-panel">
          <div className="portal-section-card">
            <div className="section-card-header">
              <div className="section-card-title">🔬 Cronbach's Alpha Reliability</div>
            </div>
            <div style={{ textAlign: 'center', padding: '1.5rem' }}>
              <div style={{ fontSize: '4rem', fontWeight: 900, color: '#818CF8' }}>0.84</div>
              <div style={{ color: '#86EFAC', fontSize: '0.9rem', fontWeight: 700, marginTop: '0.25rem' }}>Good Reliability</div>
              <div style={{ color: '#94A3B8', fontSize: '0.82rem', marginTop: '0.5rem' }}>Cronbach's α &gt; 0.80 indicates good internal consistency of the examination instrument.</div>
            </div>
            <div style={{ fontSize: '0.8rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {[['KR-20 Index', '0.81'], ['Standard Error of Measurement', '2.14'], ['Variance (Score)', '41.3'], ['Inter-Rater Reliability (AI vs Human)', '0.91']].map(([k, v]) => (
                <div key={k} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.4rem 0.75rem', background: 'rgba(11,20,36,0.5)', borderRadius: 6 }}>
                  <span style={{ color: '#64748B' }}>{k}</span><span style={{ color: '#F8FAFC', fontWeight: 700 }}>{v}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="portal-section-card">
            <div className="section-card-header">
              <div className="section-card-title">📐 Item Response Theory (IRT)</div>
            </div>
            <div className="portal-alert info" style={{ marginBottom: '1rem' }}>
              <TrendingUp size={14} />
              All items fall within acceptable IRT parameter bounds. No items flagged for removal.
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
              {QUESTION_STATS.map(q => (
                <div key={q.num} style={{ padding: '0.75rem', background: 'rgba(11,20,36,0.5)', borderRadius: 8, border: '1px solid rgba(226,232,240,0.07)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                    <span style={{ fontWeight: 700, color: '#F8FAFC' }}>Q{q.num}: {q.topic}</span>
                    <span className="status-chip green" style={{ fontSize: '0.65rem' }}>✓ Acceptable</span>
                  </div>
                  <div style={{ display: 'flex', gap: '1.25rem', fontSize: '0.78rem', color: '#94A3B8' }}>
                    <span>a-param: <strong style={{ color: '#818CF8' }}>{(q.disc * 2.5).toFixed(2)}</strong></span>
                    <span>b-param: <strong style={{ color: '#818CF8' }}>{(1 - q.difficulty).toFixed(2)}</strong></span>
                    <span>c-param: <strong style={{ color: '#818CF8' }}>0.12</strong></span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
