/* eslint-disable react-hooks/exhaustive-deps, react-hooks/set-state-in-effect */
import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { client } from '../../api/client';
import { ArrowLeft, Plus, Edit2, Trash2, Calendar, FileText, ArrowRight } from 'lucide-react';

interface Subject {
  id: string;
  name: string;
  code: string;
  description: string | null;
  language: string;
  is_active: boolean;
}

interface Exam {
  id: string;
  title: string;
  description: string | null;
  exam_date: string;
  total_marks: number;
  passing_marks: number;
  duration_minutes: number | null;
  status: string;
}

export const SubjectDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [subject, setSubject] = useState<Subject | null>(null);
  const [exams, setExams] = useState<Exam[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingExams, setLoadingExams] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [examPage, setExamPage] = useState(1);
  const [examTotalPages, setExamTotalPages] = useState(1);

  const fetchSubjectDetails = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await client.get(`/subjects/${id}`);
      setSubject(response.data);
    } catch {
      setError('Failed to load subject information.');
    } finally {
      setLoading(false);
    }
  };

  const fetchExams = async () => {
    setLoadingExams(true);
    try {
      const response = await client.get('/exams', {
        params: {
          subject_id: id,
          page: examPage,
          page_size: 10,
        },
      });
      setExams(response.data.items);
      setExamTotalPages(response.data.pages || 1);
    } catch (error) {
      console.error('Failed to fetch exams:', error);
    } finally {
      setLoadingExams(false);
    }
  };

  useEffect(() => {
    fetchSubjectDetails();
  }, [id]);

  useEffect(() => {
    fetchExams();
  }, [id, examPage]);

  const handleExamDelete = async (examId: string, title: string) => {
    if (!window.confirm(`Are you sure you want to delete the exam "${title}"?`)) {
      return;
    }

    try {
      await client.delete(`/exams/${examId}`);
      fetchExams();
    } catch {
      alert('Failed to delete exam. Please try again.');
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
        Loading subject specifications...
      </div>
    );
  }

  if (error || !subject) {
    return (
      <div style={{ padding: '2rem' }}>
        <div className="error-banner">{error || 'Subject not found'}</div>
        <Link to="/subjects" className="btn btn-secondary mt-2">
          <ArrowLeft size={16} />
          <span>Back to Subjects</span>
        </Link>
      </div>
    );
  }

  return (
    <div className="subject-details-container">
      <div className="page-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <Link to="/subjects" className="btn btn-secondary btn-sm" title="Back to subjects">
            <ArrowLeft size={16} />
          </Link>
          <h1>{subject.code}: {subject.name}</h1>
        </div>
        <Link to={`/subjects/${id}/exams/new`} className="btn btn-primary">
          <Plus size={18} />
          <span>Add Exam</span>
        </Link>
      </div>

      <div className="detail-grid">
        <div className="detail-card">
          <h3 className="detail-section-title">Overview Specifications</h3>
          <div className="metadata-list" style={{ marginBottom: '1.5rem' }}>
            <div className="metadata-row">
              <span className="metadata-label">Course Code:</span>
              <span className="metadata-value">{subject.code}</span>
            </div>
            <div className="metadata-row">
              <span className="metadata-label">Language:</span>
              <span className="metadata-value">{subject.language.toUpperCase()}</span>
            </div>
            <div className="metadata-row">
              <span className="metadata-label">Status:</span>
              <span className={subject.is_active ? 'profile-value badge' : 'profile-value badge btn-logout'}>
                {subject.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>
          </div>
          <h4 style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>Description</h4>
          <p style={{ fontSize: '0.95rem', lineHeight: '145%', color: 'var(--text-primary)' }}>
            {subject.description || 'No description provided.'}
          </p>
        </div>

        <div className="detail-card">
          <h3 className="detail-section-title">Syllabus Overview</h3>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', color: 'var(--text-secondary)' }}>
            <FileText size={40} style={{ opacity: 0.5 }} />
            <div>
              <p style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>CS202 Data Structures</p>
              <p style={{ fontSize: '0.8rem' }}>1 Exam active, stack and queue structures</p>
            </div>
          </div>
        </div>
      </div>

      <div style={{ marginTop: '2.5rem' }}>
        <h2 style={{ fontSize: '1.4rem', fontWeight: 600, marginBottom: '1rem' }}>Subject Examinations</h2>

        <div className="table-container">
          {loadingExams ? (
            <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
              Loading exams list...
            </div>
          ) : exams.length === 0 ? (
            <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
              No exams created for this subject yet. Click "Add Exam" to create one.
            </div>
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Date</th>
                  <th>Total Marks</th>
                  <th>Passing Marks</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {exams.map((exam) => (
                  <tr key={exam.id}>
                    <td style={{ fontWeight: 600, color: 'var(--text-accent)' }}>
                      <Link to={`/exams/${exam.id}`}>{exam.title}</Link>
                    </td>
                    <td>
                      <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.85rem' }}>
                        <Calendar size={14} style={{ color: 'var(--text-secondary)' }} />
                        {exam.exam_date}
                      </span>
                    </td>
                    <td>{exam.total_marks}</td>
                    <td>{exam.passing_marks}</td>
                    <td>
                      <span className={`profile-value badge ${exam.status === 'active' ? '' : exam.status === 'draft' ? 'badge-info' : 'btn-logout'}`}>
                        {exam.status.toUpperCase()}
                      </span>
                    </td>
                    <td>
                      <div className="actions-cell">
                        <Link to={`/exams/${exam.id}`} className="btn btn-secondary btn-sm" title="View exam details">
                          <ArrowRight size={14} />
                        </Link>
                        <Link to={`/subjects/${id}/exams/${exam.id}/edit`} className="btn btn-secondary btn-sm" title="Edit exam">
                          <Edit2 size={14} />
                        </Link>
                        <button
                          onClick={() => handleExamDelete(exam.id, exam.title)}
                          className="btn btn-danger btn-sm"
                          title="Delete exam"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          <div className="pagination-container">
            <span>
              Page {examPage} of {examTotalPages}
            </span>
            <div className="pagination-controls">
              <button
                className="btn btn-secondary btn-sm"
                disabled={examPage <= 1 || loadingExams}
                onClick={() => setExamPage((prev) => prev - 1)}
              >
                Previous
              </button>
              <button
                className="btn btn-secondary btn-sm"
                disabled={examPage >= examTotalPages || loadingExams}
                onClick={() => setExamPage((prev) => prev + 1)}
              >
                Next
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
