/* eslint-disable react-hooks/set-state-in-effect */
import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { client } from '../../api/client';
import { 
  AlertTriangle, 
  Search, 
  Eye, 
  Clock, 
  CheckCircle, 
  AlertOctagon, 
  BookOpen 
} from 'lucide-react';

interface Student {
  id: string;
  student_number: string;
  full_name: string;
}

interface AnswerSheet {
  id: string;
  student_id: string;
  original_filename: string;
}

interface Exam {
  id: string;
  title: string;
}

interface PlagiarismReport {
  id: string;
  exam_id: string;
  source_answer_sheet_id: string;
  target_answer_sheet_id: string;
  similarity_percentage: number;
  highest_similarity: number;
  risk_level: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export const PlagiarismDashboard: React.FC = () => {
  const [reports, setReports] = useState<PlagiarismReport[]>([]);
  const [students, setStudents] = useState<Student[]>([]);
  const [sheets, setSheets] = useState<AnswerSheet[]>([]);
  const [exams, setExams] = useState<Exam[]>([]);

  // Filtering states
  const [selectedExamId, setSelectedExamId] = useState<string>('');
  const [selectedStatus, setSelectedStatus] = useState<string>('');
  const [selectedRisk, setSelectedRisk] = useState<string>('');
  const [similarityThreshold, setSimilarityThreshold] = useState<number>(0);
  const [searchQuery, setSearchQuery] = useState<string>('');

  // Pagination states (Client-side)
  const [currentPage, setCurrentPage] = useState<number>(1);
  const pageSize = 10;

  // General loading & error states
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError(null);
    try {
      // 1. Fetch reports (flat list)
      const reportsRes = await client.get('/plagiarism/reports');
      setReports(reportsRes.data || []);

      // 2. Fetch students directory
      const studentsRes = await client.get('/students', { params: { page: 1, page_size: 100 } });
      setStudents(studentsRes.data.items || []);

      // 3. Fetch answer sheets directory
      const sheetsRes = await client.get('/answer-sheets', { params: { page: 1, page_size: 100 } });
      setSheets(sheetsRes.data.items || []);

      // 4. Fetch exams directory
      const examsRes = await client.get('/exams', { params: { page: 1, page_size: 100 } });
      setExams(examsRes.data.items || []);
    } catch (err) {
      console.error('Failed to fetch plagiarism reports:', err);
      setError('Failed to fetch plagiarism reports directory. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  // Helper Maps for mapping IDs to names/details
  const studentMap = new Map<string, Student>();
  students.forEach((s) => studentMap.set(s.id, s));

  const sheetMap = new Map<string, AnswerSheet>();
  sheets.forEach((sh) => sheetMap.set(sh.id, sh));

  const examMap = new Map<string, Exam>();
  exams.forEach((ex) => examMap.set(ex.id, ex));

  const resolveStudentInfo = (sheetId: string) => {
    const sheet = sheetMap.get(sheetId);
    if (!sheet) return { name: 'Unknown Student', number: 'N/A' };
    const student = studentMap.get(sheet.student_id);
    return student 
      ? { name: student.full_name, number: student.student_number }
      : { name: 'Awaiting Mapping', number: 'N/A' };
  };

  // Perform filtering of reports list in memory
  const filteredReports = reports.filter((r) => {
    // 1. Exam filter
    if (selectedExamId && r.exam_id !== selectedExamId) return false;

    // 2. Status filter
    if (selectedStatus && r.status !== selectedStatus) return false;

    // 3. Risk filter
    if (selectedRisk && r.risk_level !== selectedRisk) return false;

    // 4. Similarity filter
    if (r.highest_similarity * 100 < similarityThreshold) return false;

    // 5. Search query matching Student names/numbers
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      const s1 = resolveStudentInfo(r.source_answer_sheet_id);
      const s2 = resolveStudentInfo(r.target_answer_sheet_id);
      
      const s1Match = s1.name.toLowerCase().includes(query) || s1.number.toLowerCase().includes(query);
      const s2Match = s2.name.toLowerCase().includes(query) || s2.number.toLowerCase().includes(query);
      
      if (!s1Match && !s2Match) return false;
    }

    return true;
  });

  // Client-side pagination division
  const totalReportsCount = filteredReports.length;
  const totalPages = Math.max(1, Math.ceil(totalReportsCount / pageSize));
  const indexOfLastItem = currentPage * pageSize;
  const indexOfFirstItem = indexOfLastItem - pageSize;
  const currentReportsList = filteredReports.slice(indexOfFirstItem, indexOfLastItem);

  useEffect(() => {
    // Reset pagination to page 1 on filter/search change
    setCurrentPage(1);
  }, [selectedExamId, selectedStatus, selectedRisk, similarityThreshold, searchQuery]);

  // Status badge helper
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'DETECTED':
        return (
          <span className="profile-value badge badge-info" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}>
            <Clock size={12} />
            <span>PENDING REVIEW</span>
          </span>
        );
      case 'CONFIRMED_PLAGIARISM':
        return (
          <span className="profile-value badge" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem', background: 'rgba(239, 68, 68, 0.1)', color: 'var(--color-error)', border: '1px solid rgba(239, 68, 68, 0.2)' }}>
            <AlertOctagon size={12} />
            <span>CONFIRMED</span>
          </span>
        );
      case 'FALSE_POSITIVE':
        return (
          <span className="profile-value badge" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem', background: 'rgba(255,255,255,0.05)', color: 'var(--text-secondary)', border: '1px solid var(--border-color)' }}>
            <Clock size={12} />
            <span>FALSE POSITIVE</span>
          </span>
        );
      case 'DISMISSED':
        return (
          <span className="profile-value badge badge-success" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}>
            <CheckCircle size={12} />
            <span>DISMISSED</span>
          </span>
        );
      default:
        return <span className="profile-value badge">{status}</span>;
    }
  };

  // Risk Badge helper
  const getRiskBadge = (risk: string) => {
    switch (risk) {
      case 'HIGH_RISK':
        return (
          <span className="profile-value badge" style={{ background: 'rgba(239, 68, 68, 0.1)', color: 'var(--color-error)', border: '1px solid rgba(239, 68, 68, 0.2)' }}>
            HIGH RISK
          </span>
        );
      case 'SUSPICIOUS':
        return (
          <span className="profile-value badge" style={{ background: 'rgba(245, 158, 11, 0.1)', color: 'rgb(245, 158, 11)', border: '1px solid rgba(245, 158, 11, 0.2)' }}>
            SUSPICIOUS
          </span>
        );
      case 'CLEAN':
        return (
          <span className="profile-value badge badge-success">
            CLEAN
          </span>
        );
      default:
        return <span className="profile-value badge">{risk}</span>;
    }
  };

  // Score visual percentage color
  const getSimilarityColor = (pct: number) => {
    if (pct >= 70) return 'var(--color-error)';
    if (pct >= 40) return 'rgb(245, 158, 11)';
    return 'var(--color-success)';
  };

  // KPI Calculations
  const totalFlagged = reports.length;
  const pendingCount = reports.filter((r) => r.status === 'DETECTED').length;
  const confirmedCount = reports.filter((r) => r.status === 'CONFIRMED_PLAGIARISM').length;
  const falsePosCount = reports.filter((r) => r.status === 'FALSE_POSITIVE').length;
  const dismissedCount = reports.filter((r) => r.status === 'DISMISSED').length;

  return (
    <div className="plagiarism-dashboard-container" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      
      {/* Header bar */}
      <div className="page-header" style={{ marginBottom: 0 }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <AlertTriangle size={24} style={{ color: 'var(--color-error)' }} />
            <span>Plagiarism Review Dashboard</span>
          </h1>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
            Inspect potential question answer duplications, copy-paste matches, and overlap indexes.
          </p>
        </div>
      </div>

      {error && <div className="error-banner">{error}</div>}

      {/* KPI Cards Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '1rem' }}>
        <div className="detail-card" style={{ display: 'flex', flexDirection: 'column', padding: '1.25rem', margin: 0, border: '1px solid var(--border-color)' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Total Flagged</span>
          <strong style={{ fontSize: '1.75rem', color: 'var(--text-primary)', marginTop: '0.2rem' }}>{totalFlagged}</strong>
        </div>
        <div className="detail-card" style={{ display: 'flex', flexDirection: 'column', padding: '1.25rem', margin: 0, border: '1px solid var(--border-color)' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Pending Review</span>
          <strong style={{ fontSize: '1.75rem', color: 'rgb(245, 158, 11)', marginTop: '0.2rem' }}>{pendingCount}</strong>
        </div>
        <div className="detail-card" style={{ display: 'flex', flexDirection: 'column', padding: '1.25rem', margin: 0, border: '1px solid var(--border-color)' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Confirmed cases</span>
          <strong style={{ fontSize: '1.75rem', color: 'var(--color-error)', marginTop: '0.2rem' }}>{confirmedCount}</strong>
        </div>
        <div className="detail-card" style={{ display: 'flex', flexDirection: 'column', padding: '1.25rem', margin: 0, border: '1px solid var(--border-color)' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>False Positives</span>
          <strong style={{ fontSize: '1.75rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>{falsePosCount}</strong>
        </div>
        <div className="detail-card" style={{ display: 'flex', flexDirection: 'column', padding: '1.25rem', margin: 0, border: '1px solid var(--border-color)' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Dismissed cases</span>
          <strong style={{ fontSize: '1.75rem', color: 'var(--color-success)', marginTop: '0.2rem' }}>{dismissedCount}</strong>
        </div>
      </div>

      {/* Filters and Search Toolbar */}
      <div className="detail-card" style={{ padding: '1.25rem', margin: 0, border: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
          
          {/* Exam Filter */}
          <div className="input-group" style={{ flex: 1, minWidth: '200px' }}>
            <label htmlFor="examFilter">Exam Category</label>
            <select
              id="examFilter"
              value={selectedExamId}
              onChange={(e) => setSelectedExamId(e.target.value)}
              style={{ width: '100%', background: 'var(--bg-input)', color: 'var(--text-primary)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '0.5rem 0.8rem' }}
            >
              <option value="">-- All Exams --</option>
              {exams.map((ex) => (
                <option key={ex.id} value={ex.id}>{ex.title}</option>
              ))}
            </select>
          </div>

          {/* Status Filter */}
          <div className="input-group" style={{ flex: 1, minWidth: '150px' }}>
            <label htmlFor="statusFilter">Review State</label>
            <select
              id="statusFilter"
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              style={{ width: '100%', background: 'var(--bg-input)', color: 'var(--text-primary)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '0.5rem 0.8rem' }}
            >
              <option value="">-- All Statuses --</option>
              <option value="DETECTED">Pending Review</option>
              <option value="CONFIRMED_PLAGIARISM">Confirmed</option>
              <option value="FALSE_POSITIVE">False Positive</option>
              <option value="DISMISSED">Dismissed</option>
            </select>
          </div>

          {/* Risk Filter */}
          <div className="input-group" style={{ flex: 1, minWidth: '150px' }}>
            <label htmlFor="riskFilter">Risk Level</label>
            <select
              id="riskFilter"
              value={selectedRisk}
              onChange={(e) => setSelectedRisk(e.target.value)}
              style={{ width: '100%', background: 'var(--bg-input)', color: 'var(--text-primary)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '0.5rem 0.8rem' }}
            >
              <option value="">-- All Risks --</option>
              <option value="HIGH_RISK">High Risk</option>
              <option value="SUSPICIOUS">Suspicious</option>
              <option value="CLEAN">Clean</option>
            </select>
          </div>

          {/* Search Field */}
          <div className="input-group" style={{ flex: 2, minWidth: '250px' }}>
            <label htmlFor="searchField">Search Student</label>
            <div style={{ position: 'relative' }}>
              <Search size={16} style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-secondary)' }} />
              <input
                id="searchField"
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by student name or register number..."
                style={{ width: '100%', background: 'var(--bg-input)', color: 'var(--text-primary)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '0.5rem 0.8rem 0.5rem 2.2rem' }}
              />
            </div>
          </div>

        </div>

        {/* Similarity Threshold Slider */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', borderTop: '1px solid var(--border-color)', paddingTop: '0.75rem' }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', width: '220px' }}>
            Similarity Threshold: <strong>{similarityThreshold}%</strong> or above
          </span>
          <input
            type="range"
            min="0"
            max="100"
            value={similarityThreshold}
            onChange={(e) => setSimilarityThreshold(parseInt(e.target.value))}
            style={{ flexGrow: 1, accentColor: 'var(--text-accent)' }}
          />
        </div>
      </div>

      {/* Reports Directory Table */}
      <div className="table-container">
        {loading ? (
          <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
            Loading plagiarism directory...
          </div>
        ) : filteredReports.length === 0 ? (
          <div style={{ padding: '4rem 2rem', textAlign: 'center', color: 'var(--text-secondary)', border: '1px dashed var(--border-color)', borderRadius: '12px' }}>
            <AlertTriangle size={48} style={{ color: 'var(--border-color)', marginInline: 'auto', marginBottom: '1rem' }} />
            <h3 style={{ fontSize: '1.1rem', color: 'var(--text-primary)', fontWeight: 600 }}>No Plagiarism Incidents Detected</h3>
            <p style={{ fontSize: '0.85rem', maxWidth: '400px', marginInline: 'auto', marginTop: '0.4rem' }}>
              Congratulations. No answer sheets pairs match the similarity constraints based on the current filtering parameters.
            </p>
          </div>
        ) : (
          <div>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Exam Title</th>
                  <th>Student A (Source)</th>
                  <th>Student B (Target)</th>
                  <th style={{ width: '120px' }}>Max Similarity</th>
                  <th style={{ width: '120px' }}>Risk Level</th>
                  <th style={{ width: '160px' }}>Review Status</th>
                  <th style={{ width: '140px' }}>Date Flagged</th>
                  <th style={{ width: '220px' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {currentReportsList.map((r) => {
                  const exam = examMap.get(r.exam_id);
                  const s1 = resolveStudentInfo(r.source_answer_sheet_id);
                  const s2 = resolveStudentInfo(r.target_answer_sheet_id);

                  return (
                    <tr key={r.id}>
                      <td style={{ fontWeight: 600 }}>
                        {exam ? (
                          <Link to={`/plagiarism/exams/${r.exam_id}`} style={{ color: 'var(--text-accent)', textDecoration: 'none' }} title="View exam stats summary">
                            {exam.title}
                          </Link>
                        ) : (
                          'Generic Exam'
                        )}
                      </td>
                      <td>
                        <div style={{ fontWeight: 600 }}>{s1.name}</div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{s1.number}</div>
                      </td>
                      <td>
                        <div style={{ fontWeight: 600 }}>{s2.name}</div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{s2.number}</div>
                      </td>
                      <td style={{ fontWeight: 700, color: getSimilarityColor(r.highest_similarity * 100) }}>
                        {(r.highest_similarity * 100).toFixed(1)}%
                      </td>
                      <td>{getRiskBadge(r.risk_level)}</td>
                      <td>{getStatusBadge(r.status)}</td>
                      <td style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                        {new Date(r.created_at).toLocaleDateString()}
                      </td>
                      <td>
                        <div className="actions-cell">
                          <Link
                            to={`/plagiarism/reports/${r.id}`}
                            className="btn btn-primary btn-sm"
                            style={{ paddingBlock: '0.3rem', fontSize: '0.8rem', gap: '0.3rem' }}
                            title="Open side-by-side matches comparative view"
                          >
                            <Eye size={12} />
                            <span>View Report</span>
                          </Link>
                          {exam && (
                            <Link
                              to={`/plagiarism/exams/${r.exam_id}`}
                              className="btn btn-secondary btn-sm"
                              style={{ paddingBlock: '0.3rem', fontSize: '0.8rem', gap: '0.3rem' }}
                              title="View general exam stats"
                            >
                              <BookOpen size={12} />
                              <span>Summary</span>
                            </Link>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>

            {/* Pagination Controls */}
            {totalPages > 1 && (
              <div className="pagination-container" style={{ marginTop: '1.25rem' }}>
                <span>
                  Showing {indexOfFirstItem + 1} to {Math.min(indexOfLastItem, totalReportsCount)} of {totalReportsCount} reports
                </span>
                <div className="pagination-controls">
                  <button
                    className="btn btn-secondary btn-sm"
                    disabled={currentPage === 1}
                    onClick={() => setCurrentPage((prev) => prev - 1)}
                  >
                    Previous
                  </button>
                  <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                    Page {currentPage} of {totalPages}
                  </span>
                  <button
                    className="btn btn-secondary btn-sm"
                    disabled={currentPage === totalPages}
                    onClick={() => setCurrentPage((prev) => prev + 1)}
                  >
                    Next
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

    </div>
  );
};
