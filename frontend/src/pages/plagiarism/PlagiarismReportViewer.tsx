/* eslint-disable react-hooks/exhaustive-deps, react-hooks/set-state-in-effect, @typescript-eslint/no-explicit-any */
import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { client } from '../../api/client';
import { useAuth } from '../../context/AuthContext';
import { 
  ArrowLeft, 
  Clock, 
  CheckCircle, 
  AlertOctagon, 
  User, 
  FileText, 
  ShieldAlert, 
  MessageSquare,
  Activity,
  RefreshCw
} from 'lucide-react';
import { downloadFile } from '../../utils/download';

interface Student {
  id: string;
  student_number: string;
  full_name: string;
}

interface AnswerSheet {
  id: string;
  student_id: string;
  original_filename: string;
  exam_id: string;
}

interface Exam {
  id: string;
  title: string;
}

interface PlagiarismReport {
  id: string;
  exam_id: string;
  source_answer_sheet_id: string;
  target_answer_sheet_id: string;
  similarity_percentage: number;
  highest_similarity: number;
  risk_level: string;
  status: string;
  reviewed_by?: string | null;
  reviewed_at?: string | null;
  teacher_notes?: string | null;
  created_at: string;
  updated_at: string;
}

interface PlagiarismSimilarity {
  id: string;
  source_answer_sheet_id: string;
  target_answer_sheet_id: string;
  source_question_mapping_id: string;
  target_question_mapping_id: string;
  semantic_similarity: number;
  lexical_similarity: number;
  overlap_similarity: number;
  final_similarity: number;
  risk_level: string;
}

interface QuestionMapping {
  id: string;
  answer_sheet_id: string;
  question_id?: string | null;
  detected_question_number?: number | null;
  detected_question_label?: string | null;
  extracted_answer_text: string;
  status: string;
  mapping_confidence: number;
}

