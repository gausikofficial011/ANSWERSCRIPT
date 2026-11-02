/* eslint-disable react-hooks/set-state-in-effect */
/* eslint-disable @typescript-eslint/no-explicit-any */
/* eslint-disable react-hooks/exhaustive-deps */
import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { client } from '../../api/client';
import { 
  ArrowLeft, 
  RefreshCw, 
  AlertCircle, 
  Award, 
  TrendingUp, 
  TrendingDown,
  Percent,
  Download,
  FileText
} from 'lucide-react';
import { downloadFile } from '../../utils/download';

interface HistoryItem {
  exam_id: string;
  exam_title: string;
  subject_name: string;
  percentage: number;
  grade: string | null;
  pass_fail_status: string;
  published_status: string;
}

interface StudentResultsData {
  student_id: string;
  student_name: string;
  student_number: string;
  class_section: string | null;
  history: HistoryItem[];
}

export const StudentResultsViewer: React.FC = () => {
  const { studentId } = useParams<{ studentId: string }>();
  const navigate = useNavigate();

  const [data, setData] = useState<StudentResultsData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [exportingCsv, setExportingCsv] = useState<boolean>(false);
  const [downloadingPdf, setDownloadingPdf] = useState<boolean>(false);

  const fetchStudentHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await client.get(`/results/students/${studentId}`);
      setData(res.data);
    } catch (err: any) {
      console.error('Failed to load student results history:', err);
      setError(err?.response?.data?.detail || 'Failed to load student results history. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleExportHistoryCsv = async () => {
    if (!studentId) return;
    setExportingCsv(true);
    setError(null);
    try {
      await downloadFile(`/results/students/${studentId}/export/csv`);
    } catch (err: any) {
      console.error('Failed to export student results history:', err);
      setError(err?.response?.data?.detail || 'Failed to export history CSV. Please try again.');
    } finally {
      setExportingCsv(false);
    }
  };

  const handleDownloadTranscriptPdf = async () => {
    if (!studentId) return;
    setDownloadingPdf(true);
    setError(null);
    try {
      await downloadFile(`/results/students/${studentId}/transcript/pdf`);
    } catch (err: any) {
      console.error('Failed to download student transcript PDF:', err);
      setError(err?.response?.data?.detail || 'Failed to download transcript PDF. Please try again.');
    } finally {
      setDownloadingPdf(false);
    }
  };

  useEffect(() => {
    if (studentId) {
      fetchStudentHistory();
    }
  }, [studentId]);

  // Compute analytics if history is available
  const history = data?.history || [];
  const totalExams = history.length;
  
  const averagePercentage = totalExams > 0 
    ? history.reduce((sum, item) => sum + item.percentage, 0) / totalExams 
    : 0.0;

  const highestScore = totalExams > 0 
    ? Math.max(...history.map(item => item.percentage)) 
    : 0.0;

  const lowestScore = totalExams > 0 
    ? Math.min(...history.map(item => item.percentage)) 
    : 0.0;

  const passCount = history.filter(item => item.pass_fail_status === 'PASS').length;
  const passRate = totalExams > 0 
    ? (passCount / totalExams) * 100.0 
    : 0.0;

  // Grade boundaries matching: O (90), A+ (80), A (70), B+ (60), B (50), C (40), F (<40)
  const getLetterGrade = (percent: number): string => {
    if (percent >= 90.0) return 'O';
    if (percent >= 80.0) return 'A+';
    if (percent >= 70.0) return 'A';
    if (percent >= 60.0) return 'B+';
    if (percent >= 50.0) return 'B';
    if (percent >= 40.0) return 'C';
    return 'F';
  };

  const averageGrade = getLetterGrade(averagePercentage);

  return (
    <div className="dashboard-content animate-fadeIn">
      {/* Header back link */}
      <div className="dashboard-header-row">
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <button className="btn-secondary btn-icon-only" onClick={() => navigate('/results')}>
            <ArrowLeft size={16} />
          </button>
          <h1 className="dashboard-title" style={{ margin: 0 }}>
            Student Academic File
          </h1>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button className="btn-secondary" onClick={fetchStudentHistory} disabled={loading}>
            <RefreshCw size={16} className={loading ? 'spinner' : ''} />
            Refresh
          </button>
          {data && (
            <>
              <button
                className="btn-secondary"
                onClick={handleExportHistoryCsv}
                disabled={exportingCsv || downloadingPdf}
                style={{ gap: '0.4rem' }}
              >
                {exportingCsv ? <RefreshCw size={16} className="spinner" /> : <Download size={16} />}
                <span>Export History CSV</span>
              </button>
              <button
                className="btn-secondary"
                onClick={handleDownloadTranscriptPdf}
                disabled={exportingCsv || downloadingPdf}
                style={{ gap: '0.4rem' }}
              >
                {downloadingPdf ? <RefreshCw size={16} className="spinner" /> : <FileText size={16} />}
                <span>Download Transcript PDF</span>
              </button>
            </>
          )}
        </div>
      </div>

      {error && (
        <div className="error-banner">
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      {data && (
        <div className="results-student-grid" style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: '1.5rem', alignItems: 'start' }}>
          
          {/* Left Column: Student Profile & Performance Summary */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            
            {/* Student Profile Card */}
            <div className="glass-panel text-center" style={{ padding: '2rem 1.5rem' }}>
              <div className="avatar-placeholder" style={{ width: '80px', height: '80px', borderRadius: '50%', background: 'rgba(170, 59, 255, 0.15)', border: '1px solid rgba(170, 59, 255, 0.3)', color: 'var(--text-accent)', fontSize: '2.5rem', display: 'flex', alignItems: 'center', justifySelf: 'center', justifyContent: 'center', marginBottom: '1rem' }}>
                {data.student_name.charAt(0).toUpperCase()}
              </div>
              <h2 className="profile-name" style={{ fontSize: '1.35rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.25rem' }}>
                {data.student_name}
              </h2>
              <p className="profile-detail text-secondary" style={{ fontSize: '0.85rem', marginBottom: '1.25rem' }}>
                ID: {data.student_number} {data.class_section ? `| Section ${data.class_section}` : ''}
              </p>
              
              <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '1.25rem', display: 'flex', justifyContent: 'space-around' }}>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                  <span className="text-secondary" style={{ fontSize: '0.75rem' }}>Exams Taken</span>
                  <span style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--text-primary)' }}>{totalExams}</span>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                  <span className="text-secondary" style={{ fontSize: '0.75rem' }}>Avg. Score</span>
                  <span style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--text-accent)' }}>
                    {totalExams > 0 ? `${averagePercentage.toFixed(1)}%` : '—'}
                  </span>
                </div>
              </div>
            </div>

            {/* Performance Summary / Analytics Card */}
            <div className="glass-panel">
              <h3 className="panel-subtitle" style={{ paddingBottom: '0.75rem', marginBottom: '1rem', borderBottom: '1px solid var(--border-color)' }}>
                Performance Summary
              </h3>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                    <TrendingUp size={16} className="text-accent" />
                    <span>Highest Score</span>
                  </div>
                  <span style={{ fontWeight: 600 }}>{totalExams > 0 ? `${highestScore.toFixed(1)}%` : '—'}</span>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                    <TrendingDown size={16} className="text-secondary" />
                    <span>Lowest Score</span>
                  </div>
                  <span style={{ fontWeight: 600 }}>{totalExams > 0 ? `${lowestScore.toFixed(1)}%` : '—'}</span>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                    <Percent size={16} className="color-success" />
                    <span>Pass Rate</span>
                  </div>
                  <span style={{ fontWeight: 600 }} className="color-success">
                    {totalExams > 0 ? `${passRate.toFixed(1)}%` : '—'}
                  </span>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                    <Award size={16} className="text-accent" />
                    <span>Average Grade</span>
                  </div>
                  <span className="badge-info" style={{ fontWeight: 600 }}>{totalExams > 0 ? averageGrade : '—'}</span>
                </div>
              </div>
            </div>

          </div>

          {/* Right Column: Historical Results List */}
          <div className="glass-panel" style={{ minHeight: '440px' }}>
            <h3 className="panel-subtitle">Results History</h3>
            
            {history.length === 0 ? (
              <div className="empty-state" style={{ padding: '6rem 2rem' }}>
                <AlertCircle size={32} />
                <p>No results records found for this student.</p>
              </div>
            ) : (
              <div className="table-responsive">
                <table className="results-table">
                  <thead>
                    <tr>
                      <th>Subject</th>
                      <th>Exam</th>
                      <th>Percentage</th>
                      <th>Grade</th>
                      <th>Pass / Fail</th>
                      <th>Published</th>
                    </tr>
                  </thead>
                  <tbody>
                    {history.map((item) => (
                      <tr key={item.exam_id}>
                        <td>{item.subject_name}</td>
                        <td className="font-semibold">{item.exam_title}</td>
                        <td>{item.percentage?.toFixed(1)}%</td>
                        <td>
                          <span className="badge-info">{item.grade || 'F'}</span>
                        </td>
                        <td>
                          {item.pass_fail_status === 'PASS' ? (
                            <span className="badge-pass">PASS</span>
                          ) : (
                            <span className="badge-fail">FAIL</span>
                          )}
                        </td>
                        <td>
                          {item.published_status === 'PUBLISHED' ? (
                            <span className="badge-published">Published</span>
                          ) : (
                            <span className="badge-unpublished">Draft</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

        </div>
      )}
    </div>
  );
};
