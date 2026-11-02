/* eslint-disable react-hooks/exhaustive-deps, react-hooks/set-state-in-effect */
import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { client } from '../../api/client';
import { useAuth } from '../../context/AuthContext';
import { 
  ArrowLeft, 
  RefreshCw, 
  CheckCircle, 
  Clock, 
  AlertTriangle, 
  Info, 
  History, 
  LayoutGrid,
  CheckSquare,
  XSquare,
  FileText
} from 'lucide-react';
import { downloadFile } from '../../utils/download';

interface Question {
  id: string;
  question_number: number;
  question_text: string;
  marks: number;
  question_type: string;
}

interface Evaluation {
  id: string;
  answer_sheet_id: string;
  question_mapping_id: string;
  question_id: string;
  model_answer_id: string;
  rubric_id: string | null;
  max_marks: number;
  ai_score: number | null;
  similarity_score: number | null;
  keyword_match_score: number | null;
  ai_feedback: string | null;
  teacher_score: number | null;
  teacher_feedback: string | null;
  final_score: number | null;
  is_verified: boolean;
  verified_by: string | null;
  verified_at: string | null;
  evaluation_model: string | null;
  evaluation_confidence: number | null;
  created_at: string;
  updated_at: string;
}

interface CriterionEvaluation {
  id: string;
  evaluation_id: string;
  rubric_criterion_id: string;
  ai_score: number | null;
  ai_semantic_score: number | null;
  ai_keyword_score: number | null;
  ai_feedback: string | null;
  teacher_score: number | null;
  teacher_feedback: string | null;
  final_score: number | null;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

interface EvaluationRevision {
  id: string;
  evaluation_id: string;
  revision_number: number;
  previous_score: number | null;
  new_score: number;
  previous_feedback: string | null;
  new_feedback: string | null;
  reason: string;
  changed_by: string;
  created_at: string;
}

interface RubricCriterion {
  id: string;
  rubric_id: string;
  criterion_name: string;
  criterion_description: string | null;
  weight: number;
  max_marks: number;
  expected_keywords: string[];
}

export const EvaluationDetailsViewer: React.FC = () => {
  const { examId, sheetId, id } = useParams<{ examId: string; sheetId: string; id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [filename, setFilename] = useState<string>('');
  const [questions, setQuestions] = useState<Question[]>([]);
  const [sheetEvaluations, setSheetEvaluations] = useState<Evaluation[]>([]);
  
  // Active selection states
  const [activeEvalId, setActiveEvalId] = useState<string | null>(null);
  const [activeQuestionId, setActiveQuestionId] = useState<string | null>(null);
  
  // Detailed scoring states
  const [activeEvaluation, setActiveEvaluation] = useState<Evaluation | null>(null);
  const [criteriaEvaluations, setCriteriaEvaluations] = useState<CriterionEvaluation[]>([]);
  const [revisions, setRevisions] = useState<EvaluationRevision[]>([]);
  const [rubricCriteriaMap, setRubricCriteriaMap] = useState<Record<string, RubricCriterion>>({});

  // Teacher Review Mode States
  const [isEditMode, setIsEditMode] = useState<boolean>(false);
  const [overrideOverallScore, setOverrideOverallScore] = useState<string>('0');
  const [overrideOverallFeedback, setOverrideOverallFeedback] = useState<string>('');
  const [overrideReason, setOverrideReason] = useState<string>('');
  const [overrideCriteriaScores, setOverrideCriteriaScores] = useState<Record<string, string>>({});
  const [overrideCriteriaFeedback, setOverrideCriteriaFeedback] = useState<Record<string, string>>({});

  // Loading and Error states
  const [loadingList, setLoadingList] = useState<boolean>(true);
  const [loadingDetails, setLoadingDetails] = useState<boolean>(false);
  const [reprocessing, setReprocessing] = useState<boolean>(false);
  const [submittingVerify, setSubmittingVerify] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [downloadingPdf, setDownloadingPdf] = useState<boolean>(false);

  // Initialize directory & list data
  const initializePageData = async () => {
    setLoadingList(true);
    setError(null);
    try {
      // 1. Fetch answer sheet details
      const sheetRes = await client.get(`/answer-sheets/${sheetId}`);
      setFilename(sheetRes.data.original_filename);

      // 2. Fetch questions for the exam
      const questionsRes = await client.get('/questions', {
        params: { exam_id: examId, page: 1, page_size: 100 },
      });
      const qList: Question[] = questionsRes.data.items || [];
      qList.sort((a, b) => a.question_number - b.question_number);
      setQuestions(qList);

      // 3. Fetch all evaluations for this answer sheet
      const evalsRes = await client.get(`/evaluations/answer-sheets/${sheetId}`);
      const evalList: Evaluation[] = evalsRes.data || [];
      setSheetEvaluations(evalList);

      // 4. Handle route ID parameter redirect helper
      if (evalList.length > 0) {
        if (id === 'view') {
          // Default selection to the first question's evaluation sorted by number
          const firstEval = [...evalList].sort((a, b) => {
            const qA = qList.find((q) => q.id === a.question_id);
            const qB = qList.find((q) => q.id === b.question_id);
            return (qA?.question_number || 0) - (qB?.question_number || 0);
          })[0];
          
          navigate(`/exams/${examId}/answer-sheets/${sheetId}/evaluations/${firstEval.id}`, { replace: true });
        } else {
          const matched = evalList.find((ev) => ev.id === id);
          if (matched) {
            setActiveEvalId(matched.id);
            setActiveQuestionId(matched.question_id);
          } else {
            setError('Evaluation record not matching this answer sheet.');
          }
        }
      } else {
        // No evaluations available at all
        setLoadingList(false);
      }
    } catch (err) {
      console.error('Failed to load page context directory:', err);
      setError('Failed to fetch evaluation directory and exam questions details.');
    } finally {
      setLoadingList(false);
    }
  };

  useEffect(() => {
    initializePageData();
  }, [examId, sheetId]);

  // Handle updates when url `:id` parameter changes
  useEffect(() => {
    if (id && id !== 'view' && sheetEvaluations.length > 0) {
      const matched = sheetEvaluations.find((ev) => ev.id === id);
      if (matched) {
        setActiveEvalId(matched.id);
        setActiveQuestionId(matched.question_id);
        setIsEditMode(false); // Reset review mode on navigation
      }
    }
  }, [id, sheetEvaluations]);

  // Load detailed evaluation details for the active selected item
  const fetchDetailedEvaluation = async (evaluationId: string) => {
    setLoadingDetails(true);
    try {
      const res = await client.get(`/evaluations/${evaluationId}`);
      const detailed = res.data;
      setActiveEvaluation(detailed.evaluation);
      setCriteriaEvaluations(detailed.criteria_evaluations || []);
      setRevisions(detailed.revisions || []);

      // If rubric is defined, fetch rubric criteria labels
      if (detailed.evaluation.rubric_id) {
        const rubricRes = await client.get(`/rubrics/${detailed.evaluation.rubric_id}`);
        const rubricCriteria: RubricCriterion[] = rubricRes.data.criteria || [];
        const criteriaMap: Record<string, RubricCriterion> = {};
        rubricCriteria.forEach((rc) => {
          criteriaMap[rc.id] = rc;
        });
        setRubricCriteriaMap(criteriaMap);
      } else {
        setRubricCriteriaMap({});
      }
    } catch (err) {
      console.error('Failed to load evaluation details:', err);
      setError('Failed to fetch detailed scoring breakdown and criteria metrics.');
    } finally {
      setLoadingDetails(false);
    }
  };

  useEffect(() => {
    if (activeEvalId) {
      fetchDetailedEvaluation(activeEvalId);
    } else {
      setActiveEvaluation(null);
      setCriteriaEvaluations([]);
      setRevisions([]);
      setRubricCriteriaMap({});
    }
  }, [activeEvalId]);

  // Initialize review mode fields with current values
  const handleEnterReviewMode = () => {
    if (!activeEvaluation) return;
    setError(null);
    setIsEditMode(true);

    const hasRubric = !!activeEvaluation.rubric_id;
    if (hasRubric) {
      const scoresMap: Record<string, string> = {};
      const feedbackMap: Record<string, string> = {};
      criteriaEvaluations.forEach((ce) => {
        const scoreVal = ce.teacher_score !== null ? ce.teacher_score : (ce.ai_score !== null ? ce.ai_score : 0);
        scoresMap[ce.rubric_criterion_id] = scoreVal.toString();
        feedbackMap[ce.rubric_criterion_id] = ce.teacher_feedback || ce.ai_feedback || '';
      });
      setOverrideCriteriaScores(scoresMap);
      setOverrideCriteriaFeedback(feedbackMap);
    } else {
      const currentScore = activeEvaluation.teacher_score !== null ? activeEvaluation.teacher_score : (activeEvaluation.ai_score !== null ? activeEvaluation.ai_score : 0);
      setOverrideOverallScore(currentScore.toString());
    }

    setOverrideOverallFeedback(activeEvaluation.teacher_feedback || activeEvaluation.ai_feedback || '');
    setOverrideReason('');
  };

  const calculateAggregatedScore = (
    scores: Record<string, string>,
    criteriaList: CriterionEvaluation[]
  ) => {
    let totalScore = 0;
    let rubricTotalWeight = 0;

    criteriaList.forEach((ce) => {
      const cDetails = rubricCriteriaMap[ce.rubric_criterion_id];
      if (cDetails) {
        rubricTotalWeight += cDetails.weight;
      }
    });

    if (rubricTotalWeight <= 0 || !activeEvaluation) return 0;

    criteriaList.forEach((ce) => {
      const cDetails = rubricCriteriaMap[ce.rubric_criterion_id];
      if (cDetails) {
        const valStr = scores[ce.rubric_criterion_id] || '0';
        const val = parseFloat(valStr) || 0;
        const effectiveMax = (cDetails.weight / rubricTotalWeight) * activeEvaluation.max_marks;
        const critMax = cDetails.max_marks > 0 ? cDetails.max_marks : 1.0;
        const fraction = Math.max(0.0, Math.min(1.0, val / critMax));
        totalScore += fraction * effectiveMax;
      }
    });

    return Math.round(totalScore * 100) / 100;
  };

  const handleVerifySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeEvalId || !activeEvaluation) return;

    // Validate reason
    if (!overrideReason || overrideReason.trim().length < 3 || overrideReason.trim().length > 500) {
      setError('Validation Error: A change reason between 3 and 500 characters is mandatory.');
      return;
    }

    // Validate scores
    const hasRubrics = !!activeEvaluation.rubric_id;
    let finalTeacherScore: number;
    const criterionOverridesList = [];

    if (hasRubrics) {
      // Validate criterion scores
      for (const ce of criteriaEvaluations) {
        const cDetails = rubricCriteriaMap[ce.rubric_criterion_id];
        if (!cDetails) continue;

        const valStr = overrideCriteriaScores[ce.rubric_criterion_id] || '0';
        const val = parseFloat(valStr);

        if (isNaN(val) || val < 0 || val > cDetails.max_marks) {
          setError(`Validation Error: Score for criterion "${cDetails.criterion_name}" must be between 0 and ${cDetails.max_marks}.`);
          return;
        }

        criterionOverridesList.push({
          rubric_criterion_id: ce.rubric_criterion_id,
          teacher_score: val,
          teacher_feedback: overrideCriteriaFeedback[ce.rubric_criterion_id] || null
        });
      }

      // Compute aggregate total score
      finalTeacherScore = calculateAggregatedScore(overrideCriteriaScores, criteriaEvaluations);
    } else {
      // Validate direct overall score
      const val = parseFloat(overrideOverallScore);
      if (isNaN(val) || val < 0 || val > activeEvaluation.max_marks) {
        setError(`Validation Error: Direct overall score must be between 0 and ${activeEvaluation.max_marks}.`);
        return;
      }
      finalTeacherScore = val;
    }

    setSubmittingVerify(true);
    setError(null);

    const payload = {
      teacher_score: finalTeacherScore,
      teacher_feedback: overrideOverallFeedback || null,
      reason: overrideReason.trim(),
      criterion_overrides: criterionOverridesList
    };

    try {
      const res = await client.post(`/evaluations/${activeEvalId}/verify`, payload);
      
      // Update local evaluation list record
      setSheetEvaluations((prev) => 
        prev.map((ev) => (ev.id === activeEvalId ? { ...ev, ...res.data } : ev))
      );

      // Refresh detailed view
      await fetchDetailedEvaluation(activeEvalId);
      
      setIsEditMode(false);
      alert('Evaluation score override and verification submitted successfully.');
    } catch (err) {
      console.error('Failed to submit score verification:', err);
      const axiosError = err as { response?: { status?: number; data?: { detail?: string } } };
      const status = axiosError.response?.status;
      if (status === 400) {
        setError(axiosError.response?.data?.detail || 'Bad Request: Validation constraints violated.');
      } else if (status === 403) {
        setError('Authorization Failed: Only teachers are authorized to override scores and verify evaluations.');
      } else if (status === 404) {
        setError('Error: Evaluation record not found on server.');
      } else {
        setError('Failed to submit evaluation review overrides due to a server error.');
      }
    } finally {
      setSubmittingVerify(false);
    }
  };

