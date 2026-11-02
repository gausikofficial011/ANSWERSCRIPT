/* eslint-disable react-hooks/exhaustive-deps */
import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { client } from '../../api/client';
import { Plus, Search, Edit2, Trash2 } from 'lucide-react';

interface Student {
  id: string;
  student_number: string;
  full_name: string;
  email: string | null;
  class_section: string | null;
}

export const StudentsList: React.FC = () => {
  const [students, setStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [section, setSection] = useState<string>('all');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [error, setError] = useState<string | null>(null);

  const fetchStudents = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await client.get('/students', {
        params: {
          search: search || undefined,
          class_section: section === 'all' ? undefined : section,
          page,
          page_size: 10,
        },
      });
      setStudents(response.data.items);
      setTotalPages(response.data.pages || 1);
    } catch {
      setError('Failed to fetch students directory.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const delayDebounce = setTimeout(() => {
      fetchStudents();
    }, 300);

    return () => clearTimeout(delayDebounce);
  }, [search, section, page]);

  const handleDelete = async (id: string, name: string) => {
    if (!window.confirm(`Are you sure you want to remove student "${name}" from directories?`)) {
      return;
    }

    try {
      await client.delete(`/students/${id}`);
      fetchStudents();
    } catch {
      alert('Failed to delete student. Please try again.');
    }
  };

  return (
    <div className="students-container">
      <div className="page-header">
        <h1>Students Directory</h1>
        <Link to="/students/new" className="btn btn-primary">
          <Plus size={18} />
          <span>Register Student</span>
        </Link>
      </div>

      <div className="filter-bar">
        <div className="search-input-wrapper">
          <Search size={18} className="field-icon" />
          <input
            type="text"
            placeholder="Search students by name, email, or student number..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
          />
        </div>

        <select
          className="filter-select"
          value={section}
          onChange={(e) => {
            setSection(e.target.value);
            setPage(1);
          }}
        >
          <option value="all">All Sections</option>
          <option value="CS-A">CS-A</option>
          <option value="CS-B">CS-B</option>
          <option value="CS-C">CS-C</option>
        </select>
      </div>

      {error && <div className="error-banner" style={{ marginBottom: '1rem' }}>{error}</div>}

      <div className="table-container">
        {loading ? (
          <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
            Loading students list...
          </div>
        ) : students.length === 0 ? (
          <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
            No student records found.
          </div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Student Number</th>
                <th>Full Name</th>
                <th>Email Address</th>
                <th>Section</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {students.map((student) => (
                <tr key={student.id}>
                  <td style={{ fontWeight: 600, color: 'var(--text-accent)' }}>{student.student_number}</td>
                  <td>{student.full_name}</td>
                  <td>{student.email || 'N/A'}</td>
                  <td>
                    <span className="profile-value badge">
                      {student.class_section || 'N/A'}
                    </span>
                  </td>
                  <td>
                    <div className="actions-cell">
                      <Link to={`/students/${student.id}/edit`} className="btn btn-secondary btn-sm" title="Edit student">
                        <Edit2 size={14} />
                      </Link>
                      <button
                        onClick={() => handleDelete(student.id, student.full_name)}
                        className="btn btn-danger btn-sm"
                        title="Delete student"
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
