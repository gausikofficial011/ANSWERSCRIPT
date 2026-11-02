import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { client } from '../../api/client';
import { 
  FileText, 
  Scan, 
  Award, 
  CheckCircle, 
  Eye, 
  AlertTriangle, 
  TrendingUp, 
  Clock,
  Play,
  ArrowRight,
  RefreshCw,
  Cpu,
  GraduationCap
} from 'lucide-react';

interface DashboardOverview {
  total_answer_sheets: number;
  pending_ocr: number;
  pending_evaluation: number;
  completed_evaluations: number;
  teacher_review_pending: number;
  plagiarism_alerts: number;
  average_score: number;
  average_processing_time: number;
}

export const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [stats, setStats] = useState<DashboardOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchOverview = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await client.get<DashboardOverview>('/results/overview');
      setStats(response.data);
    } catch (err: any) {
      console.error(err);
      setError('Failed to fetch dashboard metrics. Please verify that the backend API server is running.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOverview();
  }, []);

  const handleStartEvaluation = () => {
    // Direct teacher to Subjects to select/create a Subject & Exam and upload answer sheets
    navigate('/subjects');
  };

  return (
    <div className="dashboard-overview-container">
      <div className="welcome-banner">
        <div className="welcome-banner-header">
          <div>
            <h1>Welcome back, {user?.full_name || user?.username || 'Teacher'}!</h1>
            <p className="subtitle">IntelliGrade Enterprise Academic Intelligence & Multi-Portal Hub</p>
          </div>
          <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
            <button 
              className="btn btn-secondary" 
              onClick={() => navigate('/portals/teacher')}
              style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
            >
              <Cpu size={18} />
              <span>Enter Multi-Portal Hub</span>
            </button>
            <button 
              className="btn btn-primary btn-start-evaluation" 
              onClick={handleStartEvaluation}
            >
              <Play size={18} fill="currentColor" />
              <span>Start Evaluation</span>
            </button>
          </div>
        </div>

        {/* 10 Role Portals Quick Selector Grid */}
        <div style={{ marginTop: '1.25rem', paddingTop: '1.25rem', borderTop: '1px solid rgba(226, 232, 240, 0.1)', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '0.75rem' }}>
          {[
            { name: 'Super Admin', route: '/portals/super-admin', badge: 'admin', label: 'Portal 1' },
            { name: 'Academic Admin', route: '/portals/academic-admin', badge: 'admin', label: 'Portal 2' },
            { name: 'Teacher Creator', route: '/portals/teacher', badge: 'teacher', label: 'Portal 3' },
            { name: 'OCR Studio', route: '/portals/ocr-review', badge: 'ocr', label: 'Portal 4' },
            { name: 'AI Evaluation', route: '/portals/ai-evaluation', badge: 'eval', label: 'Portal 5' },
            { name: 'Evaluator Review', route: '/portals/evaluator', badge: 'eval', label: 'Portal 6' },
            { name: 'Integrity Studio', route: '/portals/integrity', badge: 'integrity', label: 'Portal 7' },
            { name: 'Student Results', route: '/portals/student', badge: 'eval', label: 'Portal 8' },
            { name: 'Academic QA', route: '/portals/analytics', badge: 'analytics', label: 'Portal 9' },
            { name: 'MLOps Lab', route: '/portals/research-lab', badge: 'research', label: 'Portal 10' },
          ].map((p, idx) => (
            <Link
              key={idx}
              to={p.route}
              style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '0.2rem',
                padding: '0.6rem 0.75rem',
                background: 'rgba(11, 20, 36, 0.6)',
                border: '1px solid rgba(226, 232, 240, 0.1)',
                borderRadius: '8px',
                textDecoration: 'none',
                transition: 'all 0.15s ease'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.68rem', fontWeight: 700, color: '#818CF8' }}>{p.label}</span>
                <ArrowRight size={12} color="#94A3B8" />
              </div>
              <span style={{ fontSize: '0.82rem', fontWeight: 700, color: '#F8FAFC' }}>{p.name}</span>
            </Link>
          ))}
        </div>
      </div>

      {error && (
        <div className="error-banner">
          <AlertTriangle className="error-icon" size={18} />
          <span>{error}</span>
        </div>
      )}

      {/* Overview Statistics Grid */}
      <div className="results-kpi-grid">
        <div className="results-card">
          <div className="results-card-header">
            <FileText className="results-card-icon text-accent" size={22} />
            <span className="results-card-title">Total Answer Sheets</span>
          </div>
          <div className="results-card-value">
            {loading ? '...' : stats?.total_answer_sheets ?? 0}
          </div>
        </div>

        <div className="results-card">
          <div className="results-card-header">
            <Scan className="results-card-icon text-accent animate-pulse" size={22} />
            <span className="results-card-title">Pending OCR</span>
          </div>
          <div className="results-card-value">
            {loading ? '...' : stats?.pending_ocr ?? 0}
          </div>
        </div>

        <div className="results-card">
          <div className="results-card-header">
            <Cpu className="results-card-icon text-accent" size={22} />
            <span className="results-card-title">Pending AI Evaluation</span>
          </div>
          <div className="results-card-value">
            {loading ? '...' : stats?.pending_evaluation ?? 0}
          </div>
        </div>

        <div className="results-card">
          <div className="results-card-header">
            <CheckCircle className="results-card-icon color-success" size={22} />
            <span className="results-card-title">Completed Evaluations</span>
          </div>
          <div className="results-card-value">
            {loading ? '...' : stats?.completed_evaluations ?? 0}
          </div>
        </div>

        <div className="results-card">
          <div className="results-card-header">
            <Eye className="results-card-icon text-accent" size={22} />
            <span className="results-card-title">Teacher Review Pending</span>
          </div>
          <div className="results-card-value">
            {loading ? '...' : stats?.teacher_review_pending ?? 0}
          </div>
        </div>

        <div className="results-card">
          <div className="results-card-header">
            <AlertTriangle className={`results-card-icon ${(stats?.plagiarism_alerts ?? 0) > 0 ? 'color-error' : 'text-secondary'}`} size={22} />
            <span className="results-card-title">Plagiarism Alerts</span>
          </div>
          <div className="results-card-value">
            {loading ? '...' : stats?.plagiarism_alerts ?? 0}
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
            <Clock className="results-card-icon text-accent" size={22} />
            <span className="results-card-title">Avg. Processing Time</span>
          </div>
          <div className="results-card-value">
            {loading ? '...' : `${stats?.average_processing_time?.toFixed(1) ?? '0.0'}s`}
          </div>
        </div>
      </div>

      {/* Interactive Demonstration Wizard Stepper */}
      <div className="wizard-panel">
        <h2 className="wizard-title">
          <GraduationCap className="text-accent" size={24} />
          <span>E2E AI Evaluation Demonstration Pipeline Control Center</span>
        </h2>
        <p className="subtitle wizard-subtitle">
          Follow this structured step-by-step workflow during the MCA final demonstration panel to show the full E2E evaluation capability.
        </p>

        <div className="wizard-steps">
          {/* Step 1 */}
          <div className="wizard-step-card">
            <div className="wizard-step-header">
              <div className="wizard-step-number">1</div>
              <FileText className="wizard-step-icon" size={20} />
            </div>
            <div className="wizard-step-title">Upload Answer Key / Define Exam</div>
            <div className="wizard-step-desc">
              Define the subject, exam parameters, questions, model answers, and criteria-based scoring rubrics.
            </div>
            <Link to="/subjects" className="wizard-step-action">
              <span>Syllabus & Exam Config</span>
              <ArrowRight size={14} />
            </Link>
          </div>

          {/* Step 2 */}
          <div className="wizard-step-card">
            <div className="wizard-step-header">
              <div className="wizard-step-number">2</div>
              <Scan className="wizard-step-icon" size={20} />
            </div>
            <div className="wizard-step-title">Upload Student Answer Sheets</div>
            <div className="wizard-step-desc">
              Upload handwritten student answer sheet PDFs. The system automatically segments pages and enqueues tasks.
            </div>
            <Link to="/subjects" className="wizard-step-action">
              <span>Upload Sheets</span>
              <ArrowRight size={14} />
            </Link>
          </div>

          {/* Step 3 */}
          <div className="wizard-step-card">
            <div className="wizard-step-header">
              <div className="wizard-step-number">3</div>
              <Cpu className="wizard-step-icon" size={20} />
            </div>
            <div className="wizard-step-title">Monitor AI Processing</div>
            <div className="wizard-step-desc">
              Track background execution status (OCR conversion, question-answer mappings, and criteria evaluation).
            </div>
            <Link to="/subjects" className="wizard-step-action">
              <span>OCR & Mapping Status</span>
              <ArrowRight size={14} />
            </Link>
          </div>

          {/* Step 4 */}
          <div className="wizard-step-card">
            <div className="wizard-step-header">
              <div className="wizard-step-number">4</div>
              <Award className="wizard-step-icon" size={20} />
            </div>
            <div className="wizard-step-title">Review & Grade Results</div>
            <div className="wizard-step-desc">
              Examine detailed grading dashboards, semantic matching, keyword statistics, rubrics, and plagiarism reviews.
            </div>
            <div className="wizard-step-links">
              <Link to="/results" className="wizard-step-action">
                <span>View Results</span>
                <ArrowRight size={14} />
              </Link>
              <Link to="/plagiarism" className="wizard-step-action">
                <span>Plagiarism</span>
                <ArrowRight size={14} />
              </Link>
            </div>
          </div>
        </div>

        <div className="demo-banner-wrapper">
          <div className="demo-banner">
            <RefreshCw className="demo-banner-icon animate-spin" size={20} />
            <div>
              <strong>Demonstration State Notice</strong>: Celery tasks are executing in <code>CELERY_TASK_ALWAYS_EAGER</code> mode. 
              The backend automatically processes OCR and AI grading synchronously during sheet uploads for immediate dashboard updates.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