  const handleReevaluate = async () => {
    if (!activeEvalId) return;

    if (!window.confirm('Are you sure you want to trigger AI re-evaluation for this answer? This will re-run the similarity Scorer engines and create a new revision history record.')) {
      return;
    }

    setReprocessing(true);
    setError(null);

    try {
      const res = await client.post(`/evaluations/${activeEvalId}/re-evaluate`);
      
      // Update local evaluation list record
      setSheetEvaluations((prev) => 
        prev.map((ev) => (ev.id === activeEvalId ? { ...ev, ...res.data } : ev))
      );

      // Refresh active evaluation display values
      await fetchDetailedEvaluation(activeEvalId);
      alert('AI scoring completed successfully.');
    } catch (err) {
      console.error('Re-evaluation execution failed:', err);
      const axiosError = err as { response?: { status?: number; data?: { detail?: string } } };
      const status = axiosError.response?.status;
      if (status === 403) {
        setError('Authorization Failed: Only teachers are authorized to re-evaluate scoring sheets.');
      } else if (status === 404) {
        setError('Error: Evaluation record not found on server.');
      } else {
        setError(axiosError.response?.data?.detail || 'Failed to re-run AI evaluation pipeline due to a server error.');
      }
    } finally {
      setReprocessing(false);
    }
  };

