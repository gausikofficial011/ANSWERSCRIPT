/* eslint-disable react-hooks/exhaustive-deps, react-hooks/set-state-in-effect, @typescript-eslint/no-explicit-any */
import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { client } from '../../api/client';
import { 
  AlertTriangle, 
  ArrowLeft, 
  BookOpen, 
  Clock, 
  CheckCircle, 
  AlertOctagon, 
  Eye 
} from 'lucide-react';

interface Exam {
  id: string;
  title: string;
  description?: string;
  exam_date?: string;
}

interface Student {
  id: string;
  student_number: string;
  full_name: string;
}

interface AnswerSheet {
  id: string;
  student_id: string;
  original_filename: string;
}

interface FlaggedPair {
  report_id: string;
  source_answer_sheet_id: string;
  target_answer_sheet_id: string;
  similarity_percentage: number;
  highest_similarity: number;
  risk_level: string;
  status: string;
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
}

export const PlagiarismExamSummary: React.FC = () => {
  const { examId } = useParams<{ examId: string }>();
  const [exam, setExam] = useState<Exam | null>(null);
  const [summary, setSummary] = useState<any>(null);
  const [reports, setReports] = useState<PlagiarismReport[]>([]);
  const [students, setStudents] = useState<Student[]>([]);
  const [sheets, setSheets] = useState<AnswerSheet[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchExamSummaryData = async () => {
    setLoading(true);
    setError(null);
    try {
      // 1. Fetch Exam Metadata
      const examRes = await client.get(`/exams/${examId}`);
      setExam(examRes.data);

      // 2. Fetch Plagiarism Exam Summary
      const summaryRes = await client.get(`/plagiarism/exams/${examId}/summary`);
      setSummary(summaryRes.data);

      // 3. Fetch Plagiarism Reports (to calculate accurate pending/reviewed counts)
      const reportsRes = await client.get('/plagiarism/reports', { params: { exam_id: examId } });
      setReports(reportsRes.data || []);

      // 4. Fetch Students directory (for Student A / Student B names mapping)
      const studentsRes = await client.get('/students', { params: { page: 1, page_size: 100 } });
      setStudents(studentsRes.data.items || []);

      // 5. Fetch Answer Sheets directory (for mapping student IDs to sheets)
      const sheetsRes = await client.get('/answer-sheets', { params: { page: 1, page_size: 100 } });
      setSheets(sheetsRes.data.items || []);

    } catch (err) {
      console.error('Failed to load exam plagiarism summary:', err);
      setError('Failed to fetch plagiarism details for this exam. Please ensure the exam ID is valid.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (examId) {
      fetchExamSummaryData();
    }
  }, [examId]);

  // Helper Maps for mapping IDs to names/details
  const studentMap = new Map<string, Student>();
  students.forEach((s) => studentMap.set(s.id, s));

  const sheetMap = new Map<string, AnswerSheet>();
  sheets.forEach((sh) => sheetMap.set(sh.id, sh));

  const resolveStudentInfo = (sheetId: string) => {
    const sheet = sheetMap.get(sheetId);
    if (!sheet) return { name: 'Unknown Student', number: 'N/A' };
    const student = studentMap.get(sheet.student_id);
    return student 
      ? { name: student.full_name, number: student.student_number }
      : { name: 'Awaiting Mapping', number: 'N/A' };
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
            <span>CONFIRMED</span>
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

  if (loading) {
    return (
      <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
        <div className="spinner-medium" style={{ margin: '0 auto 1.5rem auto' }} />
        <span>Loading exam plagiarism details...</span>
      </div>
    );
  }

  if (error || !exam || !summary) {
    return (
      <div style={{ padding: '2rem' }}>
        <Link to="/plagiarism" className="btn btn-secondary btn-sm" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', marginBottom: '1.5rem' }}>
          <ArrowLeft size={16} />
          <span>Back to Dashboard</span>
        </Link>
        <div className="error-banner">{error || 'Unable to load exam plagiarism details.'}</div>
      </div>
    );
  }

  // Calculate detailed counts from reports list
  const pendingCount = reports.filter((r) => r.status === 'DETECTED').length;
  const reviewedCount = reports.length - pendingCount;
  const flaggedCount = reports.filter((r) => r.risk_level === 'HIGH_RISK' || r.risk_level === 'SUSPICIOUS').length;

  return (
    <div className="plagiarism-exam-summary-container" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      
      {/* Back button and page title */}
      <div>
        <Link to="/plagiarism" className="btn btn-secondary btn-sm" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', marginBottom: '1rem' }}>
          <ArrowLeft size={16} />
          <span>Back to Dashboard</span>
        </Link>
        
        <div className="page-header" style={{ marginBottom: 0 }}>
          <div>
            <h1 style={{ fontSize: '1.5rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <BookOpen size={24} style={{ color: 'var(--text-accent)' }} />
              <span>Plagiarism Summary: {exam.title}</span>
            </h1>
            {exam.description && (
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
                {exam.description}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* KPI metrics row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '1rem' }}>
        <div className="detail-card" style={{ display: 'flex', flexDirection: 'column', padding: '1.25rem', margin: 0, border: '1px solid var(--border-color)' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Total Reports</span>
          <strong style={{ fontSize: '1.75rem', color: 'var(--text-primary)', marginTop: '0.2rem' }}>{summary.total_reports}</strong>
        </div>
        <div className="detail-card" style={{ display: 'flex', flexDirection: 'column', padding: '1.25rem', margin: 0, border: '1px solid var(--border-color)' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Flagged Reports</span>
          <strong style={{ fontSize: '1.75rem', color: 'var(--color-error)', marginTop: '0.2rem' }}>{flaggedCount}</strong>
        </div>
        <div className="detail-card" style={{ display: 'flex', flexDirection: 'column', padding: '1.25rem', margin: 0, border: '1px solid var(--border-color)' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Reviewed Reports</span>
          <strong style={{ fontSize: '1.75rem', color: 'var(--color-success)', marginTop: '0.2rem' }}>{reviewedCount}</strong>
        </div>
        <div className="detail-card" style={{ display: 'flex', flexDirection: 'column', padding: '1.25rem', margin: 0, border: '1px solid var(--border-color)' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Pending Reports</span>
          <strong style={{ fontSize: '1.75rem', color: 'rgb(245, 158, 11)', marginTop: '0.2rem' }}>{pendingCount}</strong>
        </div>
        <div className="detail-card" style={{ display: 'flex', flexDirection: 'column', padding: '1.25rem', margin: 0, border: '1px solid var(--border-color)' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Flagged Answer Sheets</span>
          <strong style={{ fontSize: '1.75rem', color: 'var(--text-accent)', marginTop: '0.2rem' }}>{summary.flagged_sheets_count}</strong>
        </div>
      </div>

      {/* Similarity KPI Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
        <div className="detail-card" style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', padding: '1.5rem', margin: 0, border: '1px solid var(--border-color)' }}>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Highest Similarity</span>
            <strong style={{ fontSize: '2rem', color: getSimilarityColor(summary.highest_similarity * 100), marginTop: '0.2rem' }}>
              {(summary.highest_similarity * 100).toFixed(1)}%
            </strong>
          </div>
          <div style={{ flexGrow: 1, height: '8px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', overflow: 'hidden' }}>
            <div style={{ height: '100%', width: `${Math.min(100, summary.highest_similarity * 100)}%`, background: getSimilarityColor(summary.highest_similarity * 100) }} />
          </div>
        </div>

        <div className="detail-card" style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', padding: '1.5rem', margin: 0, border: '1px solid var(--border-color)' }}>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Average Similarity</span>
            <strong style={{ fontSize: '2rem', color: getSimilarityColor(summary.average_similarity), marginTop: '0.2rem' }}>
              {summary.average_similarity.toFixed(1)}%
            </strong>
          </div>
          <div style={{ flexGrow: 1, height: '8px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', overflow: 'hidden' }}>
            <div style={{ height: '100%', width: `${Math.min(100, summary.average_similarity)}%`, background: getSimilarityColor(summary.average_similarity) }} />
          </div>
        </div>
      </div>

      {/* Top Flagged Pairs List */}
      <div className="detail-card" style={{ padding: '1.5rem', margin: 0, border: '1px solid var(--border-color)' }}>
        <h3 className="detail-section-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.75rem', marginBottom: '1.25rem' }}>
          <AlertTriangle size={18} style={{ color: 'var(--color-error)' }} />
          <span>Top Flagged Similarity Pairs (Highest Risk)</span>
        </h3>

        {summary.top_flagged_pairs.length === 0 ? (
          <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
            No plagiarism incidents flagged for this exam.
          </div>
        ) : (
          <div className="table-container" style={{ margin: 0 }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Student A (Source)</th>
                  <th>Student B (Target)</th>
                  <th style={{ width: '150px' }}>Max Similarity</th>
                  <th style={{ width: '150px' }}>Risk Level</th>
                  <th style={{ width: '180px' }}>Review Status</th>
                  <th style={{ width: '150px', textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {summary.top_flagged_pairs.map((pair: FlaggedPair) => {
                  const s1 = resolveStudentInfo(pair.source_answer_sheet_id);
                  const s2 = resolveStudentInfo(pair.target_answer_sheet_id);

                  return (
                    <tr key={pair.report_id}>
                      <td>
                        <div style={{ fontWeight: 600 }}>{s1.name}</div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{s1.number}</div>
                      </td>
                      <td>
                        <div style={{ fontWeight: 600 }}>{s2.name}</div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{s2.number}</div>
                      </td>
                      <td style={{ fontWeight: 700, color: getSimilarityColor(pair.highest_similarity * 100) }}>
                        {(pair.highest_similarity * 100).toFixed(1)}%
                      </td>
                      <td>{getRiskBadge(pair.risk_level)}</td>
                      <td>{getStatusBadge(pair.status)}</td>
                      <td style={{ textAlign: 'right' }}>
                        <Link
                          to={`/plagiarism/reports/${pair.report_id}`}
                          className="btn btn-primary btn-sm"
                          style={{ paddingBlock: '0.3rem', fontSize: '0.8rem', gap: '0.3rem', display: 'inline-flex' }}
                        >
                          <Eye size={12} />
                          <span>View Report</span>
                        </Link>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

    </div>
  );
};