export const PlagiarismReportViewer: React.FC = () => {
  const { reportId } = useParams<{ reportId: string }>();
  const { user } = useAuth();
  
  // Data states
  const [report, setReport] = useState<PlagiarismReport | null>(null);
  const [similarities, setSimilarities] = useState<PlagiarismSimilarity[]>([]);
  const [sourceSheet, setSourceSheet] = useState<AnswerSheet | null>(null);
  const [targetSheet, setTargetSheet] = useState<AnswerSheet | null>(null);
  const [studentA, setStudentA] = useState<Student | null>(null);
  const [studentB, setStudentB] = useState<Student | null>(null);
  const [sourceMappings, setSourceMappings] = useState<QuestionMapping[]>([]);
  const [targetMappings, setTargetMappings] = useState<QuestionMapping[]>([]);
  const [exam, setExam] = useState<Exam | null>(null);

  // Selector state
  const [selectedSimIndex, setSelectedSimIndex] = useState<number>(0);

  // Review form states
  const [reviewStatus, setReviewStatus] = useState<string>('CONFIRMED_PLAGIARISM');
  const [reviewNotes, setReviewNotes] = useState<string>('');
  
  // UI states
  const [loading, setLoading] = useState<boolean>(true);
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [exportingPdf, setExportingPdf] = useState<boolean>(false);
  const [downloadError, setDownloadError] = useState<string | null>(null);

  const isTeacher = user?.role === 'teacher' || user?.role === 'admin';

  const fetchReportDetails = async () => {
    setLoading(true);
    setError(null);
    try {
      // 1. Fetch all reports and find our report ID
      const reportsRes = await client.get('/plagiarism/reports');
      const foundReport = (reportsRes.data || []).find((r: any) => r.id === reportId);
      if (!foundReport) {
        throw new Error('Plagiarism report not found.');
      }
      setReport(foundReport);

      // 2. Fetch exam info
      try {
        const examRes = await client.get(`/exams/${foundReport.exam_id}`);
        setExam(examRes.data);
      } catch (examErr) {
        console.warn('Could not resolve exam info:', examErr);
      }

      // 3. Fetch source and target answer sheets
      const [srcSheetRes, tgtSheetRes] = await Promise.all([
        client.get(`/answer-sheets/${foundReport.source_answer_sheet_id}`),
        client.get(`/answer-sheets/${foundReport.target_answer_sheet_id}`)
      ]);
      setSourceSheet(srcSheetRes.data);
      setTargetSheet(tgtSheetRes.data);

      // 4. Fetch Student A and Student B details
      const [studentARes, studentBRes] = await Promise.all([
        client.get(`/students/${srcSheetRes.data.student_id}`),
        client.get(`/students/${tgtSheetRes.data.student_id}`)
      ]);
      setStudentA(studentARes.data);
      setStudentB(studentBRes.data);

      // 5. Fetch question-level similarities for this report
      const similaritiesRes = await client.get(`/plagiarism/${reportId}/similarities`);
      const simList = similaritiesRes.data || [];
      setSimilarities(simList);

      // 6. Fetch Question Mappings for extracted texts
      // Note: If user is not teacher, this might fail, so we wrap in try-catch to avoid breaking page load
      try {
        const [srcMappingsRes, tgtMappingsRes] = await Promise.all([
          client.get(`/ocr/${foundReport.source_answer_sheet_id}/mappings`),
          client.get(`/ocr/${foundReport.target_answer_sheet_id}/mappings`)
        ]);
        setSourceMappings(srcMappingsRes.data || []);
        setTargetMappings(tgtMappingsRes.data || []);
      } catch (mappingErr) {
        console.warn('Could not retrieve detailed OCR mappings. Restricting to read-only view.', mappingErr);
      }

    } catch (err: any) {
      console.error('Failed to load plagiarism report details:', err);
      setError(err?.response?.data?.detail || err.message || 'Failed to retrieve report data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (reportId) {
      fetchReportDetails();
    }
  }, [reportId]);

  // Handle Review submission
  const handleReviewSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isTeacher) return;
    
    // Strict validations
    if (!reviewNotes.trim()) {
      setValidationError('Review explanation reason is required.');
      return;
    }
    if (reviewNotes.length < 3) {
      setValidationError('Review reason must be at least 3 characters.');
      return;
    }
    if (reviewNotes.length > 1000) {
      setValidationError('Review notes must not exceed 1000 characters.');
      return;
    }

    setValidationError(null);
    setSubmitting(true);

    try {
      await client.post(`/plagiarism/${reportId}/review`, {
        status: reviewStatus,
        teacher_notes: reviewNotes.trim()
      });

      // Refresh report data
      await fetchReportDetails();
      
      // Clear form
      setReviewNotes('');
    } catch (err: any) {
      console.error('Failed to submit plagiarism review decision:', err);
      setError(err?.response?.data?.detail || 'Failed to submit review decision. Check inputs and permissions.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleExportPdf = async () => {
    if (!reportId) return;
    setExportingPdf(true);
    setDownloadError(null);
    try {
      await downloadFile(`/plagiarism/reports/${reportId}/export/pdf`);
    } catch (err: any) {
      console.error('Failed to export plagiarism report PDF:', err);
      setDownloadError(err?.response?.data?.detail || 'Failed to export plagiarism report PDF. Please try again.');
    } finally {
      setExportingPdf(false);
    }
  };

  // Status Badge Mapper
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'DETECTED':
        return (
          <span className="profile-value badge badge-info" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}>
            <Clock size={12} />
            <span>PENDING REVIEW</span>
          </span>
        );
      case 'CONFIRMED_PLAGIARISM':
        return (
          <span className="profile-value badge" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem', background: 'rgba(239, 68, 68, 0.1)', color: 'var(--color-error)', border: '1px solid rgba(239, 68, 68, 0.2)' }}>
            <AlertOctagon size={12} />
            <span>CONFIRMED PLAGIARISM</span>
          </span>
        );
      case 'FALSE_POSITIVE':
        return (
          <span className="profile-value badge" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem', background: 'rgba(255,255,255,0.05)', color: 'var(--text-secondary)', border: '1px solid var(--border-color)' }}>
            <Clock size={12} />
            <span>FALSE POSITIVE</span>
          </span>
        );
      case 'DISMISSED':
        return (
          <span className="profile-value badge badge-success" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}>
            <CheckCircle size={12} />
            <span>DISMISSED</span>
          </span>
        );
      default:
        return <span className="profile-value badge">{status}</span>;
    }
  };

  // Risk Badge Mapper
  const getRiskBadge = (risk: string) => {
    switch (risk) {
      case 'HIGH_RISK':
        return (
          <span className="profile-value badge" style={{ background: 'rgba(239, 68, 68, 0.1)', color: 'var(--color-error)', border: '1px solid rgba(239, 68, 68, 0.2)' }}>
            HIGH RISK
          </span>
        );
      case 'SUSPICIOUS':
        return (
          <span className="profile-value badge" style={{ background: 'rgba(245, 158, 11, 0.1)', color: 'rgb(245, 158, 11)', border: '1px solid rgba(245, 158, 11, 0.2)' }}>
            SUSPICIOUS
          </span>
        );
      case 'CLEAN':
        return (
          <span className="profile-value badge badge-success">
            CLEAN
          </span>
        );
      default:
        return <span className="profile-value badge">{risk}</span>;
    }
  };

  const getSimilarityColor = (pct: number) => {
    if (pct >= 70) return 'var(--color-error)';
    if (pct >= 40) return 'rgb(245, 158, 11)';
    return 'var(--color-success)';
  };

  // N-gram Matching highlighter to highlight identical or highly matching chunks of text.
  // Highlights contiguous phrases of 3 or more words appearing in both texts.
  const highlightMatches = (text: string, otherText: string) => {
    if (!text) return <span style={{ color: 'var(--text-secondary)', fontStyle: 'italic' }}>[No text extracted]</span>;
    if (!otherText) return <span>{text}</span>;

    const normalize = (t: string) => t.toLowerCase().replace(/[^\w\s]/g, '').trim();
    const normOther = normalize(otherText);
    
    // Split on whitespace tokens (retaining them)
    const tokens = text.split(/(\s+)/);
    const result: React.ReactNode[] = [];
    
    let i = 0;
    while (i < tokens.length) {
      const token = tokens[i];
      if (token.trim() === '') {
        result.push(token);
        i++;
        continue;
      }
      
      let matchedLength = 0;
      let tempPhrase = '';
      let wordCount = 0;
      
      for (let j = i; j < tokens.length; j++) {
        const subToken = tokens[j];
        if (subToken.trim() !== '') {
          tempPhrase += (tempPhrase ? ' ' : '') + subToken;
          wordCount++;
        } else {
          tempPhrase += subToken;
        }
        
        const normTemp = normalize(tempPhrase);
        if (normOther.includes(normTemp)) {
          if (wordCount >= 3) {
            matchedLength = j - i + 1;
          }
        } else {
          break; // Stop growing sequence if match fails
        }
      }
      
      if (matchedLength > 0) {
        const matchedSubstring = tokens.slice(i, i + matchedLength).join('');
        result.push(
          <span 
            key={i} 
            className="match-highlight" 
            style={{ 
              background: 'rgba(239, 68, 68, 0.18)', 
              borderBottom: '2px solid rgba(239, 68, 68, 0.4)', 
              borderRadius: '2px',
              paddingInline: '2px' 
            }}
          >
            {matchedSubstring}
          </span>
        );
        i += matchedLength;
      } else {
        result.push(token);
        i++;
      }
    }
    return result;
  };

  if (loading) {
    return (
      <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
        <div className="spinner-medium" style={{ margin: '0 auto 1.5rem auto' }} />
        <span>Loading side-by-side plagiarism comparison details...</span>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div style={{ padding: '2rem' }}>
        <Link to="/plagiarism" className="btn btn-secondary btn-sm" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', marginBottom: '1.5rem' }}>
          <ArrowLeft size={16} />
          <span>Back to Dashboard</span>
        </Link>
        <div className="error-banner">{error || 'Unable to retrieve plagiarism report details.'}</div>
      </div>
    );
  }

  // Question mapping helpers
  const sourceMappingMap = new Map(sourceMappings.map(m => [m.id, m]));
  const targetMappingMap = new Map(targetMappings.map(m => [m.id, m]));

  const activeSimilarity = similarities[selectedSimIndex];
  
  let activeSourceMapping: QuestionMapping | undefined;
  let activeTargetMapping: QuestionMapping | undefined;

  if (activeSimilarity) {
    activeSourceMapping = sourceMappingMap.get(activeSimilarity.source_question_mapping_id);
    activeTargetMapping = targetMappingMap.get(activeSimilarity.target_question_mapping_id);
  }

  const activeQuestionLabel = activeSourceMapping 
    ? (activeSourceMapping.detected_question_label || `Question ${activeSourceMapping.detected_question_number}`)
    : 'Selected Question';

  return (
    <div className="plagiarism-report-viewer-container" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      
      {/* Page Header Navigation */}
      <div>
        <Link to="/plagiarism" className="btn btn-secondary btn-sm" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', marginBottom: '1rem' }}>
          <ArrowLeft size={16} />
          <span>Back to Dashboard</span>
        </Link>

        <div className="page-header" style={{ marginBottom: 0, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1 style={{ fontSize: '1.5rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <ShieldAlert size={24} style={{ color: 'var(--color-error)' }} />
              <span>Plagiarism Report Viewer</span>
            </h1>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
              Comparing {studentA?.full_name || 'Student A'} and {studentB?.full_name || 'Student B'} in {exam?.title || 'Generic Exam'}.
            </p>
          </div>
          {isTeacher && (
            <button
              onClick={handleExportPdf}
              disabled={exportingPdf}
              className="btn btn-secondary"
              style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
            >
              {exportingPdf ? <RefreshCw size={16} className="spinner" /> : <FileText size={16} />}
              <span>Export PDF Report</span>
            </button>
          )}
        </div>
      </div>

      {downloadError && (
        <div className="error-banner" style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <AlertOctagon size={16} style={{ flexShrink: 0 }} />
          <span>{downloadError}</span>
        </div>
      )}

      {/* KPI Overview and Status Card */}
      <div className="detail-card" style={{ padding: '1.5rem', margin: 0, border: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', gap: '2rem', flexWrap: 'wrap' }}>
        
        {/* Similarity Score Percentage */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Overall Similarity</span>
            <strong style={{ fontSize: '2.5rem', color: getSimilarityColor(report.similarity_percentage), lineHeight: '1' }}>
              {report.similarity_percentage.toFixed(1)}%
            </strong>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>
            <div>{getRiskBadge(report.risk_level)}</div>
            <div>{getStatusBadge(report.status)}</div>
          </div>
        </div>

        {/* Existing review status notes if verified */}
        {report.reviewed_at && (
          <div style={{ flex: 1, minWidth: '250px', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '0.8rem 1.2rem', display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}>
                <User size={12} />
                <span>Reviewed by Teacher</span>
              </span>
              <span>{new Date(report.reviewed_at).toLocaleString()}</span>
            </div>
            {report.teacher_notes ? (
              <p style={{ fontSize: '0.85rem', fontStyle: 'italic', color: 'var(--text-primary)', marginTop: '0.2rem' }}>
                &ldquo;{report.teacher_notes}&rdquo;
              </p>
            ) : (
              <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>No review comments submitted.</span>
            )}
          </div>
        )}
      </div>

      {/* Question Selector and Individual Similarity Scores */}
      {similarities.length > 0 ? (
        <div className="detail-card" style={{ padding: '1.25rem', margin: 0, border: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          
          <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
            
            {/* Dropdown segment selector */}
            <div className="input-group" style={{ flex: 1, minWidth: '280px', margin: 0 }}>
              <label htmlFor="segmentSelect" style={{ fontSize: '0.8rem' }}>Switch Flagged Questions</label>
              <select
                id="segmentSelect"
                value={selectedSimIndex}
                onChange={(e) => setSelectedSimIndex(parseInt(e.target.value))}
                style={{ width: '100%', background: 'var(--bg-input)', color: 'var(--text-primary)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '0.5rem 0.8rem' }}
              >
                {similarities.map((sim, index) => {
                  const mapItem = sourceMappingMap.get(sim.source_question_mapping_id);
                  const label = mapItem 
                    ? (mapItem.detected_question_label || `Question ${mapItem.detected_question_number}`)
                    : `Mapping Pair #${index + 1}`;
                  return (
                    <option key={sim.id} value={index}>
                      {label} ({(sim.final_similarity * 100).toFixed(0)}% Similarity)
                    </option>
                  );
                })}
              </select>
            </div>

            {/* Individual similarity metrics display */}
            {activeSimilarity && (
              <div style={{ display: 'flex', gap: '1.5rem', flexGrow: 1, background: 'rgba(255,255,255,0.01)', borderRadius: '8px', border: '1px solid var(--border-color)', padding: '0.6rem 1.2rem', justifyContent: 'space-around' }}>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Semantic match</span>
                  <strong style={{ fontSize: '1.1rem', color: getSimilarityColor(activeSimilarity.semantic_similarity * 100) }}>
                    {(activeSimilarity.semantic_similarity * 100).toFixed(0)}%
                  </strong>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Lexical match</span>
                  <strong style={{ fontSize: '1.1rem', color: getSimilarityColor(activeSimilarity.lexical_similarity * 100) }}>
                    {(activeSimilarity.lexical_similarity * 100).toFixed(0)}%
                  </strong>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Overlap score</span>
                  <strong style={{ fontSize: '1.1rem', color: getSimilarityColor(activeSimilarity.overlap_similarity * 100) }}>
                    {(activeSimilarity.overlap_similarity * 100).toFixed(0)}%
                  </strong>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', borderLeft: '1px solid var(--border-color)', paddingLeft: '1.5rem' }}>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontWeight: 600 }}>Combined Similarity</span>
                  <strong style={{ fontSize: '1.25rem', color: getSimilarityColor(activeSimilarity.final_similarity * 100) }}>
                    {(activeSimilarity.final_similarity * 100).toFixed(1)}%
                  </strong>
                </div>
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="error-banner">No detailed matching question segments found in report.</div>
      )}

      {/* Split Comparative Pane */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        
        {/* LEFT COLUMN: Student A (Source) */}
        <div className="detail-card" style={{ padding: '1.5rem', margin: 0, border: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          
          {/* Header Metadata */}
          <div style={{ borderBottom: '1px solid var(--border-color)', paddingBottom: '0.8rem', display: 'flex', gap: '0.8rem', alignItems: 'center' }}>
            <div style={{ width: '40px', height: '40px', background: 'rgba(192, 132, 252, 0.1)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, color: 'var(--text-accent)' }}>
              <User size={20} style={{ marginInline: 'auto' }} />
            </div>
            <div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Student A (Source)</div>
              <strong style={{ fontSize: '1.05rem', color: 'var(--text-primary)' }}>{studentA?.full_name || 'Unknown Student'}</strong>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>ID: {studentA?.student_number || 'N/A'}</div>
            </div>
          </div>

          {/* Answer sheet metadata */}
          <div style={{ background: 'rgba(255,255,255,0.02)', padding: '0.6rem 1rem', borderRadius: '8px', border: '1px solid var(--border-color)', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <FileText size={14} style={{ color: 'var(--text-secondary)' }} />
            <span style={{ color: 'var(--text-secondary)' }}>Sheet:</span>
            <strong style={{ color: 'var(--text-primary)' }} title={sourceSheet?.original_filename}>
              {sourceSheet?.original_filename || 'source_sheet.pdf'}
            </strong>
          </div>

          {/* Text panel for Student A */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', flexGrow: 1 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontWeight: 600 }}>
                {activeQuestionLabel} - Extracted Answer
              </span>
              {activeSourceMapping && (
                <span className="profile-value badge" style={{ fontSize: '0.75rem', paddingBlock: '0.15rem' }}>
                  Confidence: {(activeSourceMapping.mapping_confidence * 100).toFixed(0)}%
                </span>
              )}
            </div>
            <div 
              style={{ 
                background: 'var(--bg-input)', 
                border: '1px solid var(--border-color)', 
                borderRadius: '8px', 
                padding: '1.25rem', 
                minHeight: '280px', 
                fontSize: '0.9rem', 
                lineHeight: '160%',
                whiteSpace: 'pre-wrap', 
                overflowY: 'auto',
                maxHeight: '450px'
              }}
            >
              {activeSourceMapping && activeTargetMapping ? (
                highlightMatches(activeSourceMapping.extracted_answer_text, activeTargetMapping.extracted_answer_text)
              ) : (
                <span style={{ color: 'var(--text-secondary)', fontStyle: 'italic' }}>Select a question to view comparison text.</span>
              )}
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN: Student B (Target) */}
        <div className="detail-card" style={{ padding: '1.5rem', margin: 0, border: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          
          {/* Header Metadata */}
          <div style={{ borderBottom: '1px solid var(--border-color)', paddingBottom: '0.8rem', display: 'flex', gap: '0.8rem', alignItems: 'center' }}>
            <div style={{ width: '40px', height: '40px', background: 'rgba(192, 132, 252, 0.1)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, color: 'var(--text-accent)' }}>
              <User size={20} style={{ marginInline: 'auto' }} />
            </div>
            <div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Student B (Target)</div>
              <strong style={{ fontSize: '1.05rem', color: 'var(--text-primary)' }}>{studentB?.full_name || 'Unknown Student'}</strong>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>ID: {studentB?.student_number || 'N/A'}</div>
            </div>
          </div>

          {/* Answer sheet metadata */}
          <div style={{ background: 'rgba(255,255,255,0.02)', padding: '0.6rem 1rem', borderRadius: '8px', border: '1px solid var(--border-color)', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <FileText size={14} style={{ color: 'var(--text-secondary)' }} />
            <span style={{ color: 'var(--text-secondary)' }}>Sheet:</span>
            <strong style={{ color: 'var(--text-primary)' }} title={targetSheet?.original_filename}>
              {targetSheet?.original_filename || 'target_sheet.pdf'}
            </strong>
          </div>

          {/* Text panel for Student B */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', flexGrow: 1 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontWeight: 600 }}>
                {activeQuestionLabel} - Extracted Answer
              </span>
              {activeTargetMapping && (
                <span className="profile-value badge" style={{ fontSize: '0.75rem', paddingBlock: '0.15rem' }}>
                  Confidence: {(activeTargetMapping.mapping_confidence * 100).toFixed(0)}%
                </span>
              )}
            </div>
            <div 
              style={{ 
                background: 'var(--bg-input)', 
                border: '1px solid var(--border-color)', 
                borderRadius: '8px', 
                padding: '1.25rem', 
                minHeight: '280px', 
                fontSize: '0.9rem', 
                lineHeight: '160%',
                whiteSpace: 'pre-wrap', 
                overflowY: 'auto',
                maxHeight: '450px'
              }}
            >
              {activeSourceMapping && activeTargetMapping ? (
                highlightMatches(activeTargetMapping.extracted_answer_text, activeSourceMapping.extracted_answer_text)
              ) : (
                <span style={{ color: 'var(--text-secondary)', fontStyle: 'italic' }}>Select a question to view comparison text.</span>
              )}
            </div>
          </div>
        </div>

      </div>

      {/* Teacher Review Form (Role security - only visible to teachers) */}
      {isTeacher ? (
        <div className="detail-card" style={{ padding: '1.5rem', margin: 0, border: '1px solid var(--border-color)' }}>
          <h3 className="detail-section-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.75rem', marginBottom: '1.25rem' }}>
            <MessageSquare size={18} style={{ color: 'var(--text-accent)' }} />
            <span>Submit Teacher Review Decision</span>
          </h3>

          {validationError && (
            <div className="error-banner" style={{ marginBottom: '1rem' }}>
              {validationError}
            </div>
          )}

          <form onSubmit={handleReviewSubmit} className="form-layout" style={{ maxWidth: '800px', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            
            {/* Status options radio grid */}
            <div className="input-group">
              <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>Plagiarism Decision Status</label>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginTop: '0.4rem' }}>
                
                {/* Option 1: Confirmed Plagiarism */}
                <label 
                  style={{ 
                    display: 'flex', 
                    flexDirection: 'column', 
                    gap: '0.4rem', 
                    padding: '1rem', 
                    borderRadius: '8px', 
                    border: `1px solid ${reviewStatus === 'CONFIRMED_PLAGIARISM' ? 'var(--color-error)' : 'var(--border-color)'}`, 
                    background: reviewStatus === 'CONFIRMED_PLAGIARISM' ? 'rgba(239, 68, 68, 0.05)' : 'var(--bg-input)', 
                    cursor: 'pointer',
                    transition: 'all 0.2s' 
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <input 
                      type="radio" 
                      name="decision_status" 
                      value="CONFIRMED_PLAGIARISM" 
                      checked={reviewStatus === 'CONFIRMED_PLAGIARISM'} 
                      onChange={(e) => setReviewStatus(e.target.value)} 
                      disabled={submitting}
                      style={{ accentColor: 'var(--color-error)' }}
                    />
                    <strong style={{ color: 'var(--color-error)', fontSize: '0.9rem' }}>Confirm Plagiarism</strong>
                  </div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                    Flags both student answer sheets as positive cases of plagiarism.
                  </span>
                </label>

                {/* Option 2: False Positive */}
                <label 
                  style={{ 
                    display: 'flex', 
                    flexDirection: 'column', 
                    gap: '0.4rem', 
                    padding: '1rem', 
                    borderRadius: '8px', 
                    border: `1px solid ${reviewStatus === 'FALSE_POSITIVE' ? 'var(--text-secondary)' : 'var(--border-color)'}`, 
                    background: reviewStatus === 'FALSE_POSITIVE' ? 'rgba(255,255,255,0.05)' : 'var(--bg-input)', 
                    cursor: 'pointer',
                    transition: 'all 0.2s' 
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <input 
                      type="radio" 
                      name="decision_status" 
                      value="FALSE_POSITIVE" 
                      checked={reviewStatus === 'FALSE_POSITIVE'} 
                      onChange={(e) => setReviewStatus(e.target.value)} 
                      disabled={submitting}
                      style={{ accentColor: 'var(--text-secondary)' }}
                    />
                    <strong style={{ color: 'var(--text-primary)', fontSize: '0.9rem' }}>False Positive</strong>
                  </div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                    Marks similarity match as an accidental overlap (e.g. definitions).
                  </span>
                </label>

                {/* Option 3: Dismissed */}
                <label 
                  style={{ 
                    display: 'flex', 
                    flexDirection: 'column', 
                    gap: '0.4rem', 
                    padding: '1rem', 
                    borderRadius: '8px', 
                    border: `1px solid ${reviewStatus === 'DISMISSED' ? 'var(--color-success)' : 'var(--border-color)'}`, 
                    background: reviewStatus === 'DISMISSED' ? 'rgba(16, 185, 129, 0.05)' : 'var(--bg-input)', 
                    cursor: 'pointer',
                    transition: 'all 0.2s' 
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <input 
                      type="radio" 
                      name="decision_status" 
                      value="DISMISSED" 
                      checked={reviewStatus === 'DISMISSED'} 
                      onChange={(e) => setReviewStatus(e.target.value)} 
                      disabled={submitting}
                      style={{ accentColor: 'var(--color-success)' }}
                    />
                    <strong style={{ color: 'var(--color-success)', fontSize: '0.9rem' }}>Dismiss Report</strong>
                  </div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                    Clears the warning incident logs without flagging the papers.
                  </span>
                </label>

              </div>
            </div>

            {/* Notes textarea field */}
            <div className="input-group">
              <label htmlFor="notesField" style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>Explanation notes & reason (Required)</span>
                <span style={{ fontSize: '0.75rem', color: reviewNotes.length > 1000 ? 'var(--color-error)' : 'var(--text-secondary)' }}>
                  {reviewNotes.length} / 1000 characters
                </span>
              </label>
              <textarea
                id="notesField"
                className="form-textarea"
                value={reviewNotes}
                onChange={(e) => {
                  setReviewNotes(e.target.value);
                  if (validationError) setValidationError(null);
                }}
                disabled={submitting}
                placeholder="Detail your review reasoning here... Note that this field is mandatory for audit trail validation."
                style={{ minHeight: '120px' }}
              />
            </div>

            {/* Submission button controls */}
            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end', marginTop: '0.5rem' }}>
              <button
                type="submit"
                className="btn btn-primary"
                disabled={submitting || reviewNotes.trim().length < 3 || reviewNotes.length > 1000}
                style={{ minWidth: '160px', justifyContent: 'center' }}
              >
                {submitting ? (
                  <>
                    <Activity size={16} className="spinner" style={{ animation: 'rotate 1s linear infinite' }} />
                    <span>Submitting...</span>
                  </>
                ) : (
                  <span>Submit Review Decision</span>
                )}
              </button>
            </div>

          </form>
        </div>
      ) : (
        /* Read-only feedback notice for students / unauthorized accounts */
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem', background: 'rgba(255,255,255,0.02)', border: '1px dashed var(--border-color)', borderRadius: '8px', padding: '1.25rem', color: 'var(--text-secondary)' }}>
          <ShieldAlert size={20} style={{ color: 'var(--text-secondary)', flexShrink: 0 }} />
          <div>
            <strong style={{ color: 'var(--text-primary)', fontSize: '0.9rem' }}>Read-only Access Enabled</strong>
            <p style={{ fontSize: '0.8rem', marginTop: '0.15rem' }}>
              Student or unauthorized account. Plagiarism review decision form and audit submissions are restricted.
            </p>
          </div>
        </div>
      )}

    </div>
  );
};
