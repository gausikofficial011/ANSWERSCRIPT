import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { client } from '../../api/client';
import { ArrowLeft, CheckCircle2, AlertOctagon, HelpCircle, Lightbulb, Scale } from 'lucide-react';

interface Explanation {
  strengths: string;
  weaknesses: string;
  missing_topics: string[];
  improvement_suggestions: string;
  scoring_reasoning: string;
}

export const EvaluationExplanationViewer: React.FC = () => {
  const { examId, sheetId, id } = useParams<{ examId: string; sheetId: string; id: string }>();

  const [filename, setFilename] = useState<string>('');
  const [explanation, setExplanation] = useState<Explanation | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchExplanationData = async () => {
      setLoading(true);
      setError(null);
      try {
        // 1. Fetch metadata to retrieve original filename
        const sheetRes = await client.get(`/answer-sheets/${sheetId}`);
        setFilename(sheetRes.data.original_filename);

        // 2. Fetch explanation details
        const expRes = await client.get(`/evaluations/${id}/explanation`);
        setExplanation(expRes.data);
      } catch (err) {
        console.error('Failed to fetch explanation details:', err);
        setError('Failed to fetch qualitative explanation and scoring reasoning logs.');
      } finally {
        setLoading(false);
      }
    };

    fetchExplanationData();
  }, [id, sheetId]);

  if (loading) {
    return (
      <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
        Loading qualitative explanation...
      </div>
    );
  }

  if (error || !explanation) {
    return (
      <div style={{ padding: '2rem' }}>
        <div className="error-banner" style={{ marginBottom: '1rem' }}>
          {error || 'No qualitative grading explanation logs found for this evaluation.'}
        </div>
        <Link to={`/exams/${examId}/answer-sheets/${sheetId}/evaluations/${id}`} className="btn btn-secondary">
          <ArrowLeft size={16} />
          <span>Back to Scoring Breakdown</span>
        </Link>
      </div>
    );
  }

  return (
    <div className="explanation-workspace-container" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      
      {/* Header bar */}
      <div className="page-header" style={{ marginBottom: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <Link to={`/exams/${examId}/answer-sheets/${sheetId}/evaluations/${id}`} className="btn btn-secondary btn-sm" title="Back to Scoring details">
            <ArrowLeft size={16} />
          </Link>
          <div>
            <h1 style={{ fontSize: '1.25rem', fontWeight: 600 }}>Qualitative AI Assessment Report: {filename}</h1>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
              Detailed AI feedback analysis and scoring justifications
            </p>
          </div>
        </div>
      </div>

      {/* Grid: Strengths and Weaknesses */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        
        {/* Strengths Card */}
        <div className="detail-card" style={{ border: '1px solid rgba(16, 185, 129, 0.2)', background: 'rgba(16, 185, 129, 0.02)', margin: 0, padding: '1.5rem' }}>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: 'rgb(16, 185, 129)', display: 'flex', alignItems: 'center', gap: '0.5rem', borderBottom: '1px solid rgba(16, 185, 129, 0.1)', paddingBottom: '0.5rem', marginBottom: '1rem' }}>
            <CheckCircle2 size={18} />
            <span>Key Strengths Identified</span>
          </h3>
          <p style={{ fontSize: '0.9rem', lineHeight: '160%', color: 'var(--text-primary)', whiteSpace: 'pre-wrap', margin: 0 }}>
            {explanation.strengths || 'No specific strengths highlighted.'}
          </p>
        </div>

        {/* Weaknesses Card */}
        <div className="detail-card" style={{ border: '1px solid rgba(239, 68, 68, 0.2)', background: 'rgba(239, 68, 68, 0.02)', margin: 0, padding: '1.5rem' }}>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: 'rgb(239, 68, 68)', display: 'flex', alignItems: 'center', gap: '0.5rem', borderBottom: '1px solid rgba(239, 68, 68, 0.1)', paddingBottom: '0.5rem', marginBottom: '1rem' }}>
            <AlertOctagon size={18} />
            <span>Identified Weaknesses</span>
          </h3>
          <p style={{ fontSize: '0.9rem', lineHeight: '160%', color: 'var(--text-primary)', whiteSpace: 'pre-wrap', margin: 0 }}>
            {explanation.weaknesses || 'No specific weaknesses flagged.'}
          </p>
        </div>

      </div>

      {/* Missing Topics Section */}
      <div className="detail-card" style={{ border: '1px solid var(--border-color)', margin: 0, padding: '1.5rem' }}>
        <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '0.5rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem', marginBottom: '1rem' }}>
          <HelpCircle size={18} style={{ color: 'var(--text-accent)' }} />
          <span>Expected Missing Topics & Omissions</span>
        </h3>
        
        {explanation.missing_topics.length === 0 ? (
          <p style={{ fontSize: '0.9rem', color: 'rgb(16, 185, 129)', margin: 0, display: 'flex', alignItems: 'center', gap: '0.4rem', fontWeight: 500 }}>
            <CheckCircle2 size={16} />
            <span>Excellent. No expected keywords or grading topics were missing from the student answer segment.</span>
          </p>
        ) : (
          <div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.8rem' }}>
              The following keywords or concepts identified in the rubric syllabus/model answer were not detected:
            </p>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
              {explanation.missing_topics.map((topic, idx) => (
                <span 
                  key={idx} 
                  style={{ 
                    fontSize: '0.75rem', 
                    fontWeight: 600, 
                    color: 'rgb(239, 68, 68)', 
                    background: 'rgba(239, 68, 68, 0.08)', 
                    border: '1px solid rgba(239, 68, 68, 0.15)', 
                    borderRadius: '20px', 
                    padding: '0.3rem 0.8rem' 
                  }}
                >
                  {topic}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Grid: Suggestions & Scorer Reasoning */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        
        {/* Improvement Suggestions */}
        <div className="detail-card" style={{ border: '1px solid var(--border-color)', margin: 0, padding: '1.5rem' }}>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '0.5rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem', marginBottom: '1rem' }}>
            <Lightbulb size={18} style={{ color: 'rgb(245, 158, 11)' }} />
            <span>AI Improvement Suggestions</span>
          </h3>
          <p style={{ fontSize: '0.9rem', lineHeight: '160%', color: 'var(--text-primary)', whiteSpace: 'pre-wrap', margin: 0 }}>
            {explanation.improvement_suggestions || 'No recommendations recorded.'}
          </p>
        </div>

        {/* Scoring Reasoning */}
        <div className="detail-card" style={{ border: '1px solid var(--border-color)', margin: 0, padding: '1.5rem' }}>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '0.5rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem', marginBottom: '1rem' }}>
            <Scale size={18} style={{ color: 'var(--text-accent)' }} />
            <span>Scoring Scorer Reasoning</span>
          </h3>
          <p style={{ fontSize: '0.9rem', lineHeight: '160%', color: 'var(--text-primary)', whiteSpace: 'pre-wrap', margin: 0 }}>
            {explanation.scoring_reasoning || 'No details provided.'}
          </p>
        </div>

      </div>

    </div>
  );
};
