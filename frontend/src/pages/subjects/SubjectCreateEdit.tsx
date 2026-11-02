import React, { useEffect, useState } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { client } from '../../api/client';
import { ArrowLeft, Loader } from 'lucide-react';

export const SubjectCreateEdit: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const isEditMode = !!id;
  const navigate = useNavigate();

  const [name, setName] = useState('');
  const [code, setCode] = useState('');
  const [description, setDescription] = useState('');
  const [language, setLanguage] = useState('en');
  const [isActive, setIsActive] = useState(true);

  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isEditMode) {
      const fetchSubject = async () => {
        setFetching(true);
        setError(null);
        try {
          const response = await client.get(`/subjects/${id}`);
          const data = response.data;
          setName(data.name);
          setCode(data.code);
          setDescription(data.description || '');
          setLanguage(data.language);
          setIsActive(data.is_active);
        } catch {
          setError('Failed to load subject details. Please try again.');
        } finally {
          setFetching(false);
        }
      };
      fetchSubject();
    }
  }, [id, isEditMode]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (name.length < 2) {
      setError('Subject Name must be at least 2 characters.');
      return;
    }
    if (code.length < 2) {
      setError('Subject Code must be at least 2 characters.');
      return;
    }

    setLoading(true);
    setError(null);

    const payload = {
      name,
      code,
      description: description || null,
      language,
      is_active: isEditMode ? isActive : undefined,
    };

    try {
      if (isEditMode) {
        await client.put(`/subjects/${id}`, payload);
      } else {
        await client.post('/subjects', payload);
      }
      navigate('/subjects');
    } catch (err) {
      const errMsg =
        err && typeof err === 'object' && 'response' in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : null;
      setError(errMsg || 'Failed to save subject data. Verify details and try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="subject-form-container">
      <div className="page-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <Link to="/subjects" className="btn btn-secondary btn-sm" title="Back to list">
            <ArrowLeft size={16} />
          </Link>
          <h1>{isEditMode ? 'Edit Subject' : 'Create New Subject'}</h1>
        </div>
      </div>

      {fetching ? (
        <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
          Loading subject details...
        </div>
      ) : (
        <div className="form-card">
          {error && <div className="error-banner" style={{ marginBottom: '1.5rem' }}>{error}</div>}

          <form onSubmit={handleSubmit} className="form-layout">
            <div className="input-group">
              <label htmlFor="code">Subject Code (e.g. CS202)</label>
              <div className="input-wrapper">
                <input
                  id="code"
                  type="text"
                  placeholder="CS202"
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  disabled={loading}
                  style={{ paddingLeft: '1rem' }}
                  required
                />
              </div>
            </div>

            <div className="input-group">
              <label htmlFor="name">Subject Name</label>
              <div className="input-wrapper">
                <input
                  id="name"
                  type="text"
                  placeholder="Data Structures and Algorithms"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  disabled={loading}
                  style={{ paddingLeft: '1rem' }}
                  required
                />
              </div>
            </div>

            <div className="input-group">
              <label htmlFor="language">Teaching Language</label>
              <select
                id="language"
                className="filter-select"
                style={{ maxWidth: '100%', paddingLeft: '1rem' }}
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                disabled={loading}
              >
                <option value="en">English (en)</option>
                <option value="es">Spanish (es)</option>
                <option value="fr">French (fr)</option>
                <option value="de">German (de)</option>
              </select>
            </div>

            <div className="input-group">
              <label htmlFor="description">Optional Description</label>
              <textarea
                id="description"
                className="form-textarea"
                placeholder="Detailed information regarding syllabi, reference books, etc."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                disabled={loading}
              />
            </div>

            {isEditMode && (
              <div className="input-group">
                <label className="checkbox-group">
                  <input
                    type="checkbox"
                    checked={isActive}
                    onChange={(e) => setIsActive(e.target.checked)}
                    disabled={loading}
                  />
                  <span>Active Subject Status</span>
                </label>
              </div>
            )}

            <div className="form-actions">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => navigate('/subjects')}
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
                  <span>Save Subject</span>
                )}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};
