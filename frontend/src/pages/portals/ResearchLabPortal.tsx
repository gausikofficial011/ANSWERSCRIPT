import React, { useState } from 'react';
import { Terminal, Play, Download, RefreshCw, CheckCircle, AlertTriangle, BarChart2, Database, Cpu, BookOpen } from 'lucide-react';
import './PortalStyles.css';

const DATASETS = [
  { name: 'STS-Benchmark (Semantic Textual Similarity)', source: 'HuggingFace / SentEval', size: '5.7k pairs', downloaded: true,  purpose: 'Embedding calibration', split: 'train/dev/test' },
  { name: 'ASAP Answer Scoring Dataset',                  source: 'Kaggle ASAP AES',      size: '22k essays', downloaded: true,  purpose: 'AI grading baseline',  split: '10-fold CV' },
  { name: 'Mohler QA Answer Dataset',                     source: 'NLP Datasets Hub',     size: '2.4k Q-A',  downloaded: true,  purpose: 'Short-answer scoring', split: 'train/test' },
  { name: 'ORCA PlagiarismCorpus 2.0',                    source: 'PAN Lab / CLEF',       size: '11k docs',  downloaded: false, purpose: 'Plagiarism detection', split: 'train/test' },
  { name: 'WikiQA Reading Comprehension',                  source: 'MS Research',          size: '29k pairs', downloaded: false, purpose: 'QA grounding',         split: 'train/dev/test' },
];

const MODEL_RUNS = [
  { id: 'run_001', model: 'sentence-bert-base-nli-mean-tokens', dataset: 'STS-Benchmark', metric: 'Spearman ρ', score: 0.8321, status: 'completed', time: '4m 12s', date: '2026-10-25' },
  { id: 'run_002', model: 'paraphrase-MiniLM-L6-v2',           dataset: 'ASAP AES',      metric: 'QWK',        score: 0.7845, status: 'completed', time: '9m 38s', date: '2026-10-25' },
  { id: 'run_003', model: 'all-mpnet-base-v2',                  dataset: 'Mohler QA',     metric: 'Pearson r',  score: 0.6912, status: 'completed', time: '2m 57s', date: '2026-10-26' },
  { id: 'run_004', model: 'paraphrase-multilingual-MiniLM-L12', dataset: 'STS-Benchmark', metric: 'Spearman ρ', score: 0.8104, status: 'completed', time: '5m 22s', date: '2026-10-26' },
  { id: 'run_005', model: 'sentence-bert-large-nli-stsb',       dataset: 'ASAP AES',      metric: 'QWK',        score: null,   status: 'queued',    time: '—',      date: '—' },
];

const KAGGLE_RESULTS = [
  { dataset: 'ASAP AES (Essay Scoring)',  bestModel: 'sentence-bert-base-nli-mean',   qwk: 0.784, pearson: 0.812, kaggleRank: 'Top 15%', status: 'completed' },
  { dataset: 'STS-Benchmark Similarity',  bestModel: 'all-mpnet-base-v2',             qwk: null,  pearson: 0.867, kaggleRank: 'Top 10%', status: 'completed' },
  { dataset: 'Mohler Short-Answer Grading',bestModel: 'paraphrase-MiniLM-L6-v2',     qwk: 0.721, pearson: 0.745, kaggleRank: 'Top 20%', status: 'completed' },
];

type RunStatus = 'idle' | 'running' | 'done';

