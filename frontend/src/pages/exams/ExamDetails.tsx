/* eslint-disable react-hooks/exhaustive-deps, react-hooks/set-state-in-effect */
import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { client } from '../../api/client';
import { ArrowLeft, Calendar, ShieldAlert, Clock, Plus, Edit2, Trash2, Key, Award } from 'lucide-react';
import { AnswerSheetsTab } from './AnswerSheetsTab';

interface Exam {
  id: string;
  subject_id: string;
  title: string;
  description: string | null;
  exam_date: string;
  total_marks: number;
  passing_marks: number;
  duration_minutes: number | null;
  status: string;
  scoring_config: {
    semantic_weight?: number;
    keyword_weight?: number;
    plagiarism_threshold?: number;
  };
}

interface Question {
  id: string;
  exam_id: string;
  question_number: number;
  question_text: string;
  marks: number;
  question_type: string;
  language: string;
}

export const ExamDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [exam, setExam] = useState<Exam | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'questions' | 'sheets' | 'plagiarism'>('overview');

  // Questions listing state
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loadingQuestions, setLoadingQuestions] = useState(false);
  const [questionsPage, setQuestionsPage] = useState(1);
  const [questionsTotalPages, setQuestionsTotalPages] = useState(1);

  const fetchExamDetails = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await client.get(`/exams/${id}`);
      setExam(response.data);
    } catch {
      setError('Failed to load exam details.');
    } finally {
      setLoading(false);
    }
  };

  const fetchQuestions = async () => {
    setLoadingQuestions(true);
    try {
      const response = await client.get('/questions', {
        params: {
          exam_id: id,
          page: questionsPage,
          page_size: 10,
        },
      });
      setQuestions(response.data.items || []);
      setQuestionsTotalPages(response.data.pages || 1);
    } catch (err) {
      console.error('Failed to fetch questions:', err);
    } finally {
      setLoadingQuestions(false);
    }
  };

  useEffect(() => {
    fetchExamDetails();
  }, [id]);

  useEffect(() => {
    if (activeTab === 'questions') {
      fetchQuestions();
    }
  }, [id, activeTab, questionsPage]);

  const handleQuestionDelete = async (questionId: string, number: number) => {
    if (!window.confirm(`Are you sure you want to delete Question ${number}?`)) {
      return;
    }

    try {
      await client.delete(`/questions/${questionId}`);
      fetchQuestions();
    } catch {
      alert('Failed to delete question. Please try again.');
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
        Loading exam specifications...
      </div>
    );
  }

  if (error || !exam) {
    return (
      <div style={{ padding: '2rem' }}>
        <div className="error-banner">{error || 'Exam details not found'}</div>
        <Link to="/subjects" className="btn btn-secondary mt-2">
          <ArrowLeft size={16} />
          <span>Back to Subjects</span>
        </Link>
      </div>
    );
  }

  return (
    <div className="exam-details-container">
      <div className="page-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <Link to={`/subjects/${exam.subject_id}`} className="btn btn-secondary btn-sm" title="Back to subject details">
            <ArrowLeft size={16} />
          </Link>
          <h1>Exam Spec: {exam.title}</h1>
        </div>
        <span className={`profile-value badge ${exam.status === 'active' ? '' : exam.status === 'draft' ? 'badge-info' : 'btn-logout'}`}>
          {exam.status.toUpperCase()}
        </span>
      </div>

      <div className="tabs-container">
        <div className="tabs-list">
          <button
            className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            Overview Specifications
          </button>
          <button
            className={`tab-btn ${activeTab === 'questions' ? 'active' : ''}`}
            onClick={() => setActiveTab('questions')}
          >
            Questions & Rubrics
          </button>
          <button
            className={`tab-btn ${activeTab === 'sheets' ? 'active' : ''}`}
            onClick={() => setActiveTab('sheets')}
          >
            Answer Sheets (OCR)
          </button>
          <button
            className={`tab-btn ${activeTab === 'plagiarism' ? 'active' : ''}`}
            onClick={() => setActiveTab('plagiarism')}
          >
            Plagiarism Audit
          </button>
        </div>

        <div className="tab-content" style={{ marginTop: '1.5rem' }}>
          {activeTab === 'overview' && (
            <div className="detail-grid">
              <div className="detail-card">
                <h3 className="detail-section-title">General Parameters</h3>
                
                <div className="metadata-list" style={{ marginBottom: '1.5rem' }}>
                  <div className="metadata-row">
                    <span className="metadata-label">Scheduled Date:</span>
                    <span className="metadata-value" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem' }}>
                      <Calendar size={14} style={{ color: 'var(--text-secondary)' }} />
                      {exam.exam_date}
                    </span>
                  </div>
                  <div className="metadata-row">
                    <span className="metadata-label">Duration Allowance:</span>
                    <span className="metadata-value" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem' }}>
                      <Clock size={14} style={{ color: 'var(--text-secondary)' }} />
                      {exam.duration_minutes ? `${exam.duration_minutes} Minutes` : 'Unlimited'}
                    </span>
                  </div>
                  <div className="metadata-row">
                    <span className="metadata-label">Total Weight Marks:</span>
                    <span className="metadata-value" style={{ color: 'var(--text-accent)' }}>{exam.total_marks} Marks</span>
                  </div>
                  <div className="metadata-row">
                    <span className="metadata-label">Passing Minimum Marks:</span>
                    <span className="metadata-value">{exam.passing_marks} Marks</span>
                  </div>
                </div>

                <h4 style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>Overview</h4>
                <p style={{ fontSize: '0.95rem', lineHeight: '145%', color: 'var(--text-primary)' }}>
                  {exam.description || 'No detailed instructions or overview provided.'}
                </p>
              </div>

              <div className="detail-card">
                <h3 className="detail-section-title">AI Scorer Config Weights</h3>
                <div className="metadata-list">
                  <div className="metadata-row">
                    <span className="metadata-label">Semantic Similarity Weight:</span>
                    <span className="metadata-value" style={{ color: 'var(--color-success)' }}>
                      {(exam.scoring_config?.semantic_weight ?? 0.6) * 100}%
                    </span>
                  </div>
                  <div className="metadata-row">
                    <span className="metadata-label">Keyword Match Weight:</span>
                    <span className="metadata-value">
                      {(exam.scoring_config?.keyword_weight ?? 0.4) * 100}%
                    </span>
                  </div>
                  <div className="metadata-row" style={{ borderTop: '1px solid var(--border-color)', paddingTop: '0.5rem', marginTop: '0.5rem' }}>
                    <span className="metadata-label">Plagiarism Overlap Index:</span>
                    <span className="metadata-value" style={{ color: 'var(--color-error)' }}>
                      {(exam.scoring_config?.plagiarism_threshold ?? 0.85) * 100}%
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'questions' && (
            <div className="questions-tab-content">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <h2 style={{ fontSize: '1.3rem', fontWeight: 600 }}>Exam Questions Specification</h2>
                <Link to={`/exams/${exam.id}/questions/new`} className="btn btn-primary">
                  <Plus size={18} />
                  <span>Add Question</span>
                </Link>
              </div>

              <div className="table-container">
                {loadingQuestions ? (
                  <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
                    Loading questions list...
                  </div>
                ) : questions.length === 0 ? (
                  <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
                    No questions created for this exam yet. Click "Add Question" to begin.
                  </div>
                ) : (
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th style={{ width: '80px' }}>Q#</th>
                        <th>Question Text</th>
                        <th style={{ width: '100px' }}>Marks</th>
                        <th style={{ width: '120px' }}>Type</th>
                        <th style={{ width: '100px' }}>Language</th>
                        <th style={{ width: '380px' }}>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {questions.map((q) => (
                        <tr key={q.id}>
                          <td style={{ fontWeight: 600, color: 'var(--text-accent)' }}>Q{q.question_number}</td>
                          <td style={{ maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={q.question_text}>
                            {q.question_text}
                          </td>
                          <td>{q.marks}</td>
                          <td style={{ textTransform: 'capitalize' }}>{q.question_type}</td>
                          <td>{q.language.toUpperCase()}</td>
                          <td>
                            <div className="actions-cell">
                              <Link to={`/exams/${exam.id}/questions/${q.id}/edit`} className="btn btn-secondary btn-sm" title="Edit Question">
                                <Edit2 size={13} />
                                <span>Edit</span>
                              </Link>
                              <Link to={`/exams/${exam.id}/questions/${q.id}/model-answer`} className="btn btn-secondary btn-sm" title="Manage Model Answer">
                                <Key size={13} style={{ color: 'var(--color-success)' }} />
                                <span>Model Answer</span>
                              </Link>
                              <Link to={`/exams/${exam.id}/questions/${q.id}/rubric`} className="btn btn-secondary btn-sm" title="Manage Rubric">
                                <Award size={13} style={{ color: 'var(--text-accent)' }} />
                                <span>Rubric</span>
                              </Link>
                              <button
                                onClick={() => handleQuestionDelete(q.id, q.question_number)}
                                className="btn btn-danger btn-sm"
                                title="Delete Question"
                              >
                                <Trash2 size={13} />
                                <span>Delete</span>
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}

                {questions.length > 0 && (
                  <div className="pagination-container">
                    <span>
                      Page {questionsPage} of {questionsTotalPages}
                    </span>
                    <div className="pagination-controls">
                      <button
                        className="btn btn-secondary btn-sm"
                        disabled={questionsPage <= 1 || loadingQuestions}
                        onClick={() => setQuestionsPage((prev) => prev - 1)}
                      >
                        Previous
                      </button>
                      <button
                        className="btn btn-secondary btn-sm"
                        disabled={questionsPage >= questionsTotalPages || loadingQuestions}
                        onClick={() => setQuestionsPage((prev) => prev + 1)}
                      >
                        Next
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'sheets' && id && (
            <AnswerSheetsTab examId={id} />
          )}

          {activeTab === 'plagiarism' && (
            <div className="tab-panel-enabled" style={{ textAlign: 'center', padding: '3rem 2rem', background: 'rgba(255,255,255,0.01)', border: '1px solid var(--border-color)', borderRadius: '12px' }}>
              <ShieldAlert size={48} className="logo-icon" style={{ color: 'var(--text-accent)', marginBottom: '1rem', marginInline: 'auto' }} />
              <h3 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '0.5rem' }}>Plagiarism Audit Dashboard</h3>
              <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem', maxWidth: '500px', marginInline: 'auto', fontSize: '0.9rem', lineHeight: '145%' }}>
                Lexical, overlap, and semantic response similarities are checked automatically across student submissions. View the full list of flagged pairs and review incident reports on the plagiarism summary dashboard.
              </p>
              <Link to={`/plagiarism/exams/${id}`} className="btn btn-primary" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', marginInline: 'auto' }}>
                <ShieldAlert size={16} />
                <span>Open Plagiarism Dashboard</span>
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
