import React, { useEffect, useState } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { client } from '../../api/client';
import { ArrowLeft, Loader, X, Plus } from 'lucide-react';

export const ModelAnswerCreateEdit: React.FC = () => {
  const { examId, questionId } = useParams<{ examId: string; questionId: string }>();
  const navigate = useNavigate();

  const [answerText, setAnswerText] = useState('');
  const [keywords, setKeywords] = useState<string[]>([]);
  const [keywordInput, setKeywordInput] = useState('');

  const [modelAnswerId, setModelAnswerId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [questionNumber, setQuestionNumber] = useState<number | null>(null);

  // Fetch question and existing model answer
  useEffect(() => {
    const initData = async () => {
      setFetching(true);
      setError(null);
      try {
        // 1. Fetch Question details to display context
        const questionRes = await client.get(`/questions/${questionId}`);
        setQuestionNumber(questionRes.data.question_number);

        // 2. Fetch existing model answer
        const modelAnswerRes = await client.get('/model-answers', {
          params: { question_id: questionId },
        });

        const items = modelAnswerRes.data.items || [];
        if (items.length > 0) {
          const ma = items[0];
          setModelAnswerId(ma.id);
          setAnswerText(ma.answer_text);
          setKeywords(ma.keywords || []);
        }
      } catch (err) {
        console.error('Failed to load init data:', err);
        setError('Failed to fetch existing solution specifications.');
      } finally {
        setFetching(false);
      }
    };
    initData();
  }, [questionId]);

  // Tag Add handler
  const addKeyword = () => {
    const val = keywordInput.trim();
    if (!val) return;
    
    if (keywords.includes(val)) {
      setKeywordInput('');
      return;
    }

    setKeywords([...keywords, val]);
    setKeywordInput('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      addKeyword();
    }
  };

  const removeKeyword = (indexToRemove: number) => {
    setKeywords(keywords.filter((_, idx) => idx !== indexToRemove));
  };

  const handleSave = async (redirectTarget: 'rubric' | 'exit') => {
    if (!answerText.trim()) {
      setError('Reference solution answer text is required.');
      return;
    }

    setLoading(true);
    setError(null);

    const payload = {
      question_id: questionId,
      answer_text: answerText,
      keywords: keywords,
    };

    try {
      if (modelAnswerId) {
        // Edit mode
        await client.put(`/model-answers/${modelAnswerId}`, {
          answer_text: answerText,
          keywords: keywords,
        });
      } else {
        // Create mode
        await client.post('/model-answers', payload);
      }

      if (redirectTarget === 'rubric') {
        navigate(`/exams/${examId}/questions/${questionId}/rubric`);
      } else {
        navigate(`/exams/${examId}`);
      }
    } catch (err) {
      const errMsg =
        err && typeof err === 'object' && 'response' in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : null;
      setError(errMsg || 'Failed to save model answer. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="exam-form-container">
      {/* Setup Wizard Progress Header */}
      <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', background: 'var(--bg-card)', padding: '0.8rem 1.5rem', borderRadius: '12px', border: '1px solid var(--border-color)', fontSize: '0.9rem' }}>
          <span style={{ color: 'var(--text-secondary)' }}>Step 1: Question Specs ✓</span>
          <span style={{ color: 'var(--border-color)' }}>➔</span>
          <span style={{ color: 'var(--text-accent)', fontWeight: 600 }}>Step 2: Reference Solution</span>
          <span style={{ color: 'var(--border-color)' }}>➔</span>
          <span style={{ color: 'var(--text-secondary)' }}>Step 3: Grading Rubrics</span>
        </div>
      </div>

      <div className="page-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <Link to={`/exams/${examId}`} className="btn btn-secondary btn-sm" title="Back to Exam Specs">
            <ArrowLeft size={16} />
          </Link>
          <h1>Reference Solution: Question {questionNumber ?? ''}</h1>
        </div>
      </div>

      {fetching ? (
        <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
          Loading reference solution data...
        </div>
      ) : (
        <div className="form-card">
          {error && <div className="error-banner" style={{ marginBottom: '1.5rem' }}>{error}</div>}

          <div className="form-layout">
            <div className="input-group">
              <label htmlFor="answerText">Ideal Reference Answer Text</label>
              <div className="input-wrapper">
                <textarea
                  id="answerText"
                  rows={6}
                  placeholder="Enter the complete correct response or standard answer key solution here..."
                  value={answerText}
                  onChange={(e) => setAnswerText(e.target.value)}
                  disabled={loading}
                  style={{ width: '100%', background: 'var(--bg-input)', color: 'var(--text-primary)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '1rem', outline: 'none', resize: 'vertical' }}
                  required
                />
              </div>
            </div>

            {/* Keyword tag compiler */}
            <div className="input-group">
              <label>Mandatory Grading Keywords & Phrases</label>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                Type a keyword and press **Enter** or **Comma ( , )** to add it to the tags list.
              </p>
              
              <div className="tag-input-container">
                {keywords.map((kw, index) => (
                  <span key={index} className="tag-pill">
                    <span>{kw}</span>
                    <button
                      type="button"
                      onClick={() => removeKeyword(index)}
                      className="tag-remove-btn"
                      disabled={loading}
                    >
                      <X size={12} />
                    </button>
                  </span>
                ))}
                
                <input
                  type="text"
                  placeholder={keywords.length === 0 ? "e.g. recursion, complexity, base case" : "Add word..."}
                  value={keywordInput}
                  onChange={(e) => setKeywordInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  disabled={loading}
                  className="tag-raw-input"
                />

                <button
                  type="button"
                  onClick={addKeyword}
                  className="btn btn-secondary btn-sm"
                  style={{ padding: '0.3rem 0.6rem' }}
                  disabled={loading}
                >
                  <Plus size={14} />
                </button>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end', marginTop: '1.5rem' }}>
              <Link to={`/exams/${examId}`} className="btn btn-secondary">
                Cancel
              </Link>
              
              <button
                type="button"
                onClick={() => handleSave('exit')}
                className="btn btn-secondary"
                disabled={loading}
              >
                Save & Exit
              </button>

              <button
                type="button"
                onClick={() => handleSave('rubric')}
                className="btn btn-primary"
                disabled={loading}
              >
                {loading && <Loader className="animate-spin" size={16} style={{ marginRight: '0.5rem' }} />}
                <span>Save & Continue to Rubric</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
