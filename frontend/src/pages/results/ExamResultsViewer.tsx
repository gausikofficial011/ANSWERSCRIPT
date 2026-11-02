/* eslint-disable react-hooks/set-state-in-effect */
/* eslint-disable @typescript-eslint/no-explicit-any */
/* eslint-disable react-hooks/exhaustive-deps */
import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { client } from '../../api/client';
import { useAuth } from '../../context/AuthContext';
import { 
  ArrowLeft, 
  Search, 
  RefreshCw, 
  AlertCircle, 
  CheckCircle, 
  Send,
  Eye,
  Download,
  FileText
} from 'lucide-react';
import { downloadFile } from '../../utils/download';

interface ResultItem {
  student_id: string;
  student_name: string;
  student_number: string;
  marks_obtained: number;
  percentage: number;
  grade: string | null;
  pass_fail_status: string;
  verification_status: string;
  publication_status: string;
}

interface ExamResultsData {
  exam_id: string;
  exam_title: string;
  total_marks: number;
  passing_marks: number;
  items: ResultItem[];
  total_items: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export const ExamResultsViewer: React.FC = () => {
  const { examId } = useParams<{ examId: string }>();
  const { user } = useAuth();
  const navigate = useNavigate();

  const [data, setData] = useState<ExamResultsData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [exportingCsv, setExportingCsv] = useState<boolean>(false);
  const [downloadingPdf, setDownloadingPdf] = useState<boolean>(false);

  // Pagination & Search States
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(10);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [searchVal, setSearchVal] = useState<string>('');

  // Publish Modal State
  const [showConfirmModal, setShowConfirmModal] = useState<boolean>(false);
  const [publishing, setPublishing] = useState<boolean>(false);
  const [publishError, setPublishError] = useState<string | null>(null);
  const [publishSuccess, setPublishSuccess] = useState<string | null>(null);

  const fetchResults = async (page: number = currentPage, size: number = pageSize, search: string = searchQuery) => {
    setLoading(true);
    setError(null);
    try {
      const res = await client.get(`/results/exams/${examId}`, {
        params: {
          page,
          page_size: size,
          search: search.trim() || undefined
        }
      });
      setData(res.data);
    } catch (err: any) {
      console.error('Failed to load exam results details:', err);
      setError(err?.response?.data?.detail || 'Failed to load exam results details. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (examId) {
      fetchResults(currentPage, pageSize, searchQuery);
    }
  }, [examId, currentPage, pageSize, searchQuery]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setCurrentPage(1);
    setSearchQuery(searchVal);
  };

  const handleClearSearch = () => {
    setSearchVal('');
    setSearchQuery('');
    setCurrentPage(1);
  };

  const handleOpenPublishModal = () => {
    setPublishError(null);
    setPublishSuccess(null);
    setShowConfirmModal(true);
  };

  const handleConfirmPublish = async () => {
    if (!examId) return;
    setPublishing(true);
    setPublishError(null);
    try {
      const res = await client.post(`/results/exams/${examId}/publish`);
      setPublishSuccess(`Successfully published results for ${res.data.published_count} answer sheets.`);
      
      // Reload results
      await fetchResults(currentPage, pageSize, searchQuery);
      
      setTimeout(() => {
        setShowConfirmModal(false);
        setPublishSuccess(null);
      }, 2000);
    } catch (err: any) {
      console.error('Publishing failed:', err);
      setPublishError(err?.response?.data?.detail || 'Publishing failed. Ensure all papers are verified and free of active plagiarism.');
    } finally {
      setPublishing(false);
    }
  };

  // Check if exam still contains unpublished results
  const hasUnpublished = data ? data.items.some(item => item.publication_status === 'UNPUBLISHED') : false;

  const handleExportCSV = async () => {
    if (!examId) return;
    setExportingCsv(true);
    setError(null);
    try {
      await downloadFile(`/results/exams/${examId}/export/csv`);
    } catch (err: any) {
      console.error('Failed to export CSV results:', err);
      setError(err?.response?.data?.detail || 'Failed to export results CSV. Please try again.');
    } finally {
      setExportingCsv(false);
    }
  };

  const handleDownloadPDF = async () => {
    if (!examId) return;
    setDownloadingPdf(true);
    setError(null);
    try {
      await downloadFile(`/results/exams/${examId}/report/pdf`);
    } catch (err: any) {
      console.error('Failed to download exam report PDF:', err);
      setError(err?.response?.data?.detail || 'Failed to download exam report PDF. Please try again.');
    } finally {
      setDownloadingPdf(false);
    }
  };

  return (
    <div className="dashboard-content animate-fadeIn">
      {/* Header Back Link & Refresh */}
      <div className="dashboard-header-row">
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <button className="btn-secondary btn-icon-only" onClick={() => navigate('/results')}>
            <ArrowLeft size={16} />
          </button>
          <h1 className="dashboard-title" style={{ margin: 0 }}>
            {data ? data.exam_title : 'Exam Results Details'}
          </h1>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button className="btn-secondary" onClick={() => fetchResults(currentPage, pageSize, searchQuery)} disabled={loading}>
            <RefreshCw size={16} className={loading ? 'spinner' : ''} />
            Refresh
          </button>

          {(user?.role === 'teacher' || user?.role === 'admin') && data && (
            <>
              <button 
                className="btn-secondary" 
                onClick={handleExportCSV} 
                disabled={exportingCsv || downloadingPdf}
                style={{ gap: '0.4rem' }}
              >
                {exportingCsv ? <RefreshCw size={16} className="spinner" /> : <Download size={16} />}
                <span>Export Results CSV</span>
              </button>
              <button 
                className="btn-secondary" 
                onClick={handleDownloadPDF} 
                disabled={exportingCsv || downloadingPdf}
                style={{ gap: '0.4rem' }}
              >
                {downloadingPdf ? <RefreshCw size={16} className="spinner" /> : <FileText size={16} />}
                <span>Download Exam Report PDF</span>
              </button>
            </>
          )}

          {user?.role === 'teacher' && data && hasUnpublished && (
            <button className="btn-primary" onClick={handleOpenPublishModal}>
              <Send size={16} />
              Publish Results
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="error-banner">
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      {/* Exam Specs Panel */}
      {data && (
        <div className="glass-panel results-summary-bar" style={{ display: 'flex', gap: '3rem', padding: '1.25rem 2rem', marginBottom: '1.5rem' }}>
          <div className="spec-item">
            <span className="spec-label">Total Submissions</span>
            <span className="spec-value">{data.total_items} sheets</span>
          </div>
          <div className="spec-item">
            <span className="spec-label">Maximum Marks</span>
            <span className="spec-value">{data.total_marks} marks</span>
          </div>
          <div className="spec-item">
            <span className="spec-label">Passing Mark</span>
            <span className="spec-value">{data.passing_marks} marks</span>
          </div>
        </div>
      )}

      {/* Search Filter and Size selector */}
      <div className="results-filter-row" style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem', gap: '1rem' }}>
        <form onSubmit={handleSearchSubmit} className="search-box-form" style={{ display: 'flex', flexGrow: 1, maxWidth: '480px' }}>
          <div className="input-wrapper" style={{ flexGrow: 1 }}>
            <Search className="field-icon" size={18} />
            <input 
              type="text" 
              placeholder="Search by student name or number..." 
              value={searchVal}
              onChange={(e) => setSearchVal(e.target.value)}
            />
            {searchQuery && (
              <button 
                type="button" 
                className="btn-clear-search" 
                onClick={handleClearSearch}
                style={{ position: 'absolute', right: '1rem', background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer' }}
              >
                ✕
              </button>
            )}
          </div>
          <button type="submit" className="btn-submit" style={{ borderTopLeftRadius: 0, borderBottomLeftRadius: 0, padding: '0 1.25rem' }}>
            Search
          </button>
        </form>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span className="text-secondary" style={{ fontSize: '0.85rem' }}>Rows per page:</span>
          <select 
            value={pageSize}
            onChange={(e) => {
              const newSize = Number(e.target.value);
              setPageSize(newSize);
              setCurrentPage(1);
            }}
            className="select-input"
            style={{ width: '80px', padding: '0.4rem 0.5rem', background: 'var(--bg-input)', border: '1px solid var(--border-color)', borderRadius: '6px', color: 'var(--text-primary)' }}
          >
            <option value={5}>5</option>
            <option value={10}>10</option>
            <option value={20}>20</option>
            <option value={50}>50</option>
          </select>
        </div>
      </div>

      {/* Results Table */}
      <div className="glass-panel">
        {loading ? (
          <div className="loading-state">
            <RefreshCw size={24} className="spinner" />
            <p>Loading result rows...</p>
          </div>
        ) : !data || data.items.length === 0 ? (
          <div className="empty-state">
            <AlertCircle size={32} />
            <p>No student results matched criteria.</p>
          </div>
        ) : (
          <>
            <div className="table-responsive">
              <table className="results-table">
                <thead>
                  <tr>
                    <th>Student Number</th>
                    <th>Student Name</th>
                    <th>Marks Obtained</th>
                    <th>Percentage</th>
                    <th>Grade</th>
                    <th>Pass / Fail</th>
                    <th>Published Status</th>
                    <th style={{ textAlign: 'right' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {data.items.map((item) => (
                    <tr key={item.student_id}>
                      <td className="font-semibold">{item.student_number}</td>
                      <td>{item.student_name}</td>
                      <td>{item.marks_obtained?.toFixed(1)} / {data.total_marks}</td>
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
                        {item.publication_status === 'PUBLISHED' ? (
                          <span className="badge-published">Published</span>
                        ) : (
                          <span className="badge-unpublished">Draft / Unpublished</span>
                        )}
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        <button
                          className="btn-icon"
                          title="View Student History"
                          onClick={() => navigate(`/results/students/${item.student_id}`)}
                        >
                          <Eye size={16} />
                          <span>View History</span>
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination Controls */}
            {data.total_pages > 1 && (
              <div className="pagination-bar" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1.5rem', padding: '0 0.5rem' }}>
                <span className="text-secondary" style={{ fontSize: '0.85rem' }}>
                  Showing Page {data.page} of {data.total_pages} ({data.total_items} total items)
                </span>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <button
                    className="btn-secondary"
                    disabled={data.page <= 1}
                    onClick={() => setCurrentPage(data.page - 1)}
                  >
                    Previous
                  </button>
                  <button
                    className="btn-secondary"
                    disabled={data.page >= data.total_pages}
                    onClick={() => setCurrentPage(data.page + 1)}
                  >
                    Next
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Confirmation Modal */}
      {showConfirmModal && (
        <div className="modal-overlay">
          <div className="modal-container animate-scaleIn">
            <h3 className="modal-title">Confirm Release</h3>
            <p className="modal-message">
              Publishing results will make all eligible verified results available to students.
              <br />
              <strong>This action cannot be undone.</strong>
            </p>

            {publishError && (
              <div className="error-banner" style={{ margin: '1rem 0 0 0' }}>
                <AlertCircle size={16} />
                <span>{publishError}</span>
              </div>
            )}

            {publishSuccess && (
              <div className="status-valid" style={{ border: '1px solid rgba(16, 185, 129, 0.3)', padding: '0.75rem 1rem', borderRadius: '8px', marginTop: '1rem', display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                <CheckCircle size={16} />
                <span style={{ fontSize: '0.85rem' }}>{publishSuccess}</span>
              </div>
            )}

            <div className="modal-buttons">
              <button 
                className="btn-secondary" 
                onClick={() => setShowConfirmModal(false)}
                disabled={publishing}
              >
                Cancel
              </button>
              <button 
                className="btn-submit" 
                onClick={handleConfirmPublish}
                disabled={publishing}
              >
                {publishing ? 'Publishing...' : 'Confirm Publish'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
