/* eslint-disable @typescript-eslint/no-explicit-any */
import React, { useEffect, useState } from 'react';
import { client } from '../../api/client';
import { X, Upload, Loader, AlertCircle } from 'lucide-react';

interface Student {
  id: string;
  student_number: string;
  full_name: string;
}

interface AnswerSheetUploadModalProps {
  examId: string;
  onClose: () => void;
  onUploadSuccess: () => void;
}

export const AnswerSheetUploadModal: React.FC<AnswerSheetUploadModalProps> = ({
  examId,
  onClose,
  onUploadSuccess,
}) => {
  const [students, setStudents] = useState<Student[]>([]);
  const [selectedStudentId, setSelectedStudentId] = useState<string>('');
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [dragActive, setDragActive] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [fetchingStudents, setFetchingStudents] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch student directory for manual matching list
  useEffect(() => {
    const fetchStudents = async () => {
      try {
        const res = await client.get('/students', {
          params: { page: 1, page_size: 100 },
        });
        setStudents(res.data.items || []);
      } catch (err) {
        console.error('Failed to load students:', err);
      } finally {
        setFetchingStudents(false);
      }
    };
    fetchStudents();
  }, []);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const validateFiles = (filesList: FileList): File[] => {
    const valid: File[] = [];
    const allowedExtensions = ['.pdf', '.png', '.jpg', '.jpeg'];
    const maxSizeBytes = 50 * 1024 * 1024; // 50MB limit

    for (let i = 0; i < filesList.length; i++) {
      const file = filesList[i];
      const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();

      if (!allowedExtensions.includes(ext)) {
        setError(`Invalid file format: ${file.name}. Only PDF, PNG, JPG, and JPEG are supported.`);
        return [];
      }

      if (file.size > maxSizeBytes) {
        setError(`File exceeds 50MB size limit: ${file.name}`);
        return [];
      }

      if (file.size === 0) {
        setError(`Empty file rejected: ${file.name}`);
        return [];
      }

      valid.push(file);
    }

    setError(null);
    return valid;
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const valid = validateFiles(e.dataTransfer.files);
      if (valid.length > 0) {
        setSelectedFiles(valid);
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const valid = validateFiles(e.target.files);
      if (valid.length > 0) {
        setSelectedFiles(valid);
      }
    }
  };

  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedFiles.length === 0) {
      setError('Please select at least one answer sheet file to upload.');
      return;
    }

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('exam_id', examId);
    if (selectedStudentId) {
      formData.append('student_id', selectedStudentId);
    }
    selectedFiles.forEach((file) => {
      formData.append('files', file);
    });

    try {
      await client.post('/answer-sheets/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      onUploadSuccess();
      onClose();
    } catch (err: any) {
      const errMsg = err?.response?.data?.detail || 'Failed to upload answer sheets.';
      setError(errMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000, backdropFilter: 'blur(4px)' }}>
      <div className="form-card" style={{ width: '550px', maxWidth: '90%', maxHeight: '90vh', overflowY: 'auto', position: 'relative', border: '1px solid var(--border-color)', margin: 0 }}>
        
        <button
          onClick={onClose}
          style={{ position: 'absolute', top: '1.25rem', right: '1.25rem', background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer' }}
          title="Close modal"
          type="button"
        >
          <X size={20} />
        </button>

        <h2 style={{ fontSize: '1.4rem', fontWeight: 600, marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <Upload size={20} style={{ color: 'var(--text-accent)' }} />
          <span>Upload Student Answer Sheets</span>
        </h2>

        {error && (
          <div className="error-banner" style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'flex-start', gap: '0.5rem' }}>
            <AlertCircle size={16} style={{ flexShrink: 0, marginTop: '0.1rem' }} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleUploadSubmit} className="form-layout" style={{ gap: '1.2rem' }}>
          
          <div className="input-group">
            <label htmlFor="studentSelect">Manual Student Mapping (Optional Override)</label>
            {fetchingStudents ? (
              <div style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Loading student register...</div>
            ) : (
              <select
                id="studentSelect"
                value={selectedStudentId}
                onChange={(e) => setSelectedStudentId(e.target.value)}
                disabled={loading}
                style={{ width: '100%', background: 'var(--bg-input)', color: 'var(--text-primary)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '0.8rem 1rem', outline: 'none' }}
              >
                <option value="">-- Let engine auto-detect from OCR --</option>
                {students.map((student) => (
                  <option key={student.id} value={student.id}>
                    {student.full_name} ({student.student_number})
                  </option>
                ))}
              </select>
            )}
          </div>

          <div className="input-group">
            <label>Answer Sheet Files (PDF, PNG, JPG, JPEG — Max 50MB)</label>
            <div
              onDragEnter={handleDrag}
              onDragOver={handleDrag}
              onDragLeave={handleDrag}
              onDrop={handleDrop}
              style={{
                border: `2px dashed ${dragActive ? 'var(--text-accent)' : 'var(--border-color)'}`,
                borderRadius: '12px',
                padding: '2.5rem 1.5rem',
                textAlign: 'center',
                background: dragActive ? 'rgba(170, 59, 255, 0.04)' : 'rgba(0, 0, 0, 0.1)',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
              }}
              onClick={() => document.getElementById('fileInput')?.click()}
            >
              <Upload size={32} style={{ color: dragActive ? 'var(--text-accent)' : 'var(--text-secondary)', marginBottom: '0.75rem', marginInline: 'auto' }} />
              <p style={{ fontSize: '0.9rem', color: 'var(--text-primary)', fontWeight: 500 }}>
                Drag & drop files here, or <span style={{ color: 'var(--text-accent)' }}>browse files</span>
              </p>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.4rem' }}>
                Supports individual pages or bulk package uploads
              </p>
              <input
                id="fileInput"
                type="file"
                multiple
                onChange={handleFileChange}
                accept=".pdf,.png,.jpg,.jpeg"
                disabled={loading}
                style={{ display: 'none' }}
              />
            </div>
          </div>

          {selectedFiles.length > 0 && (
            <div style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '1rem' }}>
              <h4 style={{ fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.5rem', color: 'var(--text-accent)' }}>Selected Files ({selectedFiles.length}):</h4>
              <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '0.4rem', fontSize: '0.8rem' }}>
                {selectedFiles.map((file, index) => (
                  <li key={index} style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-primary)', background: 'rgba(255,255,255,0.01)', padding: '0.3rem 0.5rem', borderRadius: '4px' }}>
                    <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: '300px' }}>{file.name}</span>
                    <span style={{ color: 'var(--text-secondary)' }}>{(file.size / (1024 * 1024)).toFixed(2)} MB</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end', marginTop: '1rem' }}>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={onClose}
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading || selectedFiles.length === 0}
            >
              {loading && <Loader className="animate-spin" size={16} style={{ marginRight: '0.5rem' }} />}
              <span>{loading ? 'Uploading Sheets...' : 'Upload & Process'}</span>
            </button>
          </div>

        </form>
      </div>
    </div>
  );
};
