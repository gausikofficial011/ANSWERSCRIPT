import React, { useEffect, useState } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { client } from '../../api/client';
import { ArrowLeft, Loader } from 'lucide-react';

export const QuestionCreateEdit: React.FC = () => {
  const { examId, id } = useParams<{ examId: string; id: string }>();
  const isEditMode = !!id;
  const navigate = useNavigate();

  const [questionNumber, setQuestionNumber] = useState<number>(1);
  const [questionText, setQuestionText] = useState('');
  const [marks, setMarks] = useState<number>(5);
  const [questionType, setQuestionType] = useState('short');
  const [languageOption, setLanguageOption] = useState('en');
  const [customLanguage, setCustomLanguage] = useState('');

  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isEditMode) {
      const fetchQuestion = async () => {
        setFetching(true);
        setError(null);
        try {
          const response = await client.get(`/questions/${id}`);
          const data = response.data;
          setQuestionNumber(data.question_number);
          setQuestionText(data.question_text);
          setMarks(data.marks);
          setQuestionType(data.question_type);

          const standardLanguages = ['en', 'hi', 'ta', 'te', 'fr', 'de'];
          if (standardLanguages.includes(data.language)) {
            setLanguageOption(data.language);
            setCustomLanguage('');
          } else {
            setLanguageOption('custom');
            setCustomLanguage(data.language);
          }
        } catch {
          setError('Failed to load question details.');
        } finally {
          setFetching(false);
        }
      };
      fetchQuestion();
    }
  }, [id, isEditMode]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (questionNumber <= 0) {
      setError('Question number must be greater than 0.');
      return;
    }
    if (!questionText.trim()) {
      setError('Question text is required.');
      return;
    }
    if (marks <= 0) {
      setError('Marks must be greater than 0.');
      return;
    }

    const finalLanguage = languageOption === 'custom' ? customLanguage.trim() : languageOption;
    if (!finalLanguage) {
      setError('Language code is required.');
      return;
    }

    setLoading(true);
    setError(null);

    const payload = {
      exam_id: examId,
      question_number: Number(questionNumber),
      question_text: questionText,
      marks: Number(marks),
      question_type: questionType,
      language: finalLanguage,
    };

    try {
      if (isEditMode) {
        await client.put(`/questions/${id}`, payload);
        navigate(`/exams/${examId}`);
      } else {
        const response = await client.post('/questions', payload);
        const newQuestionId = response.data.id;
        // Proceed to next step in the setup wizard
        navigate(`/exams/${examId}/questions/${newQuestionId}/model-answer`);
      }
    } catch (err: unknown) {
      const errMsg =
        err && typeof err === 'object' && 'response' in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : null;
      setError(errMsg || 'Failed to save question. Make sure fields are correct and Question Number is unique for this exam.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="exam-form-container">
      <div className="page-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <Link to={`/exams/${examId}`} className="btn btn-secondary btn-sm" title="Back to Exam Specs">
            <ArrowLeft size={16} />
          </Link>
          <h1>{isEditMode ? 'Edit Question Specifications' : 'Add New Question'}</h1>
        </div>
      </div>

      {fetching ? (
        <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
          Loading question specs...
        </div>
      ) : (
        <div className="form-card">
          {error && <div className="error-banner" style={{ marginBottom: '1.5rem' }}>{error}</div>}

          <form onSubmit={handleSubmit} className="form-layout">
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
              <div className="input-group">
                <label htmlFor="questionNumber">Question Number Order</label>
                <div className="input-wrapper">
                  <input
                    id="questionNumber"
                    type="number"
                    min="1"
                    value={questionNumber}
                    onChange={(e) => setQuestionNumber(Number(e.target.value))}
                    disabled={loading}
                    style={{ paddingLeft: '1rem' }}
                    required
                  />
                </div>
              </div>

              <div className="input-group">
                <label htmlFor="marks">Marks Allocation</label>
                <div className="input-wrapper">
                  <input
                    id="marks"
                    type="number"
                    min="1"
                    value={marks}
                    onChange={(e) => setMarks(Number(e.target.value))}
                    disabled={loading}
                    style={{ paddingLeft: '1rem' }}
                    required
                  />
                </div>
              </div>
            </div>

            <div className="input-group">
              <label htmlFor="questionType">Question Format Type</label>
              <div className="input-wrapper">
                <select
                  id="questionType"
                  value={questionType}
                  onChange={(e) => setQuestionType(e.target.value)}
                  disabled={loading}
                  style={{ width: '100%', background: 'var(--bg-input)', color: 'var(--text-primary)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '0.8rem 1rem', outline: 'none' }}
                >
                  <option value="short">Short Answer Type</option>
                  <option value="long">Long Answer Type</option>
                  <option value="mcq">Multiple Choice (MCQ)</option>
                  <option value="descriptive">Descriptive Detail Type</option>
                </select>
              </div>
            </div>

            <div className="input-group">
              <label htmlFor="language">Question Language</label>
              <div className="input-wrapper" style={{ display: 'flex', flexDirection: 'column', gap: '0.8rem', width: '100%' }}>
                <select
                  id="language"
                  value={languageOption}
                  onChange={(e) => setLanguageOption(e.target.value)}
                  disabled={loading}
                  style={{ width: '100%', background: 'var(--bg-input)', color: 'var(--text-primary)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '0.8rem 1rem', outline: 'none' }}
                >
                  <option value="en">English (EN)</option>
                  <option value="hi">Hindi (HI)</option>
                  <option value="ta">Tamil (TA)</option>
                  <option value="te">Telugu (TE)</option>
                  <option value="fr">French (FR)</option>
                  <option value="de">German (DE)</option>
                  <option value="custom">Custom ISO Code...</option>
                </select>

                {languageOption === 'custom' && (
                  <input
                    type="text"
                    placeholder="e.g. ja, it, es"
                    value={customLanguage}
                    onChange={(e) => setCustomLanguage(e.target.value)}
                    disabled={loading}
                    style={{ background: 'var(--bg-input)', color: 'var(--text-primary)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '0.8rem 1rem', outline: 'none' }}
                    required
                  />
                )}
              </div>
            </div>

            <div className="input-group">
              <label htmlFor="questionText">Question Content Query Text</label>
              <div className="input-wrapper">
                <textarea
                  id="questionText"
                  rows={5}
                  placeholder="Define standard binary search tree implementation and state its time complexities..."
                  value={questionText}
                  onChange={(e) => setQuestionText(e.target.value)}
                  disabled={loading}
                  style={{ width: '100%', background: 'var(--bg-input)', color: 'var(--text-primary)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '1rem', outline: 'none', resize: 'vertical' }}
                  required
                />
              </div>
            </div>

            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end', marginTop: '1rem' }}>
              <Link to={`/exams/${examId}`} className="btn btn-secondary" style={{ display: 'flex', alignItems: 'center' }}>
                Cancel
              </Link>
              <button type="submit" className="btn btn-primary" disabled={loading}>
                {loading && <Loader className="animate-spin" size={16} style={{ marginRight: '0.5rem' }} />}
                <span>{isEditMode ? 'Save Question Specs' : 'Save & Continue'}</span>
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};
