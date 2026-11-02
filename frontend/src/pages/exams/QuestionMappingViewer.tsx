/* eslint-disable react-hooks/exhaustive-deps, react-hooks/set-state-in-effect */
import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { client } from '../../api/client';
import { ArrowLeft, RefreshCw, AlertTriangle, CheckCircle, HelpCircle, FileText, LayoutGrid } from 'lucide-react';

interface Question {
  id: string;
  question_number: number;
  question_text: string;
  marks: number;
  question_type: string;
}

interface QuestionMapping {
  id: string;
  answer_sheet_id: string;
  question_id: string | null;
  detected_question_number: number | null;
  detected_question_label: string | null;
  extracted_answer_text: string;
  start_page: number | null;
  end_page: number | null;
  mapping_confidence: number;
  status: string; // MAPPED, UNMAPPED, DUPLICATE_DETECTED, NOT_ATTEMPTED
  duplicate_question_flag: boolean;
  duplicate_group_id: string | null;
  answer_word_count: number;
  answer_character_count: number;
  answer_page_count: number;
}

interface MappingSummary {
  total_questions: number;
  mapped_questions: number;
  unmapped_questions: number;
  duplicate_questions: number;
  not_attempted_questions: number;
}

export const QuestionMappingViewer: React.FC = () => {
  const { examId, id } = useParams<{ examId: string; id: string }>();

  const [mappings, setMappings] = useState<QuestionMapping[]>([]);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [summary, setSummary] = useState<MappingSummary | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [reprocessing, setReprocessing] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [filename, setFilename] = useState<string>('');

  const initData = async () => {
    setLoading(true);
    setError(null);
    try {
      // 1. Fetch original filename
      const sheetRes = await client.get(`/answer-sheets/${id}`);
      setFilename(sheetRes.data.original_filename);

      // 2. Fetch exam questions directory
      const qRes = await client.get('/questions', {
        params: { exam_id: examId, page: 1, page_size: 100 },
      });
      setQuestions(qRes.data.items || []);

      // 3. Fetch mapping data
      const mapRes = await client.get(`/ocr/${id}/mappings`);
      setMappings(mapRes.data || []);

      // 4. Fetch summary stats
      const sumRes = await client.get(`/ocr/${id}/mapping-summary`);
      setSummary(sumRes.data);

    } catch (err) {
      console.error('Failed to load mapping specifications:', err);
      setError('Failed to fetch question layouts and mapping summaries.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    initData();
  }, [id, examId]);

  const handleReprocessMappings = async () => {
    setReprocessing(true);
    setError(null);
    try {
      // Call synchronous reprocess question mapping endpoint
      const res = await client.post(`/ocr/${id}/mappings/reprocess`);
      setMappings(res.data || []);
      
      // Refresh summary
      const sumRes = await client.get(`/ocr/${id}/mapping-summary`);
      setSummary(sumRes.data);

      alert('Mappings successfully re-synchronized and recalculated.');
    } catch (err) {
      console.error('Reprocess question mappings failed:', err);
      setError('Failed to re-run layout segmentation and mapping algorithms.');
    } finally {
      setReprocessing(false);
    }
  };

  const getQuestionDetails = (qId: string | null) => {
    if (!qId) return null;
    return questions.find((q) => q.id === qId) || null;
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'MAPPED':
        return (
          <span className="profile-value badge badge-success" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}>
            <CheckCircle size={12} />
            <span>MAPPED</span>
          </span>
        );
      case 'UNMAPPED':
        return (
          <span className="profile-value badge" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem', background: 'rgba(245, 158, 11, 0.1)', color: 'rgba(245, 158, 11, 1)', border: '1px solid rgba(245, 158, 11, 0.2)' }}>
            <HelpCircle size={12} />
            <span>UNMAPPED</span>
          </span>
        );
      case 'DUPLICATE_DETECTED':
        return (
          <span className="profile-value badge" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem', background: 'rgba(239, 68, 68, 0.1)', color: 'var(--color-error)', border: '1px solid rgba(239, 68, 68, 0.2)' }}>
            <AlertTriangle size={12} />
            <span>DUPLICATE</span>
          </span>
        );
      case 'NOT_ATTEMPTED':
        return (
          <span className="profile-value badge" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem', background: 'rgba(255,255,255,0.05)', color: 'var(--text-secondary)', border: '1px solid var(--border-color)' }}>
            <FileText size={12} />
            <span>NOT ATTEMPTED</span>
          </span>
        );
      default:
        return (
          <span className="profile-value badge" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}>
            <span>{status}</span>
          </span>
        );
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
        Loading OCR layout coordinate mapping configurations...
      </div>
    );
  }

  return (
    <div className="mapping-viewer-container" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      
      {/* Header panel */}
      <div className="page-header" style={{ marginBottom: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <Link to={`/exams/${examId}`} className="btn btn-secondary btn-sm" title="Back to exam specs">
            <ArrowLeft size={16} />
          </Link>
          <div>
            <h1 style={{ fontSize: '1.25rem', fontWeight: 600 }}>Coordinate Layout Mapping details: {filename}</h1>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
              Evaluate auto-detected bounding boxes mapping to exam questions parameters
            </p>
          </div>
        </div>
        
        <button
          onClick={handleReprocessMappings}
          disabled={reprocessing}
          className="btn btn-primary"
          style={{ gap: '0.5rem' }}
          title="Re-run coordinate question alignment algorithms on extracted OCR blocks"
        >
          <RefreshCw size={16} className={reprocessing ? 'animate-spin' : ''} />
          <span>{reprocessing ? 'Reprocessing...' : 'Reprocess Mapping'}</span>
        </button>
      </div>

      {error && <div className="error-banner">{error}</div>}

      {/* Summary Cards */}
      {summary && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '1rem' }}>
          <div className="detail-card" style={{ display: 'flex', flexDirection: 'column', padding: '1rem 1.25rem', margin: 0, border: '1px solid var(--border-color)' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Exam Questions</span>
            <strong style={{ fontSize: '1.5rem', color: 'var(--text-primary)', marginTop: '0.2rem' }}>{summary.total_questions}</strong>
          </div>
          <div className="detail-card" style={{ display: 'flex', flexDirection: 'column', padding: '1rem 1.25rem', margin: 0, border: '1px solid var(--border-color)' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Mapped Segments</span>
            <strong style={{ fontSize: '1.5rem', color: 'var(--color-success)', marginTop: '0.2rem' }}>{summary.mapped_questions}</strong>
          </div>
          <div className="detail-card" style={{ display: 'flex', flexDirection: 'column', padding: '1rem 1.25rem', margin: 0, border: '1px solid var(--border-color)' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Unmapped Blocks</span>
            <strong style={{ fontSize: '1.5rem', color: 'rgba(245, 158, 11, 1)', marginTop: '0.2rem' }}>{summary.unmapped_questions}</strong>
          </div>
          <div className="detail-card" style={{ display: 'flex', flexDirection: 'column', padding: '1rem 1.25rem', margin: 0, border: '1px solid var(--border-color)' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Duplicates Flagged</span>
            <strong style={{ fontSize: '1.5rem', color: 'var(--color-error)', marginTop: '0.2rem' }}>{summary.duplicate_questions}</strong>
          </div>
          <div className="detail-card" style={{ display: 'flex', flexDirection: 'column', padding: '1rem 1.25rem', margin: 0, border: '1px solid var(--border-color)' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Not Attempted</span>
            <strong style={{ fontSize: '1.5rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>{summary.not_attempted_questions}</strong>
          </div>
        </div>
      )}

      {/* Mappings Detail List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.2rem' }}>
        {mappings.length === 0 ? (
          <div className="detail-card" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
            No question mapping alignments recorded for this answer sheet.
          </div>
        ) : (
          mappings.map((m) => {
            const matchedQuestion = getQuestionDetails(m.question_id);
            return (
              <div
                key={m.id}
                className="detail-card"
                style={{
                  margin: 0,
                  border: `1px solid ${m.duplicate_question_flag ? 'var(--color-error)' : 'var(--border-color)'}`,
                  background: m.duplicate_question_flag ? 'rgba(239, 68, 68, 0.02)' : 'rgba(27, 28, 36, 0.4)',
                  padding: '1.5rem',
                }}
              >
                {/* Header Row */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.75rem', marginBottom: '1rem' }}>
                  <div>
                    <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-accent)', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                      <LayoutGrid size={16} />
                      <span>
                        {matchedQuestion ? `Question ${matchedQuestion.question_number}` : `Detected: "${m.detected_question_label || 'Unknown label'}"`}
                      </span>
                    </h3>
                    <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
                      Segment boundaries: Page {m.start_page ?? 'N/A'} {m.end_page && m.end_page !== m.start_page ? `to Page ${m.end_page}` : ''} | Word Count: {m.answer_word_count}
                    </p>
                  </div>

                  <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                      Confidence: <strong>{(m.mapping_confidence * 100).toFixed(1)}%</strong>
                    </span>
                    {getStatusBadge(m.status)}
                  </div>
                </div>

                {/* Duplicate Warning */}
                {m.duplicate_question_flag && (
                  <div className="error-banner" style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'rgba(239, 68, 68, 0.1)', color: 'var(--color-error)', border: '1px solid rgba(239, 68, 68, 0.2)', padding: '0.5rem 1rem', borderRadius: '6px', fontSize: '0.8rem' }}>
                    <AlertTriangle size={16} />
                    <span>Warning: Duplicate answer segment mapping detected. This question number may have multiple responses mapped.</span>
                  </div>
                )}

                {/* Content details */}
                <div style={{ display: 'grid', gridTemplateColumns: '3fr 2fr', gap: '1.5rem' }}>
                  
                  {/* Segmented text */}
                  <div>
                    <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: '0.4rem' }}>Extracted Segment Text:</span>
                    <div style={{ background: 'rgba(0,0,0,0.15)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '1rem', fontSize: '0.85rem', lineHeight: '150%', whiteSpace: 'pre-wrap', fontFamily: 'monospace', maxHeight: '180px', overflowY: 'auto' }}>
                      {m.extracted_answer_text || <span style={{ color: 'var(--text-secondary)', fontStyle: 'italic' }}>(No text extracted for this segment)</span>}
                    </div>
                  </div>

                  {/* Question context specs */}
                  <div style={{ borderLeft: '1px solid var(--border-color)', paddingLeft: '1.5rem', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                    {matchedQuestion ? (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.8rem' }}>
                        <div>
                          <span style={{ color: 'var(--text-secondary)' }}>Target Spec text:</span>
                          <p style={{ color: 'var(--text-primary)', fontStyle: 'italic', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden', marginTop: '0.2rem' }}>
                            "{matchedQuestion.question_text}"
                          </p>
                        </div>
                        <div style={{ display: 'flex', gap: '1rem', borderTop: '1px solid var(--border-color)', paddingTop: '0.5rem', marginTop: '0.3rem' }}>
                          <div>
                            <span style={{ color: 'var(--text-secondary)' }}>Max Marks:</span>
                            <span style={{ display: 'block', fontWeight: 600, color: 'var(--text-accent)' }}>{matchedQuestion.marks} Marks</span>
                          </div>
                          <div>
                            <span style={{ color: 'var(--text-secondary)' }}>Type:</span>
                            <span style={{ display: 'block', textTransform: 'capitalize', fontWeight: 500 }}>{matchedQuestion.question_type}</span>
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                          <AlertTriangle size={14} style={{ color: 'rgba(245, 158, 11, 1)' }} />
                          <span>No mapping link established to Exam questions parameters.</span>
                        </div>
                        <p style={{ fontSize: '0.75rem' }}>
                          Reprocessing layout mappings may realign coordinate blocks with exam specs.
                        </p>
                      </div>
                    )}
                  </div>

                </div>

              </div>
            );
          })
        )}
      </div>

    </div>
  );
};
