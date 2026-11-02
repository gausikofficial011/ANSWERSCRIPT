import React, { useEffect, useState } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { client } from '../../api/client';
import { ArrowLeft, Loader } from 'lucide-react';

export const ExamCreateEdit: React.FC = () => {
  const { subjectId, id } = useParams<{ subjectId: string; id: string }>();
  const isEditMode = !!id;
  const navigate = useNavigate();

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [examDate, setExamDate] = useState('');
  const [totalMarks, setTotalMarks] = useState(20);
  const [passingMarks, setPassingMarks] = useState(10);
  const [durationMinutes, setDurationMinutes] = useState(60);
  const [status, setStatus] = useState('draft');

  // Scoring config variables
  const [semanticWeight, setSemanticWeight] = useState(0.6);
  const [keywordWeight, setKeywordWeight] = useState(0.4);
  const [plagiarismThreshold, setPlagiarismThreshold] = useState(0.85);

  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isEditMode) {
      const fetchExam = async () => {
        setFetching(true);
        setError(null);
        try {
          const response = await client.get(`/exams/${id}`);
          const data = response.data;
          setTitle(data.title);
          setDescription(data.description || '');
          setExamDate(data.exam_date);
          setTotalMarks(data.total_marks);
          setPassingMarks(data.passing_marks);
          setDurationMinutes(data.duration_minutes || 60);
          setStatus(data.status);
          
          if (data.scoring_config) {
            setSemanticWeight(data.scoring_config.semantic_weight ?? 0.6);
            setKeywordWeight(data.scoring_config.keyword_weight ?? 0.4);
            setPlagiarismThreshold(data.scoring_config.plagiarism_threshold ?? 0.85);
          }
        } catch {
          setError('Failed to load exam information.');
        } finally {
          setFetching(false);
        }
      };
      fetchExam();
    }
  }, [id, isEditMode]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (totalMarks <= 0) {
      setError('Total marks must be greater than 0.');
      return;
    }
    if (passingMarks <= 0) {
      setError('Passing marks must be greater than 0.');
      return;
    }
    if (passingMarks > totalMarks) {
      setError('Passing marks cannot exceed total marks.');
      return;
    }

    const sum = Math.round((Number(semanticWeight) + Number(keywordWeight)) * 10) / 10;
    if (Math.abs(sum - 1.0) > 0.0001) {
      setError(`Weights sum must equal 1.0. Currently got ${sum} (Semantic: ${semanticWeight} + Keyword: ${keywordWeight})`);
      return;
    }

    setLoading(true);
    setError(null);

    const payload = {
      subject_id: subjectId,
      title,
      description: description || null,
      exam_date: examDate,
      total_marks: Number(totalMarks),
      passing_marks: Number(passingMarks),
      duration_minutes: Number(durationMinutes),
      status,
      scoring_config: {
        semantic_weight: Number(semanticWeight),
        keyword_weight: Number(keywordWeight),
        plagiarism_threshold: Number(plagiarismThreshold),
      },
    };

    try {
      if (isEditMode) {
        await client.put(`/exams/${id}`, payload);
      } else {
        await client.post('/exams', payload);
      }
      navigate(`/subjects/${subjectId}`);
    } catch (err) {
      const errMsg =
        err && typeof err === 'object' && 'response' in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : null;
      setError(errMsg || 'Failed to save exam details. Please verify your inputs.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="exam-form-container">
      <div className="page-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <Link to={`/subjects/${subjectId}`} className="btn btn-secondary btn-sm" title="Back to subject">
            <ArrowLeft size={16} />
          </Link>
          <h1>{isEditMode ? 'Edit Exam' : 'Create New Exam'}</h1>
        </div>
      </div>

      {fetching ? (
        <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
          Loading exam details...
        </div>
      ) : (
        <div className="form-card">
          {error && <div className="error-banner" style={{ marginBottom: '1.5rem' }}>{error}</div>}

          <form onSubmit={handleSubmit} className="form-layout">
            <div className="input-group">
              <label htmlFor="title">Exam Title</label>
              <div className="input-wrapper">
                <input
                  id="title"
                  type="text"
                  placeholder="Midterm Examination - CS202"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  disabled={loading}
                  style={{ paddingLeft: '1rem' }}
                  required
                />
              </div>
            </div>

            <div className="input-group">
              <label htmlFor="examDate">Exam Date</label>
              <div className="input-wrapper">
                <input
                  id="examDate"
                  type="date"
                  value={examDate}
                  onChange={(e) => setExamDate(e.target.value)}
                  disabled={loading}
                  style={{ paddingLeft: '1rem' }}
                  required
                />
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem' }}>
              <div className="input-group">
                <label htmlFor="totalMarks">Total Marks</label>
                <div className="input-wrapper">
                  <input
                    id="totalMarks"
                    type="number"
                    value={totalMarks}
                    onChange={(e) => setTotalMarks(Number(e.target.value))}
                    disabled={loading}
                    style={{ paddingLeft: '1rem' }}
                    required
                  />
                </div>
              </div>

              <div className="input-group">
                <label htmlFor="passingMarks">Passing Marks</label>
                <div className="input-wrapper">
                  <input
                    id="passingMarks"
                    type="number"
                    value={passingMarks}
                    onChange={(e) => setPassingMarks(Number(e.target.value))}
                    disabled={loading}
                    style={{ paddingLeft: '1rem' }}
                    required
                  />
                </div>
              </div>

              <div className="input-group">
                <label htmlFor="durationMinutes">Duration (mins)</label>
                <div className="input-wrapper">
                  <input
                    id="durationMinutes"
                    type="number"
                    value={durationMinutes}
                    onChange={(e) => setDurationMinutes(Number(e.target.value))}
                    disabled={loading}
                    style={{ paddingLeft: '1rem' }}
                    required
                  />
                </div>
              </div>
            </div>

            <div className="input-group">
              <label htmlFor="status">Exam Status</label>
              <select
                id="status"
                className="filter-select"
                style={{ maxWidth: '100%', paddingLeft: '1rem' }}
                value={status}
                onChange={(e) => setStatus(e.target.value)}
                disabled={loading}
              >
                <option value="draft">Draft (Inactive)</option>
                <option value="active">Active (Accepts uploads)</option>
                <option value="closed">Closed (Evaluation done)</option>
              </select>
            </div>

            <div className="input-group">
              <label htmlFor="description">Optional Description</label>
              <textarea
                id="description"
                className="form-textarea"
                placeholder="Details about syllabus coverage, modules, stacks etc."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                disabled={loading}
              />
            </div>

            <div style={{ padding: '1rem', border: '1px solid var(--border-color)', borderRadius: '8px', marginTop: '0.5rem' }}>
              <h4 style={{ fontSize: '0.9rem', color: 'var(--text-accent)', marginBottom: '0.75rem' }}>AI Scoring Scorer Configuration</h4>
              
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '0.75rem' }}>
                <div className="input-group">
                  <label htmlFor="semanticWeight">Semantic Similarity Weight (0.0 - 1.0)</label>
                  <div className="input-wrapper">
                    <input
                      id="semanticWeight"
                      type="number"
                      step="0.1"
                      min="0.0"
                      max="1.0"
                      value={semanticWeight}
                      onChange={(e) => setSemanticWeight(Number(e.target.value))}
                      disabled={loading}
                      style={{ paddingLeft: '1rem' }}
                      required
                    />
                  </div>
                </div>

                <div className="input-group">
                  <label htmlFor="keywordWeight">Keyword Matching Weight (0.0 - 1.0)</label>
                  <div className="input-wrapper">
                    <input
                      id="keywordWeight"
                      type="number"
                      step="0.1"
                      min="0.0"
                      max="1.0"
                      value={keywordWeight}
                      onChange={(e) => setKeywordWeight(Number(e.target.value))}
                      disabled={loading}
                      style={{ paddingLeft: '1rem' }}
                      required
                    />
                  </div>
                </div>
              </div>

              <div className="input-group">
                <label htmlFor="plagiarismThreshold">Plagiarism Index Flagging Threshold (0.0 - 1.0)</label>
                <div className="input-wrapper">
                  <input
                    id="plagiarismThreshold"
                    type="number"
                    step="0.05"
                    min="0.1"
                    max="1.0"
                    value={plagiarismThreshold}
                    onChange={(e) => setPlagiarismThreshold(Number(e.target.value))}
                    disabled={loading}
                    style={{ paddingLeft: '1rem' }}
                    required
                  />
                </div>
              </div>
            </div>

            <div className="form-actions">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => navigate(`/subjects/${subjectId}`)}
                disabled={loading}
              >
                Cancel
              </button>
              <button type="submit" className="btn btn-primary" disabled={loading}>
                {loading ? (
                  <>
                    <Loader size={18} className="spinner" />
                    <span>Saving...</span>
                  </>
                ) : (
                  <span>Save Exam</span>
                )}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};