  // Switch between navigator item clicks
  const handleQuestionSelect = (question: Question) => {
    setError(null);
    setIsEditMode(false); // Reset edit mode on question change
    const matchedEval = sheetEvaluations.find((ev) => ev.question_id === question.id);
    if (matchedEval) {
      navigate(`/exams/${examId}/answer-sheets/${sheetId}/evaluations/${matchedEval.id}`);
    } else {
      setActiveEvalId(null);
      setActiveQuestionId(question.id);
      setActiveEvaluation(null);
      setCriteriaEvaluations([]);
      setRevisions([]);
      setRubricCriteriaMap({});
    }
  };

  const isTeacher = user?.role === 'teacher';

  const handleDownloadReportPdf = async () => {
    if (!activeEvalId) return;
    setDownloadingPdf(true);
    setError(null);
    try {
      await downloadFile(`/evaluations/${activeEvalId}/report/pdf`);
    } catch (err) {
      console.error('Failed to download evaluation report PDF:', err);
      const axiosError = err as { response?: { data?: { detail?: string } } };
      setError(axiosError?.response?.data?.detail || 'Failed to download evaluation PDF report. Please try again.');
    } finally {
      setDownloadingPdf(false);
    }
  };

  if (loadingList) {
    return (
      <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
        Loading student answer sheet evaluations...
      </div>
    );
  }

