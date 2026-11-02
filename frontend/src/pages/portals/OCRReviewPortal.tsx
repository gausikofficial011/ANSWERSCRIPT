import React, { useState } from 'react';
import { Eye, Crop, CheckCircle, AlertTriangle, Edit, RefreshCw, Download, ChevronLeft, ChevronRight, ZoomIn, ZoomOut, RotateCw } from 'lucide-react';
import './PortalStyles.css';

const SCRIPT_QUEUE = [
  { id: 'SS-2025-001', student: 'Arjun Reddy',   roll: '24MCA01', exam: 'MCA301', pages: 8,  ocrConf: 97.2, status: 'verified',   flagged: false },
  { id: 'SS-2025-002', student: 'Priya Singh',   roll: '24MCA02', exam: 'MCA301', pages: 6,  ocrConf: 91.4, status: 'needs_review', flagged: true  },
  { id: 'SS-2025-003', student: 'Rohan Mehta',   roll: '24MCA03', exam: 'MCA301', pages: 9,  ocrConf: 88.9, status: 'needs_review', flagged: true  },
  { id: 'SS-2025-004', student: 'Kavitha Rao',   roll: '24MCA04', exam: 'MCA301', pages: 7,  ocrConf: 95.7, status: 'verified',   flagged: false },
  { id: 'SS-2025-005', student: 'Deepak Varma',  roll: '24MCA05', exam: 'MCA301', pages: 10, ocrConf: 84.1, status: 'flagged',    flagged: true  },
  { id: 'SS-2025-006', student: 'Sneha Pillai',  roll: '24MCA06', exam: 'MCA301', pages: 5,  ocrConf: 99.1, status: 'verified',   flagged: false },
];

const MOCK_BBOXES = [
  { id: 1, x: 8,  y: 10, w: 84, h: 8,  text: 'Student Name: Arjun Reddy', conf: 99.1, type: 'header' },
  { id: 2, x: 8,  y: 22, w: 60, h: 6,  text: 'Roll No: 24MCA01 | Exam: MCA301', conf: 98.4, type: 'header' },
  { id: 3, x: 8,  y: 33, w: 90, h: 7,  text: 'Q1. Explain ACID properties in DBMS with examples.', conf: 97.2, type: 'question' },
  { id: 4, x: 8,  y: 43, w: 88, h: 18, text: 'Answer: ACID stands for Atomicity, Consistency, Isolation, and Durability. These are four key properties that guarantee database transactions are processed reliably...', conf: 96.8, type: 'answer' },
  { id: 5, x: 8,  y: 65, w: 90, h: 7,  text: 'Q2. Define normalization and explain 2NF vs 3NF.', conf: 95.1, type: 'question' },
  { id: 6, x: 8,  y: 74, w: 88, h: 15, text: 'Answer: Normalization is the process of organizing data to reduce redundancy and improve integrity. 2NF requires full dependency on primary key while 3NF eliminates transitive dependencies...', conf: 94.5, type: 'answer' },
];

