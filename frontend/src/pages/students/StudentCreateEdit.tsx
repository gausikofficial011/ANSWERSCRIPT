import React, { useEffect, useState } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { client } from '../../api/client';
import { ArrowLeft, Loader } from 'lucide-react';

export const StudentCreateEdit: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const isEditMode = !!id;
  const navigate = useNavigate();

  const [studentNumber, setStudentNumber] = useState('');
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [classSection, setClassSection] = useState('CS-A');

  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isEditMode) {
      const fetchStudent = async () => {
        setFetching(true);
        setError(null);
        try {
          const response = await client.get(`/students/${id}`);
          const data = response.data;
          setStudentNumber(data.student_number);
          setFullName(data.full_name);
          setEmail(data.email || '');
          setClassSection(data.class_section || 'CS-A');
        } catch {
          setError('Failed to load student record details.');
        } finally {
          setFetching(false);
        }
      };
      fetchStudent();
    }
  }, [id, isEditMode]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (fullName.length < 2) {
      setError('Full Name must be at least 2 characters.');
      return;
    }
    if (studentNumber.length < 2) {
      setError('Student Number must be at least 2 characters.');
      return;
    }

    setLoading(true);
    setError(null);

    const payload = {
      student_number: studentNumber,
      full_name: fullName,
      email: email || null,
      class_section: classSection,
    };

    try {
      if (isEditMode) {
        await client.put(`/students/${id}`, payload);
      } else {
        await client.post('/students', payload);
      }
      navigate('/students');
    } catch (err) {
      const errMsg =
        err && typeof err === 'object' && 'response' in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : null;
      setError(errMsg || 'Failed to save student record. Verify details and try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="student-form-container">
      <div className="page-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <Link to="/students" className="btn btn-secondary btn-sm" title="Back to list">
            <ArrowLeft size={16} />
          </Link>
          <h1>{isEditMode ? 'Edit Student Details' : 'Register New Student'}</h1>
        </div>
      </div>

      {fetching ? (
        <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
          Loading student details...
        </div>
      ) : (
        <div className="form-card">
          {error && <div className="error-banner" style={{ marginBottom: '1.5rem' }}>{error}</div>}

          <form onSubmit={handleSubmit} className="form-layout">
            <div className="input-group">
              <label htmlFor="studentNumber">Student Registration Number (e.g. STU-001)</label>
              <div className="input-wrapper">
                <input
                  id="studentNumber"
                  type="text"
                  placeholder="STU-001"
                  value={studentNumber}
                  onChange={(e) => setStudentNumber(e.target.value)}
                  disabled={loading}
                  style={{ paddingLeft: '1rem' }}
                  required
                />
              </div>
            </div>

            <div className="input-group">
              <label htmlFor="fullName">Full Name</label>
              <div className="input-wrapper">
                <input
                  id="fullName"
                  type="text"
                  placeholder="Bob Miller"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  disabled={loading}
                  style={{ paddingLeft: '1rem' }}
                  required
                />
              </div>
            </div>

            <div className="input-group">
              <label htmlFor="email">Optional Email Address</label>
              <div className="input-wrapper">
                <input
                  id="email"
                  type="email"
                  placeholder="bob@student.amaes.edu"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={loading}
                  style={{ paddingLeft: '1rem' }}
                />
              </div>
            </div>

            <div className="input-group">
              <label htmlFor="classSection">Class Section Batch</label>
              <select
                id="classSection"
                className="filter-select"
                style={{ maxWidth: '100%', paddingLeft: '1rem' }}
                value={classSection}
                onChange={(e) => setClassSection(e.target.value)}
                disabled={loading}
              >
                <option value="CS-A">CS-A</option>
                <option value="CS-B">CS-B</option>
                <option value="CS-C">CS-C</option>
              </select>
            </div>

            <div className="form-actions">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => navigate('/students')}
                disabled={loading}
              >
                Cancel
              </button>
              <button type="submit" className="btn btn-primary" disabled={loading}>
                {loading ? (
                  <>
                    <Loader size={18} className="spinner" />
                    <span>Registering...</span>
                  </>
                ) : (
                  <span>Save Record</span>
                )}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};
