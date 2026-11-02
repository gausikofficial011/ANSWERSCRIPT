/* eslint-disable @typescript-eslint/no-explicit-any */
import React, { useEffect, useState } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { client } from '../../api/client';
import { ArrowLeft, Loader, Plus, Trash2, X, Info } from 'lucide-react';

interface Criterion {
  id?: string;
  criterion_name: string;
  criterion_description: string;
  weight: number;
  max_marks: number;
  expected_keywords: string[];
  order_index: number;
}

export const RubricCreateEdit: React.FC = () => {
  const { examId, questionId } = useParams<{ examId: string; questionId: string }>();
  const navigate = useNavigate();

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [totalWeight, setTotalWeight] = useState<number>(1.0);
  const [gradingMode, setGradingMode] = useState('ai');
  const [criteria, setCriteria] = useState<Criterion[]>([
    {
      criterion_name: '',
      criterion_description: '',
      weight: 1.0,
      max_marks: 5,
      expected_keywords: [],
      order_index: 0,
    },
  ]);

  const [rubricId, setRubricId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [questionNumber, setQuestionNumber] = useState<number | null>(null);
  const [questionText, setQuestionText] = useState<string>('');

  // Local helper states for individual row keyword inputs
  const [rowKeywordInputs, setRowKeywordInputs] = useState<string[]>(['']);

  // Fetch question and existing rubric
  useEffect(() => {
    const initData = async () => {
      setFetching(true);
      setError(null);
      try {
        // 1. Fetch Question details
        const questionRes = await client.get(`/questions/${questionId}`);
        setQuestionNumber(questionRes.data.question_number);
        setQuestionText(questionRes.data.question_text);
        
        // Use default title if not set
        setTitle(`Rubric for Q${questionRes.data.question_number}`);

        // 2. Fetch existing rubrics
        const rubricRes = await client.get('/rubrics', {
          params: { question_id: questionId, is_active: true },
        });

        const items = rubricRes.data.items || [];
        if (items.length > 0) {
          const r = items[0];
          setRubricId(r.id);
          setTitle(r.title);
          setDescription(r.description || '');
          setTotalWeight(r.total_weight);
          setGradingMode(r.grading_mode);
          
          if (r.criteria && r.criteria.length > 0) {
            const loadedCriteria = r.criteria.map((c: any) => ({
              id: c.id,
              criterion_name: c.criterion_name,
              criterion_description: c.criterion_description || '',
              weight: c.weight,
              max_marks: c.max_marks,
              expected_keywords: c.expected_keywords || [],
              order_index: c.order_index,
            }));
            setCriteria(loadedCriteria);
            setRowKeywordInputs(new Array(loadedCriteria.length).fill(''));
          }
        }
      } catch (err) {
        console.error('Failed to load init data:', err);
        setError('Failed to fetch existing grading schema specifications.');
      } finally {
        setFetching(false);
      }
    };
    initData();
  }, [questionId]);

  // Add a criteria row
  const addCriteriaRow = () => {
    setCriteria([
      ...criteria,
      {
        criterion_name: '',
        criterion_description: '',
        weight: 0.0,
        max_marks: 5,
        expected_keywords: [],
        order_index: criteria.length,
      },
    ]);
    setRowKeywordInputs([...rowKeywordInputs, '']);
  };

  // Remove a criteria row
  const removeCriteriaRow = (index: number) => {
    if (criteria.length <= 1) {
      alert('A Rubric must contain at least one criterion.');
      return;
    }
    setCriteria(criteria.filter((_, idx) => idx !== index));
    setRowKeywordInputs(rowKeywordInputs.filter((_, idx) => idx !== index));
  };

  // Handle value change for a criterion
  const handleCriterionChange = (index: number, field: keyof Criterion, value: any) => {
    const updated = [...criteria];
    updated[index] = {
      ...updated[index],
      [field]: value,
    };
    setCriteria(updated);
  };

  // Handle keyword tag operations inside rows
  const handleKeywordKeyDown = (index: number, e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      addKeywordToRow(index);
    }
  };

  const addKeywordToRow = (index: number) => {
    const rawVal = rowKeywordInputs[index] || '';
    const val = rawVal.trim();
    if (!val) return;

    const currentKeywords = criteria[index].expected_keywords;
    if (!currentKeywords.includes(val)) {
      handleCriterionChange(index, 'expected_keywords', [...currentKeywords, val]);
    }

    const updatedInputs = [...rowKeywordInputs];
    updatedInputs[index] = '';
    setRowKeywordInputs(updatedInputs);
  };

  const removeKeywordFromRow = (critIndex: number, keywordIndex: number) => {
    const currentKeywords = criteria[critIndex].expected_keywords;
    const filtered = currentKeywords.filter((_, idx) => idx !== keywordIndex);
    handleCriterionChange(critIndex, 'expected_keywords', filtered);
  };

  // Weight summation validation
  const sumWeights = criteria.reduce((sum, c) => sum + (Number(c.weight) || 0), 0);
  const roundedSum = Math.round(sumWeights * 1000) / 1000;
  const isWeightValid = Math.abs(roundedSum - totalWeight) < 1e-4;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!title.trim()) {
      setError('Rubric title is required.');
      return;
    }
    if (!isWeightValid) {
      setError(`Sum of criteria weights (${roundedSum}) must match rubric total weight (${totalWeight}).`);
      return;
    }

    // Basic validity check of criterion rows
    for (let i = 0; i < criteria.length; i++) {
      if (!criteria[i].criterion_name.trim()) {
        setError(`Criterion row ${i + 1} requires a name.`);
        return;
      }
      if (criteria[i].weight <= 0) {
        setError(`Criterion row ${i + 1} weight must be greater than 0.`);
        return;
      }
      if (criteria[i].max_marks <= 0) {
        setError(`Criterion row ${i + 1} max marks must be greater than 0.`);
        return;
      }
    }

    setLoading(true);
    setError(null);

    // Format criteria payload
    const formattedCriteria = criteria.map((c, index) => ({
      id: c.id, // Only present if editing existing
      criterion_name: c.criterion_name,
      criterion_description: c.criterion_description || null,
      weight: Number(c.weight),
      max_marks: Number(c.max_marks),
      expected_keywords: c.expected_keywords,
      order_index: index,
    }));

    const payload = {
      question_id: questionId,
      title: title,
      description: description || null,
      total_weight: Number(totalWeight),
      grading_mode: gradingMode,
      criteria: formattedCriteria,
    };

    try {
      if (rubricId) {
        // Edit mode
        await client.put(`/rubrics/${rubricId}`, payload);
      } else {
        // Create mode
        await client.post('/rubrics', payload);
      }
      navigate(`/exams/${examId}`);
    } catch (err) {
      const errMsg =
        err && typeof err === 'object' && 'response' in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : null;
      setError(errMsg || 'Failed to save rubric. Please verify weight limits and inputs.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="exam-form-container" style={{ maxWidth: '1000px' }}>
      {/* Setup Wizard Progress Header */}
      <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', background: 'var(--bg-card)', padding: '0.8rem 1.5rem', borderRadius: '12px', border: '1px solid var(--border-color)', fontSize: '0.9rem' }}>
          <span style={{ color: 'var(--text-secondary)' }}>Step 1: Question Specs ✓</span>
          <span style={{ color: 'var(--border-color)' }}>➔</span>
          <span style={{ color: 'var(--text-secondary)' }}>Step 2: Reference Solution ✓</span>
          <span style={{ color: 'var(--border-color)' }}>➔</span>
          <span style={{ color: 'var(--text-accent)', fontWeight: 600 }}>Step 3: Grading Rubrics</span>
        </div>
      </div>

      <div className="page-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <Link to={`/exams/${examId}`} className="btn btn-secondary btn-sm" title="Back to Exam Specs">
            <ArrowLeft size={16} />
          </Link>
          <h1>Grading Rubric builder: Question {questionNumber ?? ''}</h1>
        </div>
      </div>

      {fetching ? (
        <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
          Loading rubric configuration specs...
        </div>
      ) : (
        <div className="form-card">
          {error && <div className="error-banner" style={{ marginBottom: '1.5rem' }}>{error}</div>}

          {/* Context box showing Question Text */}
          <div style={{ background: 'rgba(170, 59, 255, 0.05)', border: '1px solid rgba(170, 59, 255, 0.15)', padding: '1rem', borderRadius: '8px', marginBottom: '1.5rem', fontSize: '0.9rem' }}>
            <span style={{ fontWeight: 600, color: 'var(--text-accent)', display: 'block', marginBottom: '0.2rem' }}>Question Content Context:</span>
            <p style={{ color: 'var(--text-primary)', fontStyle: 'italic', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
              "{questionText}"
            </p>
          </div>

          <form onSubmit={handleSubmit} className="form-layout">
            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr', gap: '1.5rem' }}>
              <div className="input-group">
                <label htmlFor="title">Rubric Title Name</label>
                <div className="input-wrapper">
                  <input
                    id="title"
                    type="text"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    disabled={loading}
                    style={{ paddingLeft: '1rem' }}
                    required
                  />
                </div>
              </div>

              <div className="input-group">
                <label htmlFor="totalWeight">Total Target Weight</label>
                <div className="input-wrapper">
                  <input
                    id="totalWeight"
                    type="number"
                    step="0.1"
                    min="0.1"
                    value={totalWeight}
                    onChange={(e) => setTotalWeight(Number(e.target.value))}
                    disabled={loading}
                    style={{ paddingLeft: '1rem' }}
                    required
                  />
                </div>
              </div>

              <div className="input-group">
                <label htmlFor="gradingMode">Grading Mode</label>
                <div className="input-wrapper">
                  <select
                    id="gradingMode"
                    value={gradingMode}
                    onChange={(e) => setGradingMode(e.target.value)}
                    disabled={loading}
                    style={{ width: '100%', background: 'var(--bg-input)', color: 'var(--text-primary)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '0.8rem 1rem', outline: 'none' }}
                  >
                    <option value="ai">AI Auto Grade</option>
                    <option value="manual">Manual Instructor</option>
                    <option value="hybrid">Hybrid Evaluation</option>
                  </select>
                </div>
              </div>
            </div>

            <div className="input-group">
              <label htmlFor="description">Rubric Instructions / Description</label>
              <div className="input-wrapper">
                <textarea
                  id="description"
                  rows={2}
                  placeholder="Outline any special marking guidelines or descriptions for these grading criteria..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  disabled={loading}
                  style={{ width: '100%', background: 'var(--bg-input)', color: 'var(--text-primary)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '1rem', outline: 'none', resize: 'vertical' }}
                />
              </div>
            </div>

            {/* Criteria builder grid */}
            <div style={{ marginTop: '2rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 600 }}>Rubric Criteria Allocation</h3>
                <button
                  type="button"
                  onClick={addCriteriaRow}
                  className="btn btn-secondary btn-sm"
                  disabled={loading}
                >
                  <Plus size={16} />
                  <span>Add Criterion Row</span>
                </button>
              </div>

              <div className="criteria-list-container" style={{ display: 'flex', flexDirection: 'column', gap: '1.2rem' }}>
                {criteria.map((c, critIdx) => (
                  <div
                    key={critIdx}
                    className="detail-card"
                    style={{ position: 'relative', border: '1px solid var(--border-color)', padding: '1.5rem', borderRadius: '12px', background: 'rgba(27, 28, 36, 0.4)' }}
                  >
                    {/* Delete button top right */}
                    <button
                      type="button"
                      onClick={() => removeCriteriaRow(critIdx)}
                      className="btn btn-danger btn-sm"
                      style={{ position: 'absolute', top: '1rem', right: '1rem', padding: '0.4rem' }}
                      disabled={loading || criteria.length <= 1}
                      title="Remove Criterion"
                    >
                      <Trash2 size={14} />
                    </button>

                    <div style={{ display: 'grid', gridTemplateColumns: '3fr 1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
                      <div className="input-group">
                        <label>Criterion Name *</label>
                        <input
                          type="text"
                          placeholder="e.g. Concept Accuracy"
                          value={c.criterion_name}
                          onChange={(e) => handleCriterionChange(critIdx, 'criterion_name', e.target.value)}
                          disabled={loading}
                          style={{ background: 'var(--bg-input)', color: 'var(--text-primary)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '0.6rem 1rem', outline: 'none', width: '100%' }}
                          required
                        />
                      </div>
                      
                      <div className="input-group">
                        <label>Weight (relative) *</label>
                        <input
                          type="number"
                          step="0.05"
                          min="0.01"
                          max="1.0"
                          placeholder="0.5"
                          value={c.weight}
                          onChange={(e) => handleCriterionChange(critIdx, 'weight', Number(e.target.value))}
                          disabled={loading}
                          style={{ background: 'var(--bg-input)', color: 'var(--text-primary)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '0.6rem 1rem', outline: 'none', width: '100%' }}
                          required
                        />
                      </div>

                      <div className="input-group">
                        <label>Max Marks *</label>
                        <input
                          type="number"
                          step="0.5"
                          min="0.5"
                          placeholder="5.0"
                          value={c.max_marks}
                          onChange={(e) => handleCriterionChange(critIdx, 'max_marks', Number(e.target.value))}
                          disabled={loading}
                          style={{ background: 'var(--bg-input)', color: 'var(--text-primary)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '0.6rem 1rem', outline: 'none', width: '100%' }}
                          required
                        />
                      </div>
                    </div>

                    <div className="input-group" style={{ marginBottom: '1rem' }}>
                      <label>Criterion Description</label>
                      <input
                        type="text"
                        placeholder="Explain what specific technical aspect this criterion evaluates..."
                        value={c.criterion_description}
                        onChange={(e) => handleCriterionChange(critIdx, 'criterion_description', e.target.value)}
                        disabled={loading}
                        style={{ background: 'var(--bg-input)', color: 'var(--text-primary)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '0.6rem 1rem', outline: 'none', width: '100%' }}
                      />
                    </div>

                    {/* Keywords pills for criterion */}
                    <div className="input-group">
                      <label>Expected Keywords (Criterion Specific)</label>
                      <div className="tag-input-container" style={{ padding: '0.4rem' }}>
                        {c.expected_keywords.map((kw, kwIdx) => (
                          <span key={kwIdx} className="tag-pill" style={{ background: 'rgba(255,255,255,0.04)' }}>
                            <span>{kw}</span>
                            <button
                              type="button"
                              onClick={() => removeKeywordFromRow(critIdx, kwIdx)}
                              className="tag-remove-btn"
                              disabled={loading}
                            >
                              <X size={10} />
                            </button>
                          </span>
                        ))}
                        <input
                          type="text"
                          placeholder="Add word..."
                          value={rowKeywordInputs[critIdx] || ''}
                          onChange={(e) => {
                            const val = [...rowKeywordInputs];
                            val[critIdx] = e.target.value;
                            setRowKeywordInputs(val);
                          }}
                          onKeyDown={(e) => handleKeywordKeyDown(critIdx, e)}
                          disabled={loading}
                          className="tag-raw-input"
                          style={{ fontSize: '0.8rem' }}
                        />
                        <button
                          type="button"
                          onClick={() => addKeywordToRow(critIdx)}
                          className="btn btn-secondary btn-sm"
                          style={{ padding: '0.2rem 0.4rem' }}
                          disabled={loading}
                        >
                          <Plus size={12} />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Summation Status Bar */}
            <div
              className={`status-bar ${isWeightValid ? 'status-valid' : 'status-invalid'}`}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.8rem',
                padding: '1rem',
                borderRadius: '8px',
                marginTop: '2rem',
                fontSize: '0.9rem',
                fontWeight: 500,
                border: '1px solid transparent',
              }}
            >
              <Info size={18} />
              <div style={{ flexGrow: 1 }}>
                <span>Sum of Criteria Weights: </span>
                <strong style={{ fontSize: '1.05rem' }}>{roundedSum}</strong>
                <span> / Target Rubric Weight: </span>
                <strong>{totalWeight}</strong>
                {isWeightValid ? (
                  <span style={{ marginLeft: '1rem', color: 'var(--color-success)', fontWeight: 600 }}>✓ Validation Passed</span>
                ) : (
                  <span style={{ marginLeft: '1rem', color: 'var(--color-error)', fontWeight: 600 }}>✗ Weights must sum up to target weight ({totalWeight})</span>
                )}
              </div>
            </div>

            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end', marginTop: '1.5rem' }}>
              <Link to={`/exams/${examId}`} className="btn btn-secondary">
                Cancel
              </Link>
              <button
                type="submit"
                className="btn btn-primary"
                disabled={loading || !isWeightValid}
              >
                {loading && <Loader className="animate-spin" size={16} style={{ marginRight: '0.5rem' }} />}
                <span>Save Rubric Specifications</span>
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};