export const OCRReviewPortal: React.FC = () => {
  const [selectedScript, setSelectedScript] = useState(SCRIPT_QUEUE[0]);
  const [selectedBBox, setSelectedBBox] = useState<number | null>(null);
  const [editingText, setEditingText] = useState('');
  const [editMode, setEditMode] = useState(false);
  const [zoom, setZoom] = useState(100);
  const [currentPage, setCurrentPage] = useState(1);
  const [verifiedToast, setVerifiedToast] = useState(false);
  const [bboxes, setBboxes] = useState(MOCK_BBOXES);

  const handleVerify = () => {
    setVerifiedToast(true);
    setTimeout(() => setVerifiedToast(false), 3000);
  };

  const handleBBoxEdit = (bbox: typeof MOCK_BBOXES[0]) => {
    setSelectedBBox(bbox.id);
    setEditingText(bbox.text);
    setEditMode(true);
  };

  const handleSaveEdit = () => {
    setBboxes(prev => prev.map(b => b.id === selectedBBox ? { ...b, text: editingText } : b));
    setEditMode(false);
  };

  return (
    <div className="portal-page">
      {/* Header */}
      <div className="portal-header">
        <div className="portal-header-left">
          <div className="portal-badge-row">
            <span className="portal-badge ocr">Portal 4: OCR Studio</span>
            <span className="live-indicator"><span className="live-dot" />Tesseract 5.3.3 LSTM Active</span>
          </div>
          <h1>OCR & Document Review Studio</h1>
          <p>Inspect AI-extracted answer text, correct transcription errors, validate bounding-box mappings, and approve scripts for AI scoring.</p>
        </div>
        <div className="portal-header-actions">
          <button className="btn btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Download size={15} /> Export OCR Report
          </button>
          <button className="btn btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }} onClick={handleVerify}>
            <CheckCircle size={15} /> Approve & Forward to AI
          </button>
        </div>
      </div>

      {/* KPI Strip */}
      <div className="kpi-strip">
        {[
          { icon: '📄', label: 'Scripts in Queue', value: SCRIPT_QUEUE.length.toString(), delta: '3 awaiting review', color: '#818CF8' },
          { icon: '✅', label: 'Verified', value: SCRIPT_QUEUE.filter(s => s.status === 'verified').length.toString(), delta: 'Ready for AI scoring', color: '#22C55E' },
          { icon: '⚠️', label: 'Flagged', value: SCRIPT_QUEUE.filter(s => s.flagged).length.toString(), delta: 'Requires manual correction', color: '#F59E0B' },
          { icon: '🎯', label: 'Avg OCR Confidence', value: `${(SCRIPT_QUEUE.reduce((s, x) => s + x.ocrConf, 0) / SCRIPT_QUEUE.length).toFixed(1)}%`, delta: 'Above 90% threshold', color: '#38BDF8' },
        ].map((k, i) => (
          <div key={i} className="kpi-card">
            <div className="kpi-icon" style={{ background: 'rgba(79,70,229,0.2)', fontSize: '1.2rem' }}>{k.icon}</div>
            <div className="kpi-value" style={{ color: k.color }}>{k.value}</div>
            <div className="kpi-label">{k.label}</div>
            <div className="kpi-delta flat">{k.delta}</div>
          </div>
        ))}
      </div>

      {verifiedToast && (
        <div className="portal-alert success">
          <CheckCircle size={16} />
          <div><strong>Script verified!</strong> SS-2025-001 approved and forwarded to AI Evaluation queue.</div>
        </div>
      )}

      {/* Main Split View */}
      <div className="split-panel left-heavy">
        {/* Left: Script Queue */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {/* Script Selection */}
          <div className="portal-section-card">
            <div className="section-card-header">
              <div className="section-card-title"><Eye size={16} color="#67E8F9" /> Script Review Queue</div>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {SCRIPT_QUEUE.map((s) => (
                <div
                  key={s.id}
                  className={`candidate-card ${selectedScript.id === s.id ? 'selected' : ''}`}
                  onClick={() => setSelectedScript(s)}
                >
                  <div className="candidate-avatar">{s.student.charAt(0)}</div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600, color: '#F8FAFC', fontSize: '0.9rem' }}>{s.student}</div>
                    <div style={{ fontSize: '0.75rem', color: '#94A3B8' }}>{s.id} · {s.roll} · {s.pages} pages</div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '0.8rem', fontWeight: 700, color: s.ocrConf > 95 ? '#22C55E' : s.ocrConf > 88 ? '#F59E0B' : '#EF4444' }}>
                      {s.ocrConf.toFixed(1)}%
                    </div>
                    <span className={`status-chip ${s.status === 'verified' ? 'green' : s.status === 'flagged' ? 'red' : 'amber'}`} style={{ fontSize: '0.65rem' }}>
                      <span className="status-dot" />{s.status.replace('_', ' ')}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Edit Panel */}
          {editMode && (
            <div className="portal-section-card">
              <div className="section-card-header">
                <div className="section-card-title"><Edit size={15} color="#F59E0B" /> Transcript Editor</div>
              </div>
              <div className="portal-form-group">
                <label className="portal-form-label">Correct OCR Transcript:</label>
                <textarea
                  className="portal-form-textarea"
                  value={editingText}
                  onChange={e => setEditingText(e.target.value)}
                  rows={5}
                />
              </div>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <button className="btn btn-secondary" onClick={() => setEditMode(false)}>Cancel</button>
                <button className="btn btn-primary" onClick={handleSaveEdit}>Save Correction</button>
              </div>
            </div>
          )}
        </div>

        {/* Right: Canvas & Bboxes */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {/* Canvas Controls */}
          <div className="portal-section-card">
            <div className="section-card-header">
              <div className="section-card-title">
                📜 {selectedScript.student} — {selectedScript.exam} (Page {currentPage}/{selectedScript.pages})
              </div>
              <div style={{ display: 'flex', gap: '0.35rem' }}>
                <button className="icon-btn" onClick={() => setZoom(z => Math.max(50, z - 10))}><ZoomOut size={13} /></button>
                <span style={{ fontSize: '0.78rem', color: '#94A3B8', padding: '0 0.3rem', alignSelf: 'center' }}>{zoom}%</span>
                <button className="icon-btn" onClick={() => setZoom(z => Math.min(200, z + 10))}><ZoomIn size={13} /></button>
                <button className="icon-btn"><RotateCw size={13} /></button>
                <button className="icon-btn" onClick={() => setCurrentPage(p => Math.max(1, p - 1))} disabled={currentPage === 1}><ChevronLeft size={13} /></button>
                <button className="icon-btn" onClick={() => setCurrentPage(p => Math.min(selectedScript.pages, p + 1))} disabled={currentPage === selectedScript.pages}><ChevronRight size={13} /></button>
              </div>
            </div>

            {/* Simulated OCR Canvas */}
            <div className="ocr-canvas-wrap" style={{ height: '460px', backgroundColor: '#F7F5F0', transform: `scale(${zoom / 100})`, transformOrigin: 'top center', transition: 'transform 0.2s' }}>
              {/* Simulated answer sheet paper */}
              <div style={{ width: '90%', height: '95%', position: 'relative', background: '#FEFCE8', borderRadius: '4px', boxShadow: '0 4px 15px rgba(0,0,0,0.15)', padding: '20px', fontFamily: 'serif', fontSize: '11px', color: '#1a1a1a', lineHeight: 1.8 }}>
                {/* Ruled lines */}
                {Array.from({ length: 20 }).map((_, i) => (
                  <div key={i} style={{ position: 'absolute', left: 0, right: 0, top: `${5 + i * 4.7}%`, height: '1px', background: 'rgba(0,0,150,0.1)' }} />
                ))}

                {/* Bounding Box overlays */}
                {bboxes.map(bb => (
                  <div
                    key={bb.id}
                    className={`ocr-bounding-box ${selectedBBox === bb.id ? 'selected' : ''}`}
                    style={{ left: `${bb.x}%`, top: `${bb.y}%`, width: `${bb.w}%`, height: `${bb.h}%` }}
                    onClick={() => setSelectedBBox(bb.id)}
                    title={`Confidence: ${bb.conf}% | Type: ${bb.type}`}
                  >
                    <div style={{ position: 'absolute', top: '-18px', left: 0, fontSize: '9px', background: selectedBBox === bb.id ? '#F59E0B' : '#4F46E5', color: '#FFF', padding: '1px 4px', borderRadius: '2px', whiteSpace: 'nowrap' }}>
                      {bb.type} · {bb.conf.toFixed(0)}%
                    </div>
                  </div>
                ))}

                {/* Actual text */}
                {bboxes.map(bb => (
                  <div key={`t-${bb.id}`} style={{ position: 'absolute', left: `${bb.x}%`, top: `${bb.y}%`, width: `${bb.w}%`, height: `${bb.h}%`, overflow: 'hidden', fontSize: bb.type === 'header' ? '10px' : '9px', fontWeight: bb.type === 'question' ? 700 : 400, padding: '1px 2px' }}>
                    {bb.text}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Extracted Segments Panel */}
          <div className="portal-section-card">
            <div className="section-card-header">
              <div className="section-card-title"><Crop size={15} color="#67E8F9" /> Extracted Segments ({bboxes.length})</div>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', maxHeight: '300px', overflowY: 'auto' }}>
              {bboxes.map(bb => (
                <div
                  key={bb.id}
                  style={{ padding: '0.75rem', background: selectedBBox === bb.id ? 'rgba(79,70,229,0.15)' : 'rgba(11,20,36,0.5)', borderRadius: '7px', border: `1px solid ${selectedBBox === bb.id ? 'rgba(79,70,229,0.4)' : 'rgba(226,232,240,0.07)'}`, cursor: 'pointer', transition: 'all 0.15s' }}
                  onClick={() => setSelectedBBox(bb.id)}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.3rem' }}>
                    <span className={`status-chip ${bb.type === 'answer' ? 'blue' : bb.type === 'question' ? 'purple' : 'gray'}`} style={{ fontSize: '0.65rem' }}>{bb.type}</span>
                    <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                      <span style={{ fontSize: '0.72rem', color: bb.conf > 95 ? '#22C55E' : bb.conf > 88 ? '#F59E0B' : '#EF4444', fontWeight: 700 }}>{bb.conf.toFixed(1)}%</span>
                      <button className="icon-btn" style={{ width: 26, height: 26 }} onClick={e => { e.stopPropagation(); handleBBoxEdit(bb); }}><Edit size={11} /></button>
                    </div>
                  </div>
                  <div style={{ fontSize: '0.8rem', color: '#CBD5E1', lineHeight: 1.4, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{bb.text}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