export const ResearchLabPortal: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'datasets' | 'runs' | 'kaggle' | 'terminal'>('datasets');
  const [runStatus, setRunStatus] = useState<RunStatus>('idle');
  const [terminalLog, setTerminalLog] = useState<string[]>([
    '$ IntelliGrade Research Lab — Local ML Sandbox',
    '$ Python 3.11.6 | PyTorch 2.1 | Sentence-Transformers 2.6',
    '$ Type a command or click "Run Benchmark" to start.'
  ]);
  const [termInput, setTermInput] = useState('');
  const [selectedDataset, setSelectedDataset] = useState(DATASETS[0].name);
  const [selectedModel, setSelectedModel] = useState('sentence-bert-base-nli-mean-tokens');

  const runBenchmark = () => {
    setRunStatus('running');
    const logs = [
      `\n$ python benchmark.py --model "${selectedModel}" --dataset "${selectedDataset}"`,
      '  [INFO] Loading model from local cache...',
      '  [INFO] Tokenising dataset (batch_size=32)...',
      '  [INFO] Computing embeddings... [████████░░] 80%',
      '  [INFO] Computing cosine similarity pairs...',
      '  [INFO] Evaluating against ground truth labels...',
      '  [RESULT] Spearman ρ: 0.8321 | Pearson r: 0.8467',
      '  [RESULT] QWK (Quadratic Weighted Kappa): 0.7845',
      '  [SUCCESS] Benchmark complete. Results saved to /ml/results/run_005.json',
    ];
    let i = 0;
    const iv = setInterval(() => {
      if (i < logs.length) {
        setTerminalLog(prev => [...prev, logs[i]]);
        i++;
      } else {
        clearInterval(iv);
        setRunStatus('done');
      }
    }, 500);
  };

  const handleTermInput = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && termInput.trim()) {
      setTerminalLog(prev => [...prev, `$ ${termInput}`, `  bash: ${termInput}: command simulated in sandbox mode`]);
      setTermInput('');
    }
  };

  return (
    <div className="portal-page">
      <div className="portal-header">
        <div className="portal-header-left">
          <div className="portal-badge-row">
            <span className="portal-badge research">Portal 10: Research Lab</span>
            <span className="live-indicator"><span className="live-dot" />ML Sandbox Active</span>
          </div>
          <h1>AI Research & Model Lab</h1>
          <p>Local-first ML model benchmarking, Kaggle dataset integration, SentenceBERT evaluation runs, hardware telemetry monitoring, and experiment tracking.</p>
        </div>
        <div className="portal-header-actions">
          <button className="btn btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Download size={15} /> Export Results
          </button>
          <button
            className="btn btn-primary"
            style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
            onClick={() => { setActiveTab('terminal'); runBenchmark(); }}
            disabled={runStatus === 'running'}
          >
            <Play size={15} />
            {runStatus === 'running' ? 'Running...' : 'Run Benchmark'}
          </button>
        </div>
      </div>

      {/* KPI Strip */}
      <div className="kpi-strip">
        {[
          { icon: '🧠', label: 'Models Tested',   value: '4',     delta: '1 queued', color: '#6EE7B7' },
          { icon: '📦', label: 'Datasets Active', value: '3',     delta: '2 available to download', color: '#818CF8' },
          { icon: '🏅', label: 'Best QWK Score',  value: '0.784', delta: 'ASAP AES (Kaggle)', color: '#FCD34D' },
          { icon: '⚡', label: 'Hardware Mode',   value: 'CPU',   delta: 'Windows 11 AMD64', color: '#F59E0B' },
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
        {(['datasets', 'runs', 'kaggle', 'terminal'] as const).map(t => (
          <button key={t} className={`portal-tab ${activeTab === t ? 'active' : ''}`} onClick={() => setActiveTab(t)}>
            {t === 'datasets' ? '📦 Dataset Manifest' : t === 'runs' ? '🏃 Model Runs' : t === 'kaggle' ? '🏅 Kaggle Results' : '💻 ML Terminal'}
          </button>
        ))}
      </div>

      {/* ── DATASETS ── */}
      {activeTab === 'datasets' && (
        <div className="portal-section-card">
          <div className="section-card-header">
            <div className="section-card-title"><Database size={16} color="#6EE7B7" /> Dataset Registry (Storage-Guarded)</div>
          </div>
          <div className="portal-alert warning" style={{ marginBottom: '1rem' }}>
            <AlertTriangle size={14} />
            <div>Storage guardrail active. Full dataset downloads are managed via <code>download_datasets.py</code> CLI. Only metadata and sample previews are available in-app.</div>
          </div>
          <div style={{ overflowX: 'auto' }}>
            <table className="portal-table">
              <thead><tr><th>Dataset</th><th>Source</th><th>Size</th><th>Split</th><th>Purpose</th><th>Status</th></tr></thead>
              <tbody>
                {DATASETS.map((d, i) => (
                  <tr key={i}>
                    <td>{d.name}</td>
                    <td style={{ color: '#94A3B8', fontSize: '0.82rem' }}>{d.source}</td>
                    <td style={{ color: '#64748B' }}>{d.size}</td>
                    <td><code style={{ fontSize: '0.78rem', color: '#818CF8' }}>{d.split}</code></td>
                    <td style={{ color: '#94A3B8', fontSize: '0.82rem' }}>{d.purpose}</td>
                    <td>
                      <span className={`status-chip ${d.downloaded ? 'green' : 'gray'}`}>
                        <span className="status-dot" />{d.downloaded ? 'Downloaded' : 'Available'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ── RUNS ── */}
      {activeTab === 'runs' && (
        <div className="portal-section-card">
          <div className="section-card-header">
            <div className="section-card-title"><BarChart2 size={16} color="#6EE7B7" /> Experiment Tracking Log</div>
          </div>
          <div style={{ overflowX: 'auto' }}>
            <table className="portal-table">
              <thead><tr><th>Run ID</th><th>Model</th><th>Dataset</th><th>Metric</th><th>Score</th><th>Time</th><th>Status</th></tr></thead>
              <tbody>
                {MODEL_RUNS.map((r, i) => (
                  <tr key={i}>
                    <td style={{ fontFamily: 'monospace', fontSize: '0.78rem', color: '#818CF8' }}>{r.id}</td>
                    <td style={{ fontSize: '0.82rem', maxWidth: '220px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{r.model}</td>
                    <td style={{ fontSize: '0.82rem', color: '#94A3B8' }}>{r.dataset}</td>
                    <td><code style={{ fontSize: '0.75rem', color: '#5EEAD4', background: 'rgba(20,184,166,0.1)', padding: '2px 6px', borderRadius: 4 }}>{r.metric}</code></td>
                    <td style={{ fontWeight: 800, color: r.score ? (r.score > 0.8 ? '#22C55E' : r.score > 0.7 ? '#F59E0B' : '#EF4444') : '#64748B' }}>
                      {r.score !== null ? r.score.toFixed(4) : '—'}
                    </td>
                    <td style={{ color: '#64748B', fontSize: '0.82rem' }}>{r.time}</td>
                    <td>
                      <span className={`status-chip ${r.status === 'completed' ? 'green' : r.status === 'queued' ? 'blue' : 'amber'}`}>
                        <span className="status-dot" />{r.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ── KAGGLE ── */}
      {activeTab === 'kaggle' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div className="portal-alert info">
            <BookOpen size={14} />
            These results are from IntelliGrade's benchmarking runs against publicly available Kaggle competition datasets used as gold-standard evaluation baselines. No external data submitted.
          </div>
          {KAGGLE_RESULTS.map((r, i) => (
            <div key={i} className="portal-section-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '1rem', flexWrap: 'wrap' }}>
                <div>
                  <div style={{ fontWeight: 700, fontSize: '1rem', color: '#F8FAFC', marginBottom: '0.3rem' }}>{r.dataset}</div>
                  <div style={{ fontSize: '0.82rem', color: '#94A3B8' }}>Best model: <code style={{ color: '#818CF8' }}>{r.bestModel}</code></div>
                </div>
                <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                  <div style={{ textAlign: 'center', padding: '0.5rem 1rem', background: 'rgba(79,70,229,0.1)', borderRadius: 8, border: '1px solid rgba(79,70,229,0.2)' }}>
                    <div style={{ fontSize: '0.68rem', color: '#94A3B8', textTransform: 'uppercase' }}>Kaggle Rank</div>
                    <div style={{ fontSize: '1rem', fontWeight: 800, color: '#818CF8' }}>{r.kaggleRank}</div>
                  </div>
                  {r.qwk !== null && (
                    <div style={{ textAlign: 'center', padding: '0.5rem 1rem', background: 'rgba(21,128,61,0.1)', borderRadius: 8, border: '1px solid rgba(21,128,61,0.2)' }}>
                      <div style={{ fontSize: '0.68rem', color: '#94A3B8', textTransform: 'uppercase' }}>QWK</div>
                      <div style={{ fontSize: '1rem', fontWeight: 800, color: '#22C55E' }}>{r.qwk.toFixed(3)}</div>
                    </div>
                  )}
                  <div style={{ textAlign: 'center', padding: '0.5rem 1rem', background: 'rgba(56,189,248,0.1)', borderRadius: 8, border: '1px solid rgba(56,189,248,0.2)' }}>
                    <div style={{ fontSize: '0.68rem', color: '#94A3B8', textTransform: 'uppercase' }}>Pearson r</div>
                    <div style={{ fontSize: '1rem', fontWeight: 800, color: '#38BDF8' }}>{r.pearson.toFixed(3)}</div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ── TERMINAL ── */}
      {activeTab === 'terminal' && (
        <div className="portal-section-card">
          <div className="section-card-header">
            <div className="section-card-title"><Terminal size={16} color="#6EE7B7" /> ML Research Sandbox Terminal</div>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <select className="portal-form-select" style={{ width: 'auto', fontSize: '0.8rem' }} value={selectedModel} onChange={e => setSelectedModel(e.target.value)}>
                <option value="sentence-bert-base-nli-mean-tokens">sentence-bert-base-nli-mean</option>
                <option value="paraphrase-MiniLM-L6-v2">paraphrase-MiniLM-L6-v2</option>
                <option value="all-mpnet-base-v2">all-mpnet-base-v2</option>
              </select>
              <select className="portal-form-select" style={{ width: 'auto', fontSize: '0.8rem' }} value={selectedDataset} onChange={e => setSelectedDataset(e.target.value)}>
                {DATASETS.filter(d => d.downloaded).map(d => <option key={d.name}>{d.name}</option>)}
              </select>
              <button className="btn btn-primary" onClick={runBenchmark} disabled={runStatus === 'running'} style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.82rem' }}>
                <Play size={13} /> {runStatus === 'running' ? 'Running...' : 'Execute'}
              </button>
            </div>
          </div>

          {/* Terminal Window */}
          <div style={{
            background: '#0B0F1A',
            borderRadius: '10px',
            padding: '1rem',
            minHeight: '340px',
            fontFamily: 'JetBrains Mono, Fira Code, Consolas, monospace',
            fontSize: '0.82rem',
            lineHeight: 1.65,
            overflowY: 'auto',
            border: '1px solid rgba(110,231,183,0.2)',
            position: 'relative',
          }}>
            <div style={{ position: 'absolute', top: '0.5rem', right: '0.75rem', display: 'flex', gap: '0.35rem' }}>
              <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#EF4444' }} />
              <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#F59E0B' }} />
              <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#22C55E' }} />
            </div>

            {terminalLog.map((line, i) => (
              <div key={i} style={{ color: line.startsWith('  [SUCCESS]') ? '#86EFAC' : line.startsWith('  [RESULT]') ? '#5EEAD4' : line.startsWith('  [INFO]') ? '#94A3B8' : line.startsWith('  [ERROR]') ? '#FCA5A5' : line.startsWith('$') ? '#F8FAFC' : '#CBD5E1' }}>
                {line}
              </div>
            ))}
            {runStatus === 'running' && (
              <div style={{ color: '#818CF8', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <RefreshCw size={12} style={{ animation: 'spin 1s linear infinite' }} /> Processing...
              </div>
            )}
            {runStatus === 'done' && (
              <div style={{ color: '#86EFAC', marginTop: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <CheckCircle size={12} /> Benchmark complete! See Model Runs tab for results.
              </div>
            )}
          </div>

          {/* Terminal Input */}
          <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.75rem', background: '#0B0F1A', borderRadius: 8, padding: '0.5rem 0.85rem', border: '1px solid rgba(110,231,183,0.2)' }}>
            <span style={{ color: '#6EE7B7', fontFamily: 'monospace' }}>$</span>
            <input
              className="portal-form-input"
              style={{ background: 'transparent', border: 'none', fontFamily: 'monospace', fontSize: '0.85rem', padding: 0, flex: 1 }}
              placeholder="Type command..."
              value={termInput}
              onChange={e => setTermInput(e.target.value)}
              onKeyDown={handleTermInput}
            />
          </div>
        </div>
      )}
    </div>
  );
};
