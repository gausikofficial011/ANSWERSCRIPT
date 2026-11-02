/* eslint-disable react-hooks/set-state-in-effect */
/* eslint-disable @typescript-eslint/no-explicit-any */
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { client } from '../../api/client';
import { useAuth } from '../../context/AuthContext';
import { 
  GraduationCap, 
  Users, 
  Award, 
  Globe, 
  CheckCircle, 
  AlertCircle, 
  TrendingUp, 
  RefreshCw,
  Eye,
  Send
} from 'lucide-react';

interface DashboardStats {
  total_students_evaluated: number;
  total_results: number;
  total_published: number;
  pending_publication: number;
  average_score: number;
  pass_rate: number;
  fail_rate: number;
}

interface Exam {
  id: string;
  title: string;
  subject_id: string;
  status: string;
  total_marks: number;
}

interface Subject {
  id: string;
  name: string;
  code: string;
}

interface ExamStatsCache {
  [examId: string]: {
    studentCount: number;
    isPublished: boolean;
    hasUnpublished: boolean;
    loading: boolean;
  };
}

export const ResultsDashboard: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [exams, setExams] = useState<Exam[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [examStats, setExamStats] = useState<ExamStatsCache>({});

  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Publish Modal State
  const [showConfirmModal, setShowConfirmModal] = useState<boolean>(false);
  const [selectedExamId, setSelectedExamId] = useState<string | null>(null);
  const [publishing, setPublishing] = useState<boolean>(false);
  const [publishError, setPublishError] = useState<string | null>(null);
  const [publishSuccess, setPublishSuccess] = useState<string | null>(null);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError(null);
    try {
      // 1. Fetch KPI stats
      const statsRes = await client.get('/results/dashboard');
      setStats(statsRes.data);

      // 2. Fetch Exams List
      const examsRes = await client.get('/exams', { params: { page: 1, page_size: 100 } });
      setExams(examsRes.data.items || []);

      // 3. Fetch Subjects List
      const subjectsRes = await client.get('/subjects', { params: { page: 1, page_size: 100 } });
      setSubjects(subjectsRes.data.items || []);
    } catch (err: any) {
      console.error('Failed to load results dashboard data:', err);
      setError(err?.response?.data?.detail || 'Failed to load results dashboard data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const loadExamStats = async (examId: string) => {
    // Avoid re-fetching if already loading
    if (examStats[examId]?.loading) return;

    setExamStats(prev => ({
      ...prev,
      [examId]: { ...prev[examId], loading: true } as any
    }));

    try {
      const res = await client.get(`/results/exams/${examId}`);
      const items = res.data.items || [];
      const studentCount = res.data.total_items || items.length;
      
      // Determine if published/unpublished
      const isPublished = items.length > 0 && items.every((item: any) => item.publication_status === 'PUBLISHED');
      const hasUnpublished = items.some((item: any) => item.publication_status === 'UNPUBLISHED');

      setExamStats(prev => ({
        ...prev,
        [examId]: {
          studentCount,
          isPublished,
          hasUnpublished,
          loading: false
        }
      }));
    } catch (err) {
      console.error(`Failed to load stats for exam ${examId}:`, err);
      setExamStats(prev => ({
        ...prev,
        [examId]: {
          studentCount: 0,
          isPublished: false,
          hasUnpublished: false,
          loading: false
        }
      }));
    }
  };

  const subjectMap = new Map<string, string>();
  subjects.forEach(sub => subjectMap.set(sub.id, `${sub.name} (${sub.code})`));

  const handleOpenPublishModal = (examId: string) => {
    setSelectedExamId(examId);
    setPublishError(null);
    setPublishSuccess(null);
    setShowConfirmModal(true);
  };

  const handleConfirmPublish = async () => {
    if (!selectedExamId) return;
    setPublishing(true);
    setPublishError(null);
    try {
      const res = await client.post(`/results/exams/${selectedExamId}/publish`);
      setPublishSuccess(`Successfully published results for ${res.data.published_count} answer sheets.`);
      
      // Update local exam cache stats and stats dashboard overview
      await loadExamStats(selectedExamId);
      
      const newStats = await client.get('/results/dashboard');
      setStats(newStats.data);
      
      setTimeout(() => {
        setShowConfirmModal(false);
        setSelectedExamId(null);
        setPublishSuccess(null);
      }, 2000);
    } catch (err: any) {
      console.error('Publishing failed:', err);
      setPublishError(err?.response?.data?.detail || 'Publishing failed. Please verify that all sheets are verified and free of active plagiarism.');
    } finally {
      setPublishing(false);
    }
  };

  return (
    <div className="dashboard-content animate-fadeIn">
      <div className="dashboard-header-row">
        <h1 className="dashboard-title">
          <GraduationCap className="dashboard-title-icon" size={28} />
          Academic Results & Publishing
        </h1>
        <button className="btn-secondary" onClick={fetchDashboardData} disabled={loading}>
          <RefreshCw size={16} className={loading ? 'spinner' : ''} />
          Refresh
        </button>
      </div>

      {error && (
        <div className="error-banner">
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      {/* KPI Cards Grid */}
      <div className="results-kpi-grid">
        <div className="results-card">
          <div className="results-card-header">
            <Users className="results-card-icon text-accent" size={22} />
            <span className="results-card-title">Total Students Evaluated</span>
          </div>
          <div className="results-card-value">
            {loading ? '...' : stats?.total_students_evaluated ?? 0}
          </div>
        </div>

        <div className="results-card">
          <div className="results-card-header">
            <Award className="results-card-icon color-success" size={22} />
            <span className="results-card-title">Total Results Saved</span>
          </div>
          <div className="results-card-value">
            {loading ? '...' : stats?.total_results ?? 0}
          </div>
        </div>

        <div className="results-card">
          <div className="results-card-header">
            <Globe className="results-card-icon text-accent" size={22} />
            <span className="results-card-title">Total Published</span>
          </div>
          <div className="results-card-value">
            {loading ? '...' : stats?.total_published ?? 0}
          </div>
        </div>

        <div className="results-card">
          <div className="results-card-header">
            <AlertCircle className="results-card-icon text-secondary" size={22} />
            <span className="results-card-title">Pending Release</span>
          </div>
          <div className="results-card-value">
            {loading ? '...' : stats?.pending_publication ?? 0}
          </div>
        </div>

        <div className="results-card">
          <div className="results-card-header">
            <TrendingUp className="results-card-icon text-accent" size={22} />
            <span className="results-card-title">Average Performance</span>
          </div>
          <div className="results-card-value">
            {loading ? '...' : `${stats?.average_score?.toFixed(1) ?? '0.0'}%`}
          </div>
        </div>

        <div className="results-card">
          <div className="results-card-header">
            <CheckCircle className="results-card-icon color-success" size={22} />
            <span className="results-card-title">Pass Rate</span>
          </div>
          <div className="results-card-value">
            {loading ? '...' : `${stats?.pass_rate?.toFixed(1) ?? '0.0'}%`}
          </div>
        </div>
      </div>

      {/* Exams Directory Section */}
      <div className="glass-panel" style={{ marginTop: '2rem' }}>
        <h2 className="panel-subtitle">Exams Directory</h2>
        
        {loading ? (
          <div className="loading-state">
            <RefreshCw size={24} className="spinner" />
            <p>Loading exams listing...</p>
          </div>
        ) : exams.length === 0 ? (
          <div className="empty-state">
            <AlertCircle size={32} />
            <p>No exams available in the system.</p>
          </div>
        ) : (
          <div className="table-responsive">
            <table className="results-table">
              <thead>
                <tr>
                  <th>Exam Title</th>
                  <th>Subject</th>
                  <th>Student Count</th>
                  <th>Publication Status</th>
                  <th style={{ textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {exams.map((exam) => {
                  const examStat = examStats[exam.id];
                  const hasStatsLoaded = !!examStat;

                  return (
                    <tr key={exam.id}>
                      <td className="font-semibold">{exam.title}</td>
                      <td>{subjectMap.get(exam.subject_id) || 'General'}</td>
                      <td>
                        {hasStatsLoaded ? (
                          <span>{examStat.studentCount} students</span>
                        ) : (
                          <button 
                            className="btn-link"
                            onClick={() => loadExamStats(exam.id)}
                            disabled={!!examStats[exam.id]?.loading}
                          >
                            {examStats[exam.id]?.loading ? 'Loading...' : 'Reveal Stats'}
                          </button>
                        )}
                      </td>
                      <td>
                        {hasStatsLoaded ? (
                          examStat.isPublished ? (
                            <span className="badge-published">Published</span>
                          ) : (
                            <span className="badge-unpublished">Draft / Unpublished</span>
                          )
                        ) : (
                          <span className="text-secondary">—</span>
                        )}
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        <div className="actions-cell">
                          <button 
                            className="btn-icon" 
                            title="View Exam Results"
                            onClick={() => navigate(`/results/exams/${exam.id}`)}
                          >
                            <Eye size={16} />
                            <span>View</span>
                          </button>

                          {user?.role === 'teacher' && hasStatsLoaded && examStat.hasUnpublished && (
                            <button
                              className="btn-icon btn-action-success"
                              title="Publish Results"
                              onClick={() => handleOpenPublishModal(exam.id)}
                            >
                              <Send size={16} />
                              <span>Publish</span>
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
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
