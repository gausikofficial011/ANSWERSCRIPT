/* eslint-disable react-hooks/exhaustive-deps, react-hooks/set-state-in-effect */
import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { client } from '../../api/client';
import { Plus, Trash2, FileText, CheckCircle, Clock, AlertTriangle, HelpCircle, AlertOctagon } from 'lucide-react';
import { AnswerSheetUploadModal } from './AnswerSheetUploadModal';

interface Student {
  id: string;
  student_number: string;
  full_name: string;
}

interface AnswerSheet {
  id: string;
  exam_id: string;
  student_id: string;
  uploaded_by: string;
  original_filename: string;
  stored_filename: string;
  file_path: string;
  file_size_bytes: number;
  mime_type: string;
  page_count: number | null;
  status: string;
  error_message: string | null;
  processed_at: string | null;
  supersedes_answer_sheet_id: string | null;
  superseded_by_answer_sheet_id: string | null;
  processing_status: string;
  created_at: string;
  student?: Student;
}

interface AnswerSheetsTabProps {
  examId: string;
}

export const AnswerSheetsTab: React.FC<AnswerSheetsTabProps> = ({ examId }) => {
  const [sheets, setSheets] = useState<AnswerSheet[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState<boolean>(false);

  // Poll status interval helper
  const isPendingStatus = (status: string) => {
    const nonTerminal = [
      'UPLOADED',
      'QUEUED_FOR_OCR',
      'OCR_PROCESSING',
      'QUESTION_DETECTION',
      'ANSWER_SEGMENTATION',
      'QUESTION_MAPPING',
      'EVALUATION_PROCESSING',
    ];
    return nonTerminal.includes(status);
  };

  const fetchAnswerSheets = async (showLoading = true) => {
    if (showLoading) setLoading(true);
    try {
      // 1. Fetch answer sheets list
      const sheetsRes = await client.get('/answer-sheets', {
        params: { exam_id: examId, page: 1, page_size: 100 },
      });
      const items: AnswerSheet[] = sheetsRes.data.items || [];

      // 2. Fetch students directory to map student name/number to student_id
      const studentsRes = await client.get('/students', {
        params: { page: 1, page_size: 100 },
      });
      const students: Student[] = studentsRes.data.items || [];
      const studentMap = new Map<string, Student>();
      students.forEach((s) => studentMap.set(s.id, s));

      const enriched = items.map((sheet) => ({
        ...sheet,
        student: studentMap.get(sheet.student_id),
      }));

      setSheets(enriched);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch answer sheets:', err);
      setError('Failed to fetch uploaded answer sheets directory.');
    } finally {
      if (showLoading) setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnswerSheets(true);
  }, [examId]);

  // Set up polling logic
  useEffect(() => {
    const needsPolling = sheets.some((sheet) => isPendingStatus(sheet.status));
    if (!needsPolling) return;

    const interval = setInterval(() => {
      fetchAnswerSheets(false);
    }, 5000);

    return () => clearInterval(interval);
  }, [sheets]);

  const handleDelete = async (id: string, name: string) => {
    if (!window.confirm(`Are you sure you want to permanently delete answer sheet file "${name}"?`)) {
      return;
    }

    try {
      await client.delete(`/answer-sheets/${id}`);
      fetchAnswerSheets(false);
    } catch (err) {
      console.error('Failed to delete sheet:', err);
      alert('Failed to delete answer sheet. Please try again.');
    }
  };

  const getStatusBadge = (status: string, errorMsg: string | null) => {
    switch (status) {
      case 'UPLOADED':
      case 'QUEUED_FOR_OCR':
        return (
          <span className="profile-value badge badge-info" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }} title="Pending pipeline pick-up">
            <Clock size={12} />
            <span>PENDING</span>
          </span>
        );
      case 'OCR_PROCESSING':
      case 'QUESTION_DETECTION':
      case 'ANSWER_SEGMENTATION':
      case 'QUESTION_MAPPING':
      case 'EVALUATION_PROCESSING':
        return (
          <span className="profile-value badge" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem', background: 'rgba(170, 59, 255, 0.1)', color: 'var(--text-accent)', border: '1px solid rgba(170, 59, 255, 0.2)' }} title="Currently executing pipeline components">
            <span className="animate-spin" style={{ display: 'inline-block', width: '8px', height: '8px', border: '1.5px solid var(--text-accent)', borderTopColor: 'transparent', borderRadius: '50%' }} />
            <span>PROCESSING</span>
          </span>
        );
      case 'OCR_COMPLETED':
      case 'MAPPING_COMPLETED':
        return (
          <span className="profile-value badge badge-success" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }} title="OCR & layout segmentation completed">
            <CheckCircle size={12} />
            <span>MAPPING COMPLETED</span>
          </span>
        );
      case 'EVALUATION_COMPLETED':
        return (
          <span className="profile-value badge badge-success" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }} title="AI scoring completed">
            <CheckCircle size={12} />
            <span>AI EVALUATED</span>
          </span>
        );
      case 'TEACHER_REVIEW_PENDING':
        return (
          <span className="profile-value badge" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem', background: 'rgba(245, 158, 11, 0.1)', color: 'rgb(245, 158, 11)', border: '1px solid rgba(245, 158, 11, 0.2)' }} title="AI score complete, awaiting teacher verification">
            <Clock size={12} />
            <span>PENDING REVIEW</span>
          </span>
        );
      case 'VERIFIED':
        return (
          <span className="profile-value badge" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem', background: 'rgba(16, 185, 129, 0.1)', color: 'rgb(16, 185, 129)', border: '1px solid rgba(16, 185, 129, 0.2)' }} title="Evaluation and score verified by teacher">
            <CheckCircle size={12} />
            <span>VERIFIED</span>
          </span>
        );
      case 'PUBLISHED':
        return (
          <span className="profile-value badge" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem', background: 'rgba(6, 182, 212, 0.1)', color: 'rgb(6, 182, 212)', border: '1px solid rgba(6, 182, 212, 0.2)' }} title="Scores published to students">
            <CheckCircle size={12} />
            <span>PUBLISHED</span>
          </span>
        );
      case 'FAILED':
        return (
          <span className="profile-value badge" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem', background: 'rgba(239, 68, 68, 0.1)', color: 'var(--color-error)', border: '1px solid rgba(239, 68, 68, 0.2)' }} title={errorMsg || 'Pipeline process error'}>
            <AlertOctagon size={12} />
            <span>FAILED</span>
          </span>
        );
      case 'SUPERSEDED':
        return (
          <span className="profile-value badge" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem', background: 'rgba(255,255,255,0.05)', color: 'var(--text-secondary)', border: '1px solid var(--border-color)', textDecoration: 'line-through' }} title="Replaced by a newer sheet upload attempt">
            <AlertTriangle size={12} />
            <span>SUPERSEDED</span>
          </span>
        );
      default:
        return (
          <span className="profile-value badge" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}>
            <HelpCircle size={12} />
            <span>{status}</span>
          </span>
        );
    }
  };

  return (
    <div className="answer-sheets-tab" style={{ marginTop: '1.5rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--text-primary)' }}>Student Answer Sheets Directory</h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
            Manage exam submissions. Automates page conversion, OCR extraction, and segment coordinate mappings.
          </p>
        </div>
        <button
          type="button"
          onClick={() => setIsUploadModalOpen(true)}
          className="btn btn-primary"
        >
          <Plus size={18} />
          <span>Upload Answer Sheet</span>
        </button>
      </div>

      {error && <div className="error-banner" style={{ marginBottom: '1.5rem' }}>{error}</div>}

      <div className="table-container">
        {loading ? (
          <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
            Loading answer sheets directory...
          </div>
        ) : sheets.length === 0 ? (
          <div style={{ padding: '4rem 2rem', textAlign: 'center', color: 'var(--text-secondary)', border: '1px dashed var(--border-color)', borderRadius: '12px', background: 'rgba(0,0,0,0.1)' }}>
            <FileText size={48} style={{ color: 'var(--border-color)', marginInline: 'auto', marginBottom: '1rem' }} />
            <h3 style={{ fontSize: '1.1rem', color: 'var(--text-primary)', fontWeight: 600, marginBottom: '0.4rem' }}>No Submissions Uploaded</h3>
            <p style={{ fontSize: '0.85rem', maxWidth: '400px', marginInline: 'auto', marginBottom: '1.5rem' }}>
              Drag and drop student answer sheet scans (PDFs/Images) to trigger EasyOCR extraction and mapping.
            </p>
            <button
              onClick={() => setIsUploadModalOpen(true)}
              className="btn btn-primary"
            >
              <Plus size={16} />
              <span>Upload Files Now</span>
            </button>
          </div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Student Number</th>
                <th>Full Name</th>
                <th>Original File</th>
                <th>Pages</th>
                <th>Pipeline Status</th>
                <th>Uploaded At</th>
                <th style={{ width: '300px' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {sheets.map((sheet) => (
                <tr key={sheet.id} style={{ opacity: sheet.status === 'SUPERSEDED' ? 0.6 : 1 }}>
                  <td style={{ fontWeight: 600, color: sheet.status === 'SUPERSEDED' ? 'var(--text-secondary)' : 'var(--text-accent)' }}>
                    {sheet.student?.student_number || 'UNMAPPED'}
                  </td>
                  <td>{sheet.student?.full_name || <span style={{ color: 'var(--color-error)', fontStyle: 'italic' }}>Auto-mapping pending...</span>}</td>
                  <td style={{ maxWidth: '180px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={sheet.original_filename}>
                    {sheet.original_filename}
                  </td>
                  <td>{sheet.page_count ?? 'N/A'}</td>
                  <td>{getStatusBadge(sheet.status, sheet.error_message)}</td>
                  <td>{new Date(sheet.created_at).toLocaleString()}</td>
                  <td>
                    <div className="actions-cell">
                      <Link
                        to={`/exams/${examId}/answer-sheets/${sheet.id}/ocr`}
                        className={`btn btn-secondary btn-sm ${sheet.status === 'UPLOADED' || sheet.status === 'QUEUED_FOR_OCR' ? 'disabled' : ''}`}
                        style={{ pointerEvents: (sheet.status === 'UPLOADED' || sheet.status === 'QUEUED_FOR_OCR') ? 'none' : 'auto', opacity: (sheet.status === 'UPLOADED' || sheet.status === 'QUEUED_FOR_OCR') ? 0.5 : 1 }}
                        title="View raw extracted text and word confidence indexes"
                      >
                        OCR Text
                      </Link>
                      <Link
                        to={`/exams/${examId}/answer-sheets/${sheet.id}/mappings`}
                        className={`btn btn-secondary btn-sm ${['UPLOADED', 'QUEUED_FOR_OCR', 'OCR_PROCESSING', 'QUESTION_DETECTION'].includes(sheet.status) ? 'disabled' : ''}`}
                        style={{ pointerEvents: ['UPLOADED', 'QUEUED_FOR_OCR', 'OCR_PROCESSING', 'QUESTION_DETECTION'].includes(sheet.status) ? 'none' : 'auto', opacity: ['UPLOADED', 'QUEUED_FOR_OCR', 'OCR_PROCESSING', 'QUESTION_DETECTION'].includes(sheet.status) ? 0.5 : 1 }}
                        title="View segmented question mappings and coordinate bounding boxes"
                      >
                        Mappings
                      </Link>
                      <Link
                        to={`/exams/${examId}/answer-sheets/${sheet.id}/evaluations/view`}
                        className={`btn btn-secondary btn-sm ${!['EVALUATION_COMPLETED', 'TEACHER_REVIEW_PENDING', 'VERIFIED', 'PUBLISHED', 'PLAGIARISM_REVIEW_PENDING'].includes(sheet.status) ? 'disabled' : ''}`}
                        style={{ pointerEvents: !['EVALUATION_COMPLETED', 'TEACHER_REVIEW_PENDING', 'VERIFIED', 'PUBLISHED', 'PLAGIARISM_REVIEW_PENDING'].includes(sheet.status) ? 'none' : 'auto', opacity: !['EVALUATION_COMPLETED', 'TEACHER_REVIEW_PENDING', 'VERIFIED', 'PUBLISHED', 'PLAGIARISM_REVIEW_PENDING'].includes(sheet.status) ? 0.5 : 1 }}
                        title="View detailed AI question evaluations, marks and feedback summaries"
                      >
                        Evaluations
                      </Link>
                      <button
                        onClick={() => handleDelete(sheet.id, sheet.original_filename)}
                        className="btn btn-danger btn-sm"
                        title="Delete Answer Sheet Record"
                      >
                        <Trash2 size={13} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {isUploadModalOpen && (
        <AnswerSheetUploadModal
          examId={examId}
          onClose={() => setIsUploadModalOpen(false)}
          onUploadSuccess={() => fetchAnswerSheets(false)}
        />
      )}
    </div>
  );
};
