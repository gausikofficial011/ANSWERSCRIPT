/* eslint-disable react-hooks/exhaustive-deps, react-hooks/set-state-in-effect */
import React, { useEffect, useState } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { client } from '../../api/client';
import { ArrowLeft, RefreshCw, AlertTriangle, CheckCircle, Info } from 'lucide-react';

interface BoundingBox {
  text: string;
  confidence: number;
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  page_number: number;
  low_confidence_flag: boolean;
}

interface OCRResult {
  id: string;
  answer_sheet_id: string;
  page_number: number;
  extracted_text: string;
  bounding_boxes: BoundingBox[];
  low_confidence_flag: boolean;
  confidence_score: number;
  average_confidence: number;
  words_detected: number;
  processing_time: number;
  ocr_engine_version: string;
  preprocessing_version: string;
  original_image_path: string;
  processed_image_path: string;
  status: string;
  language_detected: string | null;
  created_at: string;
}

export const OCRResultsViewer: React.FC = () => {
  const { examId, id } = useParams<{ examId: string; id: string }>();
  const navigate = useNavigate();

  const [ocrResults, setOcrResults] = useState<OCRResult[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [activePageIndex, setActivePageIndex] = useState<number>(0);
  const [reprocessing, setReprocessing] = useState<boolean>(false);
  const [filename, setFilename] = useState<string>('');

  const fetchOcrResults = async () => {
    setLoading(true);
    setError(null);
    try {
      // 1. Fetch metadata to get original filename
      const sheetRes = await client.get(`/answer-sheets/${id}`);
      setFilename(sheetRes.data.original_filename);

      // 2. Fetch OCR results
      const ocrRes = await client.get(`/ocr/${id}/results`);
      const data: OCRResult[] = ocrRes.data || [];
      // Sort by page number ascending
      data.sort((a, b) => a.page_number - b.page_number);
      setOcrResults(data);
    } catch (err) {
      console.error('Failed to load OCR results:', err);
      setError('Failed to load OCR processing results for this answer sheet.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOcrResults();
  }, [id]);

  const handleReprocessOCR = async () => {
    if (!window.confirm('Are you sure you want to trigger a complete OCR reprocessing? This will clear all existing text segments and mappings, and re-enqueue the OCR background pipeline.')) {
      return;
    }

    setReprocessing(true);
    setError(null);
    try {
      await client.post(`/ocr/${id}/reprocess`);
      // Reprocess OCR queues it asynchronously and returns 202. Redirect user back to exam specs.
      alert('OCR reprocessing task successfully queued in the background. Returning to Answer Sheets directory.');
      navigate(`/exams/${examId}`);
    } catch (err) {
      console.error('Reprocess OCR failed:', err);
      setError('Failed to trigger OCR reprocessing pipeline.');
      setReprocessing(false);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
        Loading OCR output specifications...
      </div>
    );
  }

  if (error || ocrResults.length === 0) {
    return (
      <div style={{ padding: '2rem' }}>
        <div className="error-banner" style={{ marginBottom: '1rem' }}>
          {error || 'No OCR result records found. The document may still be in the preprocessing queue.'}
        </div>
        <Link to={`/exams/${examId}`} className="btn btn-secondary">
          <ArrowLeft size={16} />
          <span>Back to Exam</span>
        </Link>
      </div>
    );
  }

  const activeResult = ocrResults[activePageIndex];

  return (
    <div className="ocr-viewer-container" style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 120px)', gap: '1rem' }}>
      
      {/* Header Panel */}
      <div className="page-header" style={{ marginBottom: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <Link to={`/exams/${examId}`} className="btn btn-secondary btn-sm" title="Back to exam">
            <ArrowLeft size={16} />
          </Link>
          <div>
            <h1 style={{ fontSize: '1.25rem', fontWeight: 600 }}>OCR Document Output: {filename}</h1>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
              Answer Sheet ID: {id} | Extracted via OCR Engine Version: {activeResult?.ocr_engine_version || 'N/A'}
            </p>
          </div>
        </div>
        
        <button
          onClick={handleReprocessOCR}
          disabled={reprocessing}
          className="btn btn-secondary"
          style={{ gap: '0.5rem' }}
          title="Reset and re-run OCR on the original uploaded document"
        >
          <RefreshCw size={16} className={reprocessing ? 'animate-spin' : ''} />
          <span>{reprocessing ? 'Reprocessing...' : 'Reprocess OCR'}</span>
        </button>
      </div>

      {/* Split Workspace */}
      <div style={{ display: 'flex', flexGrow: 1, gap: '1.5rem', minHeight: 0 }}>
        
        {/* Left Navigator Pane */}
        <div className="detail-card" style={{ width: '280px', display: 'flex', flexDirection: 'column', gap: '1.2rem', flexShrink: 0, overflowY: 'auto', margin: 0 }}>
          <h3 style={{ fontSize: '0.95rem', fontWeight: 600, borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>Page Index</h3>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
            {ocrResults.map((res, index) => (
              <button
                key={res.id}
                onClick={() => setActivePageIndex(index)}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '0.8rem 1rem',
                  borderRadius: '8px',
                  border: `1px solid ${index === activePageIndex ? 'var(--text-accent)' : 'var(--border-color)'}`,
                  background: index === activePageIndex ? 'rgba(170, 59, 255, 0.08)' : 'rgba(0,0,0,0.1)',
                  color: 'var(--text-primary)',
                  textAlign: 'left',
                  cursor: 'pointer',
                  fontSize: '0.85rem',
                  transition: 'all 0.2s',
                }}
              >
                <span style={{ fontWeight: 600 }}>Page {res.page_number}</span>
                {res.low_confidence_flag ? (
                  <span style={{ color: 'var(--color-error)', display: 'inline-flex', alignItems: 'center' }} title="Low confidence words mapped on page">
                    <AlertTriangle size={14} />
                  </span>
                ) : (
                  <span style={{ color: 'var(--color-success)', display: 'inline-flex', alignItems: 'center' }}>
                    <CheckCircle size={14} />
                  </span>
                )}
              </button>
            ))}
          </div>

          <div style={{ marginTop: 'auto', background: 'rgba(255,255,255,0.01)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '0.8rem', fontSize: '0.75rem' }}>
            <h4 style={{ fontWeight: 600, color: 'var(--text-accent)', marginBottom: '0.4rem' }}>Metadata (Selected Page):</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.3rem', color: 'var(--text-secondary)' }}>
              <div>Confidence: <strong>{(activeResult.average_confidence * 100).toFixed(1)}%</strong></div>
              <div>Words Detected: <strong>{activeResult.words_detected}</strong></div>
              <div>Processing Time: <strong>{activeResult.processing_time.toFixed(2)}s</strong></div>
              <div style={{ wordBreak: 'break-all', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }} title={activeResult.original_image_path}>
                Source Image: <strong style={{ fontSize: '0.7rem' }}>{activeResult.original_image_path || 'N/A'}</strong>
              </div>
            </div>
          </div>
        </div>

        {/* Right Output Text Pane */}
        <div className="detail-card" style={{ flexGrow: 1, display: 'flex', flexDirection: 'column', minWidth: 0, margin: 0, padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.75rem', marginBottom: '1rem' }}>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span>Extracted Page {activeResult.page_number} Text Output</span>
              {activeResult.low_confidence_flag && (
                <span className="profile-value badge" style={{ background: 'rgba(239, 68, 68, 0.1)', color: 'var(--color-error)', border: '1px solid rgba(239, 68, 68, 0.2)', fontSize: '0.7rem' }}>
                  LOW CONFIDENCE WARNING
                </span>
              )}
            </h3>
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
              <Info size={14} />
              <span>Low confidence blocks are highlighted below</span>
            </div>
          </div>

          <div style={{ flexGrow: 1, display: 'flex', gap: '1.5rem', minHeight: 0 }}>
            {/* Plain Extracted Text */}
            <div style={{ flex: 1, background: 'rgba(0,0,0,0.15)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '1.25rem', overflowY: 'auto', fontSize: '0.9rem', lineHeight: '160%', whiteSpace: 'pre-wrap', color: 'var(--text-primary)', fontFamily: 'monospace' }}>
              {activeResult.extracted_text || '(No text extracted from this page)'}
            </div>

            {/* Bounding box list view with confidence highlights */}
            <div style={{ width: '350px', border: '1px solid var(--border-color)', borderRadius: '8px', display: 'flex', flexDirection: 'column', minHeight: 0 }}>
              <div style={{ background: 'rgba(255,255,255,0.02)', padding: '0.75rem 1rem', borderBottom: '1px solid var(--border-color)', fontSize: '0.8rem', fontWeight: 600 }}>
                Structured Words Bounding Blocks ({activeResult.bounding_boxes.length})
              </div>
              
              <div style={{ flexGrow: 1, overflowY: 'auto', padding: '0.6rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {activeResult.bounding_boxes.map((box, idx) => (
                  <div
                    key={idx}
                    style={{
                      background: box.low_confidence_flag ? 'rgba(239, 68, 68, 0.05)' : 'rgba(255,255,255,0.01)',
                      border: `1px solid ${box.low_confidence_flag ? 'rgba(239, 68, 68, 0.2)' : 'var(--border-color)'}`,
                      borderRadius: '6px',
                      padding: '0.6rem 0.8rem',
                      fontSize: '0.8rem',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '0.3rem',
                    }}
                  >
                    <div style={{ fontWeight: 500, color: box.low_confidence_flag ? 'var(--color-error)' : 'var(--text-primary)', wordBreak: 'break-all' }}>
                      "{box.text}"
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)', fontSize: '0.7rem' }}>
                      <span>Confidence: <strong>{(box.confidence * 100).toFixed(1)}%</strong></span>
                      <span>Coords: ({box.x1}, {box.y1}) to ({box.x2}, {box.y2})</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

      </div>

    </div>
  );
};
