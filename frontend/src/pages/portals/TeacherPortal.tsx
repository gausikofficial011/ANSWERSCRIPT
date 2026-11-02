import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  BookOpen,
  Edit3,
  Sliders,
  UploadCloud,
  Target,
  PlusCircle,
  ChevronRight,
  CheckCircle2,
  Save,
  ArrowRight
} from 'lucide-react';

export const TeacherPortal: React.FC = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'builder' | 'exams'>('builder');
  const [exams, setExams] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Exam Builder State matching Image 1 Portal 3
  const [currentStep, setCurrentStep] = useState(2); // 2 Questions
  const [questionType, setQuestionType] = useState('ESSAY');
  const [maxMarks, setMaxMarks] = useState(10);
  const [questionText, setQuestionText] = useState('Define Stack and Queue. Explain their operations with examples.');
  const [keywords, setKeywords] = useState<string[]>([
    'Stack', 'Queue', 'LIFO', 'FIFO', 'push', 'pop', 'enqueue', 'dequeue'
  ]);
  const [newKeyword, setNewKeyword] = useState('');
  const [modelAnswer, setModelAnswer] = useState(
    'A stack is a linear data structure that follows Last In First Out (LIFO) principle. It supports push and pop operations.\n' +
    'A queue is a linear data structure that follows First In First Out (FIFO) principle. It supports enqueue and dequeue operations.'
  );
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/v1/exams?page=1&page_size=20')
      .then(res => res.json())
      .then(data => {
        setExams(data?.items || []);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const handleAddKeyword = () => {
    if (newKeyword.trim() && !keywords.includes(newKeyword.trim())) {
      setKeywords([...keywords, newKeyword.trim()]);
      setNewKeyword('');
    }
  };

  const handleRemoveKeyword = (kw: string) => {
    setKeywords(keywords.filter(k => k !== kw));
  };

  const handleSaveQuestion = () => {
    setSaveSuccess(true);
    setTimeout(() => setSaveSuccess(false), 2500);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Editorial Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.25rem' }}>
            <span className="portal-badge teacher">Portal 3: Authoring</span>
            <span style={{ fontSize: '0.8rem', color: '#A5B4FC', fontWeight: 600 }}>Question Papers, Model Answers & Rubrics</span>
          </div>
          <h1 style={{ fontSize: '1.85rem', fontWeight: 800, color: '#F8FAFC', letterSpacing: '-0.02em', margin: 0 }}>
            Teacher Portal — Exam & Question Creation
          </h1>
          <p style={{ color: '#94A3B8', fontSize: '0.92rem', margin: '0.25rem 0 0 0' }}>
            Subjects &gt; CS202 &gt; Midterm Examination builder with automated keyword extraction and rubric grounding.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button 
            onClick={() => setActiveTab(activeTab === 'builder' ? 'exams' : 'builder')} 
            className="btn btn-secondary" 
            style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
          >
            <BookOpen size={16} />
            <span>{activeTab === 'builder' ? 'View All Exams' : 'Open Question Builder'}</span>
          </button>
          <button onClick={() => navigate('/subjects/new')} className="btn btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <PlusCircle size={16} />
            <span>New Subject</span>
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '0.5rem', borderBottom: '1px solid rgba(226, 232, 240, 0.1)', paddingBottom: '0.5rem' }}>
        <button
          onClick={() => setActiveTab('builder')}
          style={{
            background: activeTab === 'builder' ? 'rgba(79, 70, 229, 0.25)' : 'transparent',
            border: activeTab === 'builder' ? '1px solid rgba(129, 140, 248, 0.4)' : '1px solid transparent',
            color: activeTab === 'builder' ? '#FFFFFF' : '#94A3B8',
            padding: '0.5rem 1.2rem',
            borderRadius: 8,
            fontWeight: 700,
            fontSize: '0.88rem',
            cursor: 'pointer'
          }}
        >
          📝 Examination Builder (Step Wizard)
        </button>
        <button
          onClick={() => setActiveTab('exams')}
          style={{
            background: activeTab === 'exams' ? 'rgba(79, 70, 229, 0.25)' : 'transparent',
            border: activeTab === 'exams' ? '1px solid rgba(129, 140, 248, 0.4)' : '1px solid transparent',
            color: activeTab === 'exams' ? '#FFFFFF' : '#94A3B8',
            padding: '0.5rem 1.2rem',
            borderRadius: 8,
            fontWeight: 700,
            fontSize: '0.88rem',
            cursor: 'pointer'
          }}
        >
          📚 Authored Examinations ({exams.length || 4})
        </button>
      </div>

      {/* TAB 1: INTERACTIVE STEP WIZARD MATCHING IMAGE 1 PORTAL 3 */}
      {activeTab === 'builder' && (
        <div style={{ background: '#0F172A', border: '1px solid rgba(226, 232, 240, 0.12)', borderRadius: 16, padding: '1.8rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Breadcrumb & Steps */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', borderBottom: '1px solid rgba(255, 255, 255, 0.08)', paddingBottom: '1.2rem' }}>
            <div>
              <div style={{ fontSize: '0.82rem', color: '#94A3B8' }}>Subjects &gt; CS202 &gt; Midterm Examination</div>
              <h2 style={{ fontSize: '1.35rem', fontWeight: 800, color: '#FFFFFF', margin: '0.2rem 0 0 0' }}>Create Examination</h2>
            </div>

            {/* 5-Step Process Bar */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
              {[
                { num: 1, label: 'Basic Details' },
                { num: 2, label: 'Questions' },
                { num: 3, label: 'Model Answers' },
                { num: 4, label: 'Rubric' },
                { num: 5, label: 'Publish' },
              ].map(step => (
                <div 
                  key={step.num}
                  onClick={() => setCurrentStep(step.num)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.4rem',
                    padding: '0.35rem 0.75rem',
                    borderRadius: 9999,
                    background: currentStep === step.num ? '#4F46E5' : 'rgba(255, 255, 255, 0.05)',
                    border: currentStep === step.num ? '1px solid #818CF8' : '1px solid rgba(255, 255, 255, 0.08)',
                    color: currentStep === step.num ? '#FFFFFF' : '#94A3B8',
                    fontSize: '0.78rem',
                    fontWeight: 600,
                    cursor: 'pointer'
                  }}
                >
                  <span style={{ width: 18, height: 18, borderRadius: '50%', background: currentStep === step.num ? '#FFFFFF' : 'rgba(255, 255, 255, 0.1)', color: currentStep === step.num ? '#4F46E5' : '#CBD5E1', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.7rem', fontWeight: 800 }}>
                    {step.num}
                  </span>
                  <span>{step.label}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Question Configuration Header */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <span style={{ fontSize: '1.1rem', fontWeight: 800, color: '#FFFFFF' }}>Question 1 (10 Marks)</span>
              <span style={{ background: 'rgba(79, 70, 229, 0.2)', color: '#A5B4FC', border: '1px solid rgba(99, 102, 241, 0.4)', borderRadius: 6, padding: '0.2rem 0.6rem', fontSize: '0.75rem', fontWeight: 700 }}>
                Active Section A
              </span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <label style={{ fontSize: '0.82rem', color: '#94A3B8', fontWeight: 600 }}>Question Type</label>
                <select 
                  value={questionType}
                  onChange={(e) => setQuestionType(e.target.value)}
                  style={{ background: '#1E293B', border: '1px solid rgba(255, 255, 255, 0.15)', color: '#F8FAFC', borderRadius: 6, padding: '0.35rem 0.75rem', fontSize: '0.82rem' }}
                >
                  <option value="ESSAY">ESSAY</option>
                  <option value="SHORT_ANSWER">SHORT ANSWER</option>
                  <option value="NUMERICAL">NUMERICAL</option>
                </select>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <label style={{ fontSize: '0.82rem', color: '#94A3B8', fontWeight: 600 }}>Max Marks</label>
                <input 
                  type="number"
                  value={maxMarks}
                  onChange={(e) => setMaxMarks(Number(e.target.value))}
                  style={{ width: '60px', background: '#1E293B', border: '1px solid rgba(255, 255, 255, 0.15)', color: '#F8FAFC', borderRadius: 6, padding: '0.35rem 0.5rem', fontSize: '0.82rem', textAlign: 'center' }}
                />
              </div>
            </div>
          </div>

          {/* Question Text Editor & Toolbar */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', background: '#1E293B', padding: '0.4rem 0.6rem', borderRadius: '8px 8px 0 0', border: '1px solid rgba(255, 255, 255, 0.1)', borderBottom: 'none' }}>
              {['B', 'I', 'U', 'S', '</>', '≡', '❝'].map((tool, idx) => (
                <button
                  key={idx}
                  type="button"
                  style={{ background: 'transparent', border: 'none', color: '#CBD5E1', padding: '0.2rem 0.5rem', borderRadius: 4, cursor: 'pointer', fontWeight: 700, fontSize: '0.85rem' }}
                >
                  {tool}
                </button>
              ))}
            </div>
            <textarea
              value={questionText}
              onChange={(e) => setQuestionText(e.target.value)}
              rows={3}
              style={{
                width: '100%',
                background: '#0B1120',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '0 0 8px 8px',
                padding: '0.85rem',
                color: '#F8FAFC',
                fontSize: '0.92rem',
                lineHeight: 1.5,
                outline: 'none',
                fontFamily: 'inherit'
              }}
            />
          </div>

          {/* Expected Keywords Section */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <label style={{ fontSize: '0.85rem', fontWeight: 700, color: '#F8FAFC' }}>
                Expected Keywords (Lexical & Concept Grounding)
              </label>
              <span style={{ fontSize: '0.75rem', color: '#94A3B8' }}>{keywords.length} keywords indexed</span>
            </div>

            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', background: '#0B1120', border: '1px solid rgba(255, 255, 255, 0.1)', borderRadius: 8, padding: '0.75rem' }}>
              {keywords.map(kw => (
                <span 
                  key={kw}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '0.35rem',
                    background: 'rgba(239, 68, 68, 0.15)',
                    border: '1px solid rgba(239, 68, 68, 0.35)',
                    color: '#FCA5A5',
                    padding: '0.25rem 0.65rem',
                    borderRadius: 9999,
                    fontSize: '0.78rem',
                    fontWeight: 600
                  }}
                >
                  {kw}
                  <button 
                    type="button" 
                    onClick={() => handleRemoveKeyword(kw)} 
                    style={{ background: 'none', border: 'none', color: '#FCA5A5', cursor: 'pointer', padding: 0, fontSize: '0.85rem', lineHeight: 1 }}
                  >
                    ×
                  </button>
                </span>
              ))}

              <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem' }}>
                <input 
                  type="text"
                  placeholder="+ Add keyword..."
                  value={newKeyword}
                  onChange={(e) => setNewKeyword(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddKeyword())}
                  style={{ background: 'transparent', border: 'none', outline: 'none', color: '#CBD5E1', fontSize: '0.78rem', width: '110px' }}
                />
              </div>
            </div>
          </div>

          {/* Model Answer Section */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <label style={{ fontSize: '0.85rem', fontWeight: 700, color: '#F8FAFC' }}>
              Model Answer (Semantic Vector Benchmark)
            </label>
            <textarea
              value={modelAnswer}
              onChange={(e) => setModelAnswer(e.target.value)}
              rows={4}
              style={{
                width: '100%',
                background: '#0B1120',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: 8,
                padding: '0.85rem',
                color: '#E2E8F0',
                fontSize: '0.88rem',
                lineHeight: 1.6,
                outline: 'none',
                fontFamily: 'inherit'
              }}
            />
          </div>

          {/* Bottom Actions */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid rgba(255, 255, 255, 0.08)', paddingTop: '1.2rem' }}>
            <div>
              {saveSuccess && (
                <span style={{ color: '#86EFAC', fontSize: '0.82rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                  <CheckCircle2 size={16} /> Question, keywords and model answer saved to examination bank!
                </span>
              )}
            </div>

            <div style={{ display: 'flex', gap: '0.85rem' }}>
              <button 
                id="save-question-btn"
                type="button" 
                onClick={handleSaveQuestion}
                className="btn btn-secondary" 
                style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', padding: '0.55rem 1.25rem' }}
              >
                <Save size={16} />
                <span>Save Question</span>
              </button>

              <button 
                id="next-step-btn"
                type="button" 
                onClick={() => setCurrentStep(Math.min(5, currentStep + 1))}
                className="btn btn-primary" 
                style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', padding: '0.55rem 1.35rem' }}
              >
                <span>Next</span>
                <ArrowRight size={16} />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: AUTHORED EXAMINATIONS TABLE */}
      {activeTab === 'exams' && (
        <div style={{ background: '#14243A', border: '1px solid rgba(226, 232, 240, 0.12)', borderRadius: '12px', padding: '1.5rem' }}>
          <h2 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#F8FAFC', marginBottom: '1rem' }}>Authored Examinations</h2>
          {exams.length === 0 && !loading ? (
            <div style={{ textAlign: 'center', padding: '2rem', color: '#94A3B8' }}>No examination papers found. Author a new exam to begin.</div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {exams.map((exam: any) => (
                <div
                  key={exam.id}
                  onClick={() => navigate(`/exams/${exam.id}`)}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '1rem 1.25rem',
                    background: 'rgba(11, 20, 36, 0.5)',
                    border: '1px solid rgba(226, 232, 240, 0.08)',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    transition: 'background 0.15s ease'
                  }}
                >
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                      <span style={{ fontWeight: 700, fontSize: '1rem', color: '#F8FAFC' }}>{exam.title}</span>
                      <span style={{ background: 'rgba(21, 128, 61, 0.2)', color: '#86EFAC', border: '1px solid rgba(21, 128, 61, 0.4)', padding: '0.2rem 0.5rem', borderRadius: '4px', fontSize: '0.7rem', fontWeight: 700 }}>
                        {exam.status}
                      </span>
                    </div>
                    <div style={{ fontSize: '0.8rem', color: '#94A3B8', marginTop: '0.25rem' }}>
                      Max Marks: {exam.total_marks} | Academic Year: 2025-2026
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', color: '#818CF8' }}>
                    <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>Manage Questions & Rubrics</span>
                    <ChevronRight size={18} />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Quick Workspaces Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1rem' }}>
        <div className="kpi-stat-card" style={{ cursor: 'pointer' }} onClick={() => navigate('/subjects')}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div className="kpi-title">Question Paper Builder</div>
            <Edit3 size={18} color="#818CF8" />
          </div>
          <div className="kpi-value" style={{ fontSize: '1.3rem' }}>Sections & Subquestions</div>
          <div className="kpi-subtitle">Maximum marks allocation & question hierarchy</div>
        </div>

        <div className="kpi-stat-card" style={{ cursor: 'pointer' }} onClick={() => navigate('/subjects')}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div className="kpi-title">Criterion Rubric Config</div>
            <Sliders size={18} color="#10B981" />
          </div>
          <div className="kpi-value" style={{ fontSize: '1.3rem' }}>Mathematical Weights</div>
          <div className="kpi-subtitle">Formulation: r_c = beta*s_c + (1-beta)*k_c</div>
        </div>

        <div className="kpi-stat-card" style={{ cursor: 'pointer' }} onClick={() => navigate('/dashboard')}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div className="kpi-title">Batch Ingestion Queue</div>
            <UploadCloud size={18} color="#38BDF8" />
          </div>
          <div className="kpi-value" style={{ fontSize: '1.3rem' }}>Answer Script PDF Upload</div>
          <div className="kpi-subtitle">Validates signatures, rasterises 200 DPI pages</div>
        </div>

        <div className="kpi-stat-card" style={{ cursor: 'pointer' }} onClick={() => navigate('/portals/ai-evaluation')}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div className="kpi-title">Model Answer Calibration</div>
            <Target size={18} color="#F59E0B" />
          </div>
          <div className="kpi-value" style={{ fontSize: '1.3rem' }}>Sample Benchmark</div>
          <div className="kpi-subtitle">Test evaluation accuracy against sample papers</div>
        </div>
      </div>
    </div>
  );
};