  const selectedQuestion = questions.find((q) => q.id === activeQuestionId);
  const liveAggregatedScore = isEditMode && activeEvaluation && activeEvaluation.rubric_id
    ? calculateAggregatedScore(overrideCriteriaScores, criteriaEvaluations)
    : 0;

  return (
    <div className="evaluation-workspace-container" style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 120px)', gap: '1rem', position: 'relative' }}>
      
      {/* Loading Overlay for Re-evaluation / Submissions */}
      {(reprocessing || submittingVerify) && (
        <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(3px)', zIndex: 999, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', gap: '1rem', borderRadius: '12px' }}>
          <RefreshCw className="animate-spin" size={48} style={{ color: 'var(--text-accent)' }} />
          <h3 style={{ fontSize: '1.2rem', fontWeight: 600 }}>
            {reprocessing ? 'Re-evaluating answer via AI Scorer...' : 'Submitting verification overrides to server...'}
          </h3>
        </div>
      )}

      {/* Header Bar */}
      <div className="page-header" style={{ marginBottom: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <Link to={`/exams/${examId}`} className="btn btn-secondary btn-sm" title="Back to Exam Details">
            <ArrowLeft size={16} />
          </Link>
          <div>
            <h1 style={{ fontSize: '1.25rem', fontWeight: 600 }}>AI Grading Evaluation: {filename || 'Answer Sheet'}</h1>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
              Sheet ID: {sheetId} | Status: {sheetEvaluations[0]?.is_verified ? 'Verified' : 'AI Evaluated'}
            </p>
          </div>
        </div>

        {activeEvalId && !isEditMode && (
          <div style={{ display: 'flex', gap: '0.75rem' }}>
            {isTeacher && (
              <button
                onClick={handleEnterReviewMode}
                className="btn btn-primary"
                style={{ gap: '0.4rem' }}
                title="Verify score and input overrides"
              >
                <CheckSquare size={16} />
                <span>Verify & Adjust Score</span>
              </button>
            )}
            <Link
              to={`/exams/${examId}/answer-sheets/${sheetId}/evaluations/${activeEvalId}/explanation`}
              className="btn btn-secondary"
              title="View detailed strengths, weaknesses and scoring explanations"
            >
              View Explanation View
            </Link>
            <button
              onClick={handleDownloadReportPdf}
              disabled={downloadingPdf}
              className="btn btn-secondary"
              style={{ gap: '0.5rem' }}
              title="Download Evaluation Report PDF"
            >
              {downloadingPdf ? <RefreshCw size={16} className="animate-spin" /> : <FileText size={16} />}
              <span>Download PDF Report</span>
            </button>
            <button
              onClick={handleReevaluate}
              disabled={reprocessing || !isTeacher}
              className="btn btn-secondary"
              style={{ gap: '0.5rem', opacity: isTeacher ? 1 : 0.5, cursor: isTeacher ? 'pointer' : 'not-allowed' }}
              title={isTeacher ? 'Re-run AI evaluation engines' : 'Only teachers can re-evaluate answer sheets'}
            >
              <RefreshCw size={16} className={reprocessing ? 'animate-spin' : ''} />
              <span>Re-evaluate Answer</span>
            </button>
          </div>
        )}
      </div>

      {error && (
        <div className="error-banner" style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <AlertTriangle size={16} style={{ flexShrink: 0 }} />
          <span>{error}</span>
        </div>
      )}

      {/* Split Workspace */}
      <div style={{ display: 'flex', flexGrow: 1, gap: '1.5rem', minHeight: 0 }}>
        
        {/* Left Side Question Navigator */}
        <div className="detail-card" style={{ width: '280px', display: 'flex', flexDirection: 'column', gap: '1rem', flexShrink: 0, overflowY: 'auto', margin: 0 }}>
          <h3 style={{ fontSize: '0.95rem', fontWeight: 600, borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <LayoutGrid size={16} />
            <span>Questions Navigator</span>
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
            {questions.map((q) => {
              const matchedEval = sheetEvaluations.find((ev) => ev.question_id === q.id);
              const isActive = q.id === activeQuestionId;

              return (
                <button
                  key={q.id}
                  onClick={() => handleQuestionSelect(q)}
                  style={{
                    display: 'flex',
                    flexDirection: 'column',
                    padding: '0.8rem 1rem',
                    borderRadius: '8px',
                    border: `1px solid ${isActive ? 'var(--text-accent)' : 'var(--border-color)'}`,
                    background: isActive ? 'rgba(170, 59, 255, 0.08)' : 'rgba(0,0,0,0.1)',
                    color: 'var(--text-primary)',
                    textAlign: 'left',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                    gap: '0.3rem',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center' }}>
                    <span style={{ fontWeight: 600 }}>Question {q.question_number}</span>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{q.marks} Marks</span>
                  </div>

                  {matchedEval ? (
                    <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center', marginTop: '0.2rem' }}>
                      <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-accent)' }}>
                        Score: {matchedEval.final_score !== null ? matchedEval.final_score.toFixed(1) : matchedEval.ai_score?.toFixed(1) || '0.0'}
                      </span>
                      {matchedEval.is_verified ? (
                        <span style={{ display: 'flex', alignItems: 'center', gap: '0.2rem', fontSize: '0.7rem', color: 'rgb(16, 185, 129)' }}>
                          <CheckCircle size={10} />
                          <span>Verified</span>
                        </span>
                      ) : (
                        <span style={{ display: 'flex', alignItems: 'center', gap: '0.2rem', fontSize: '0.7rem', color: 'rgb(147, 51, 234)' }}>
                          <Clock size={10} />
                          <span>AI Scored</span>
                        </span>
                      )}
                    </div>
                  ) : (
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontStyle: 'italic', marginTop: '0.2rem' }}>
                      Unmapped / Awaiting OCR
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        </div>

        {/* Right Side Content Panel */}
        <div className="detail-card" style={{ flexGrow: 1, display: 'flex', flexDirection: 'column', minWidth: 0, margin: 0, overflowY: 'auto' }}>
          
          {/* TEACHER REVIEW MODE FORM */}
          {isEditMode && activeEvaluation ? (
            <form onSubmit={handleVerifySubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              <div style={{ borderBottom: '1px solid var(--border-color)', paddingBottom: '0.75rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h2 style={{ fontSize: '1.1rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <CheckSquare size={18} style={{ color: 'var(--text-accent)' }} />
                  <span>Teacher Verification Overrides: Question {selectedQuestion?.question_number}</span>
                </h2>
                <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                  Max Marks: <strong>{activeEvaluation.max_marks}</strong>
                </div>
              </div>

              {/* OVERALL SCORE & COMMENTS CARD */}
              <div className="detail-card" style={{ background: 'rgba(255,255,255,0.01)', border: '1px solid var(--border-color)', padding: '1.25rem', margin: 0, display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <h3 style={{ fontSize: '0.9rem', fontWeight: 600, margin: 0, color: 'var(--text-accent)' }}>Overall Scoring Values</h3>
                
                {activeEvaluation.rubric_id ? (
                  /* Rubric total aggregate display */
                  <div style={{ display: 'flex', gap: '2rem', alignItems: 'center', background: 'rgba(0,0,0,0.1)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                    <div>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', display: 'block' }}>Aggregated Overridden Score:</span>
                      <strong style={{ fontSize: '1.5rem', color: 'var(--color-success)' }}>{liveAggregatedScore.toFixed(1)} / {activeEvaluation.max_marks}</strong>
                    </div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                      Note: The overall score is calculated dynamically based on weights sum of criterion overrides below.
                    </div>
                  </div>
                ) : (
                  /* Overall direct input */
                  <div className="input-group" style={{ maxWidth: '200px' }}>
                    <label htmlFor="overallScoreInput">Direct Score Override</label>
                    <input
                      id="overallScoreInput"
                      type="number"
                      step="0.5"
                      min="0"
                      max={activeEvaluation.max_marks}
                      value={overrideOverallScore}
                      onChange={(e) => setOverrideOverallScore(e.target.value)}
                      style={{ width: '100%', background: 'var(--bg-input)', border: '1px solid var(--border-color)', color: 'var(--text-primary)', borderRadius: '8px', padding: '0.6rem 0.8rem' }}
                      required
                    />
                  </div>
                )}

                <div className="input-group">
                  <label htmlFor="overallFeedbackInput">Overall Feedback Comments</label>
                  <textarea
                    id="overallFeedbackInput"
                    rows={4}
                    value={overrideOverallFeedback}
                    onChange={(e) => setOverrideOverallFeedback(e.target.value)}
                    style={{ width: '100%', background: 'var(--bg-input)', border: '1px solid var(--border-color)', color: 'var(--text-primary)', borderRadius: '8px', padding: '0.8rem', fontFamily: 'inherit', resize: 'vertical' }}
                    placeholder="Enter final question override comments..."
                  />
                </div>
              </div>

              {/* CRITERION OVERRIDES GRID (IF RUBRIC DEFINED) */}
              {activeEvaluation.rubric_id && criteriaEvaluations.length > 0 && (
                <div>
                  <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.8rem' }}>Criterion-specific Overrides</h3>
                  
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    {criteriaEvaluations.map((ce) => {
                      const cDetails = rubricCriteriaMap[ce.rubric_criterion_id];
                      if (!cDetails) return null;

                      return (
                        <div key={ce.id} style={{ border: '1px solid var(--border-color)', borderRadius: '8px', padding: '1rem', background: 'rgba(0,0,0,0.1)' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem', marginBottom: '0.75rem', alignItems: 'flex-start' }}>
                            <div>
                              <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{cDetails.criterion_name}</span>
                              {cDetails.criterion_description && (
                                <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', margin: 0, marginTop: '0.1rem' }}>{cDetails.criterion_description}</p>
                              )}
                            </div>
                            <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Weight: {(cDetails.weight * 100).toFixed(0)}%</span>
                          </div>

                          <div style={{ display: 'grid', gridTemplateColumns: '150px 1fr', gap: '1rem', alignItems: 'flex-start' }}>
                            <div className="input-group">
                              <label>Score (Max: {cDetails.max_marks})</label>
                              <input
                                type="number"
                                step="0.1"
                                min="0"
                                max={cDetails.max_marks}
                                value={overrideCriteriaScores[ce.rubric_criterion_id] || '0'}
                                onChange={(e) => setOverrideCriteriaScores({
                                  ...overrideCriteriaScores,
                                  [ce.rubric_criterion_id]: e.target.value
                                })}
                                style={{ width: '100%', background: 'var(--bg-input)', border: '1px solid var(--border-color)', color: 'var(--text-primary)', borderRadius: '8px', padding: '0.5rem 0.75rem' }}
                                required
                              />
                            </div>
                            <div className="input-group">
                              <label>Feedback Override</label>
                              <input
                                type="text"
                                value={overrideCriteriaFeedback[ce.rubric_criterion_id] || ''}
                                onChange={(e) => setOverrideCriteriaFeedback({
                                  ...overrideCriteriaFeedback,
                                  [ce.rubric_criterion_id]: e.target.value
                                })}
                                placeholder="Enter criterion comments..."
                                style={{ width: '100%', background: 'var(--bg-input)', border: '1px solid var(--border-color)', color: 'var(--text-primary)', borderRadius: '8px', padding: '0.5rem 0.75rem' }}
                              />
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* CHANGE REASON (MANDATORY) */}
              <div className="detail-card" style={{ border: '1px solid var(--border-color)', padding: '1.25rem', margin: 0 }}>
                <div className="input-group">
                  <label htmlFor="reasonInput" style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>Verification / Modification Reason (Mandatory)</span>
                    <span style={{ fontSize: '0.75rem', color: overrideReason.length < 3 || overrideReason.length > 500 ? 'var(--color-error)' : 'var(--color-success)' }}>
                      {overrideReason.length} / 500 chars (Min: 3)
                    </span>
                  </label>
                  <textarea
                    id="reasonInput"
                    rows={2}
                    value={overrideReason}
                    onChange={(e) => setOverrideReason(e.target.value)}
                    style={{ width: '100%', background: 'var(--bg-input)', border: '1px solid var(--border-color)', color: 'var(--text-primary)', borderRadius: '8px', padding: '0.6rem 0.8rem', fontSize: '0.85rem' }}
                    placeholder="Enter short justification explaining verification overrides (e.g. AI failed to detect formula matches)..."
                    required
                  />
                </div>
              </div>

              {/* ACTION BUTTONS */}
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem', marginTop: '1rem' }}>
                <button
                  type="button"
                  onClick={() => setIsEditMode(false)}
                  className="btn btn-secondary"
                  style={{ gap: '0.4rem' }}
                >
                  <XSquare size={16} />
                  <span>Cancel Overrides</span>
                </button>
                <button
                  type="submit"
                  disabled={submittingVerify || overrideReason.trim().length < 3 || overrideReason.trim().length > 500}
                  className="btn btn-primary"
                  style={{ gap: '0.4rem' }}
                >
                  <CheckSquare size={16} />
                  <span>Submit Overrides & Verify</span>
                </button>
              </div>
            </form>
          ) : (
            /* READ MODE PRESENTATION */
            loadingDetails ? (
              <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
                Loading scoring details...
              </div>
            ) : !activeEvalId ? (
              <div style={{ padding: '4rem 2rem', textAlign: 'center', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
                <Info size={48} style={{ color: 'var(--border-color)', marginBottom: '1rem' }} />
                <h3 style={{ fontSize: '1.1rem', color: 'var(--text-primary)', fontWeight: 600, marginBottom: '0.4rem' }}>No AI Scorer Record Available</h3>
                <p style={{ fontSize: '0.85rem', maxWidth: '400px' }}>
                  {selectedQuestion 
                    ? `AI Scorer has not evaluated Question ${selectedQuestion.question_number}. Confirm that this question has been successfully mapped to layout segments inside Mappings.`
                    : 'Select an exam question navigation item from the left pane to explore AI scoring logs.'
                  }
                </p>
              </div>
            ) : (
              activeEvaluation && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                  
                  {/* Score Summary Metrics */}
                  <div style={{ display: 'grid', gridTemplateColumns: '2fr 3fr', gap: '1.5rem' }}>
                    
                    {/* Left Block: Score Card */}
                    <div style={{ background: 'rgba(255,255,255,0.01)', border: '1px solid var(--border-color)', borderRadius: '12px', padding: '1.5rem', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
                      <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Scorer Final Rating</span>
                      <div style={{ display: 'flex', alignItems: 'baseline', marginTop: '0.5rem', marginBottom: '0.5rem' }}>
                        <strong style={{ fontSize: '3rem', color: 'var(--text-accent)', lineHeight: '1' }}>
                          {activeEvaluation.final_score !== null ? activeEvaluation.final_score.toFixed(1) : activeEvaluation.ai_score?.toFixed(1) || '0.0'}
                        </strong>
                        <span style={{ fontSize: '1.25rem', color: 'var(--text-secondary)', marginLeft: '0.2rem' }}>/ {activeEvaluation.max_marks}</span>
                      </div>
                      
                      {activeEvaluation.is_verified ? (
                        <span className="profile-value badge" style={{ background: 'rgba(16, 185, 129, 0.1)', color: 'rgb(16, 185, 129)', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
                          Verified by Instructor
                        </span>
                      ) : (
                        <span className="profile-value badge" style={{ background: 'rgba(147, 51, 234, 0.1)', color: 'rgb(147, 51, 234)', border: '1px solid rgba(147, 51, 234, 0.2)' }}>
                          AI Generated Score
                        </span>
                      )}

                      <div style={{ marginTop: '1.2rem', display: 'flex', flexDirection: 'column', alignItems: 'center', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                        <div>Confidence rating: <strong>{activeEvaluation.evaluation_confidence ? `${(activeEvaluation.evaluation_confidence * 100).toFixed(0)}%` : 'N/A'}</strong></div>
                        <div>Engine Model: <strong>{activeEvaluation.evaluation_model || 'GPT Scorer'}</strong></div>
                      </div>
                    </div>

                    {/* Right Block: Weight progress gauges */}
                    <div style={{ background: 'rgba(255,255,255,0.01)', border: '1px solid var(--border-color)', borderRadius: '12px', padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem', justifyContent: 'center' }}>
                      <h4 style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.4rem', margin: 0 }}>Scoring Weights Comparison Matrix</h4>
                      
                      {/* Semantic Score */}
                      <div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '0.3rem' }}>
                          <span style={{ color: 'var(--text-secondary)' }}>Semantic Answer Match:</span>
                          <strong style={{ color: 'var(--text-primary)' }}>{activeEvaluation.similarity_score ? `${(activeEvaluation.similarity_score * 100).toFixed(0)}%` : '0%'}</strong>
                        </div>
                        <div style={{ height: '6px', background: 'rgba(255,255,255,0.05)', borderRadius: '3px', overflow: 'hidden' }}>
                          <div style={{ width: `${(activeEvaluation.similarity_score || 0) * 100}%`, height: '100%', background: 'rgb(16, 185, 129)', borderRadius: '3px' }} />
                        </div>
                      </div>

                      {/* Keyword Match */}
                      <div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '0.3rem' }}>
                          <span style={{ color: 'var(--text-secondary)' }}>Keyword Presence Match:</span>
                          <strong style={{ color: 'var(--text-primary)' }}>{activeEvaluation.keyword_match_score ? `${(activeEvaluation.keyword_match_score * 100).toFixed(0)}%` : '0%'}</strong>
                        </div>
                        <div style={{ height: '6px', background: 'rgba(255,255,255,0.05)', borderRadius: '3px', overflow: 'hidden' }}>
                          <div style={{ width: `${(activeEvaluation.keyword_match_score || 0) * 100}%`, height: '100%', background: 'rgb(59, 130, 246)', borderRadius: '3px' }} />
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* AI Overall Assessment feedback */}
                  <div>
                    <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.5rem' }}>AI Overall Feedback</h3>
                    <div style={{ background: 'rgba(0,0,0,0.15)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '1.25rem', fontSize: '0.9rem', lineHeight: '150%', color: 'var(--text-primary)', whiteSpace: 'pre-wrap' }}>
                      {activeEvaluation.ai_feedback || '(No feedback provided)'}
                    </div>
                  </div>

                  {/* Criteria Breakdown Table */}
                  <div>
                    <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.6rem' }}>Rubric Criteria Performance Breakdown</h3>
                    {criteriaEvaluations.length === 0 ? (
                      <div style={{ border: '1px solid var(--border-color)', borderRadius: '8px', padding: '1.5rem', textAlign: 'center', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                        No criteria-specific scoring logs generated for this question evaluation.
                      </div>
                    ) : (
                      <div className="table-container" style={{ border: '1px solid var(--border-color)', borderRadius: '8px' }}>
                        <table className="data-table" style={{ margin: 0 }}>
                          <thead>
                            <tr>
                              <th>Criterion Name & Description</th>
                              <th style={{ width: '80px' }}>Weight</th>
                              <th style={{ width: '100px' }}>Semantic</th>
                              <th style={{ width: '100px' }}>Keyword</th>
                              <th style={{ width: '80px' }}>Score</th>
                              <th>AI Criterion Comments</th>
                            </tr>
                          </thead>
                          <tbody>
                            {criteriaEvaluations.map((ce) => {
                              const cDetails = rubricCriteriaMap[ce.rubric_criterion_id];
                              return (
                                <tr key={ce.id}>
                                  <td>
                                    <div style={{ fontWeight: 600, color: 'var(--text-accent)' }}>
                                      {cDetails?.criterion_name || 'Generic Criterion'}
                                    </div>
                                    {cDetails?.criterion_description && (
                                      <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.15rem' }}>
                                        {cDetails.criterion_description}
                                      </div>
                                    )}
                                  </td>
                                  <td>{cDetails ? `${(cDetails.weight * 100).toFixed(0)}%` : 'N/A'}</td>
                                  <td>{ce.ai_semantic_score !== null ? `${(ce.ai_semantic_score * 100).toFixed(0)}%` : 'N/A'}</td>
                                  <td>{ce.ai_keyword_score !== null ? `${(ce.ai_keyword_score * 100).toFixed(0)}%` : 'N/A'}</td>
                                  <td style={{ fontWeight: 700, color: 'var(--text-primary)' }}>
                                    {ce.final_score !== null ? ce.final_score.toFixed(1) : ce.ai_score?.toFixed(1) || '0.0'}
                                  </td>
                                  <td style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                                    {ce.ai_feedback || '-'}
                                  </td>
                                </tr>
                              );
                            })}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>

                  {/* Revisions History Timeline */}
                  <div>
                    <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.6rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                      <History size={18} />
                      <span>Evaluation Revisions Log ({revisions.length})</span>
                    </h3>
                    {revisions.length === 0 ? (
                      <div style={{ border: '1px dashed var(--border-color)', borderRadius: '8px', padding: '1.5rem', textAlign: 'center', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                        First evaluation revision. No subsequent score overrides or reprocessing attempts recorded.
                      </div>
                    ) : (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', borderLeft: '2px solid var(--border-color)', paddingLeft: '1.25rem', marginLeft: '0.5rem', marginTop: '0.5rem' }}>
                        {revisions.map((rev) => (
                          <div key={rev.id} style={{ position: 'relative', background: 'rgba(255,255,255,0.01)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '1rem', display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                            {/* Timeline dot */}
                            <div style={{ position: 'absolute', left: '-27px', top: '1.2rem', width: '10px', height: '10px', borderRadius: '50%', background: 'var(--text-accent)', border: '2px solid var(--bg-dashboard)' }} />
                            
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-accent)' }}>Revision #{rev.revision_number}</span>
                              <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{new Date(rev.created_at).toLocaleString()}</span>
                            </div>

                            <div style={{ fontSize: '0.8rem', display: 'flex', gap: '1.5rem', color: 'var(--text-primary)', paddingBlock: '0.2rem' }}>
                              <div>AI Score: <strong>{activeEvaluation.ai_score !== null ? activeEvaluation.ai_score.toFixed(1) : 'N/A'}</strong></div>
                              <div>Teacher Score: <strong style={{ color: 'var(--color-success)' }}>{rev.new_score.toFixed(1)}</strong></div>
                              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Changer: {rev.changed_by === user?.id ? 'You' : 'Instructor'}</div>
                            </div>

                            {rev.reason && (
                              <div style={{ fontSize: '0.8rem', background: 'rgba(0,0,0,0.1)', border: '1px solid var(--border-color)', borderRadius: '6px', padding: '0.5rem 0.75rem' }}>
                                <span style={{ color: 'var(--text-secondary)', display: 'block', fontSize: '0.7rem', textTransform: 'uppercase', marginBottom: '0.2rem' }}>Reason for override:</span>
                                <span style={{ color: 'var(--text-primary)', fontStyle: 'italic' }}>"{rev.reason}"</span>
                              </div>
                            )}

                            {rev.new_feedback && (
                              <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', margin: 0 }}>
                                Feedback updated: <span style={{ color: 'var(--text-primary)' }}>"{rev.new_feedback}"</span>
                              </p>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                </div>
              )
            )
          )}
        </div>

      </div>

    </div>
  );
};
