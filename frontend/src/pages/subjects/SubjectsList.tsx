/* eslint-disable react-hooks/exhaustive-deps */
import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { client } from '../../api/client';
import { Plus, Search, Edit2, Trash2, ArrowRight } from 'lucide-react';

interface Subject {
  id: string;
  name: string;
  code: string;
  description: string | null;
  language: string;
  is_active: boolean;
}

export const SubjectsList: React.FC = () => {
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [isActive, setIsActive] = useState<string>('all');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [error, setError] = useState<string | null>(null);

  const fetchSubjects = async () => {
    setLoading(true);
    setError(null);
    try {
      const activeParam = isActive === 'active' ? true : isActive === 'inactive' ? false : undefined;
      const response = await client.get('/subjects', {
        params: {
          search: search || undefined,
          is_active: activeParam,
          page,
          page_size: 10,
        },
      });
      setSubjects(response.data.items);
      setTotalPages(response.data.pages || 1);
    } catch {
      setError('Failed to fetch subjects list. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const delayDebounce = setTimeout(() => {
      fetchSubjects();
    }, 300);

    return () => clearTimeout(delayDebounce);
  }, [search, isActive, page]);

  const handleDelete = async (id: string, name: string) => {
    if (!window.confirm(`Are you sure you want to delete the subject "${name}"?`)) {
      return;
    }

    try {
      await client.delete(`/subjects/${id}`);
      fetchSubjects();
    } catch {
      alert('Failed to delete subject. Please try again.');
    }
  };

  return (
    <div className="subjects-container">
      <div className="page-header">
        <h1>Subjects Directory</h1>
        <Link to="/subjects/new" className="btn btn-primary">
          <Plus size={18} />
          <span>Create Subject</span>
        </Link>
      </div>

      <div className="filter-bar">
        <div className="search-input-wrapper">
          <Search size={18} className="field-icon" />
          <input
            type="text"
            placeholder="Search subjects by name or code..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
          />
        </div>

        <select
          className="filter-select"
          value={isActive}
          onChange={(e) => {
            setIsActive(e.target.value);
            setPage(1);
          }}
        >
          <option value="all">All Statuses</option>
          <option value="active">Active Only</option>
          <option value="inactive">Inactive Only</option>
        </select>
      </div>

      {error && <div className="error-banner" style={{ marginBottom: '1rem' }}>{error}</div>}

      <div className="table-container">
        {loading ? (
          <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
            Loading subjects list...
          </div>
        ) : subjects.length === 0 ? (
          <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
            No subjects found matching your filters.
          </div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Code</th>
                <th>Subject Name</th>
                <th>Language</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {subjects.map((subj) => (
                <tr key={subj.id}>
                  <td style={{ fontWeight: 600, color: 'var(--text-accent)' }}>
                    <Link to={`/subjects/${subj.id}`}>{subj.code}</Link>
                  </td>
                  <td>{subj.name}</td>
                  <td>{subj.language.toUpperCase()}</td>
                  <td>
                    <span className={subj.is_active ? 'profile-value badge' : 'profile-value badge btn-logout'}>
                      {subj.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td>
                    <div className="actions-cell">
                      <Link to={`/subjects/${subj.id}`} className="btn btn-secondary btn-sm" title="View details">
                        <ArrowRight size={14} />
                      </Link>
                      <Link to={`/subjects/${subj.id}/edit`} className="btn btn-secondary btn-sm" title="Edit subject">
                        <Edit2 size={14} />
                      </Link>
                      <button
                        onClick={() => handleDelete(subj.id, subj.name)}
                        className="btn btn-danger btn-sm"
                        title="Delete subject"
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
            Page {page} of {totalPages}
          </span>
          <div className="pagination-controls">
            <button
              className="btn btn-secondary btn-sm"
              disabled={page <= 1 || loading}
              onClick={() => setPage((prev) => prev - 1)}
            >
              Previous
            </button>
            <button
              className="btn btn-secondary btn-sm"
              disabled={page >= totalPages || loading}
              onClick={() => setPage((prev) => prev + 1)}
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
