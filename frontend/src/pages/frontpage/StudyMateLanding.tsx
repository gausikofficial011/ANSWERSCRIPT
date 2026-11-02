import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';

/* ── Animated Counter Hook ── */
const useCounter = (target: number, duration: number, start: boolean) => {
  const [count, setCount] = useState(0);
  useEffect(() => {
    if (!start) return;
    let startTime: number | null = null;
    const step = (timestamp: number) => {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / duration, 1);
      setCount(Math.floor(progress * target));
      if (progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }, [start, target, duration]);
  return count;
};

const FEATURES = [
  {
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/>
      </svg>
    ),
    title: 'AI Answer Evaluation',
    desc: 'SentenceBERT semantic scoring with evidence-grounded rubric alignment and per-concept coverage analysis.',
    color: '#6366F1',
    bg: 'rgba(99,102,241,0.1)',
    border: 'rgba(99,102,241,0.25)',
  },
  {
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 21V9"/>
      </svg>
    ),
    title: 'OCR Document Studio',
    desc: 'Tesseract 5 LSTM engine extracts handwritten answers with bounding-box overlay and confidence-scored transcript editing.',
    color: '#22D3EE',
    bg: 'rgba(34,211,238,0.1)',
    border: 'rgba(34,211,238,0.25)',
  },
  {
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
      </svg>
    ),
    title: 'Academic Integrity',
    desc: 'Pairwise cosine similarity heatmap flags collusion clusters with verbatim phrase detection before any score is certified.',
    color: '#F59E0B',
    bg: 'rgba(245,158,11,0.1)',
    border: 'rgba(245,158,11,0.25)',
  },
  {
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/>
        <line x1="6" y1="20" x2="6" y2="14"/>
      </svg>
    ),
    title: 'Psychometric Analytics',
    desc: 'Cronbach\'s α reliability, IRT parameters, discrimination index, and department-level benchmark comparisons.',
    color: '#10B981',
    bg: 'rgba(16,185,129,0.1)',
    border: 'rgba(16,185,129,0.25)',
  },
  {
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="3"/><path d="M12 1v4M12 19v4M4.22 4.22l2.83 2.83M16.95 16.95l2.83 2.83M1 12h4M19 12h4M4.22 19.78l2.83-2.83M16.95 7.05l2.83-2.83"/>
      </svg>
    ),
    title: 'Research ML Lab',
    desc: 'Kaggle-benchmarked models (ASAP AES QWK 0.784, Top 15%), local experiment tracking and hardware telemetry.',
    color: '#A78BFA',
    bg: 'rgba(167,139,250,0.1)',
    border: 'rgba(167,139,250,0.25)',
  },
  {
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/>
        <path d="M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75"/>
      </svg>
    ),
    title: '10-Role Portal System',
    desc: 'Isolated JWT-scoped workspaces for Admin, Teacher, OCR, AI Evaluator, Integrity Officer, Student and more.',
    color: '#F472B6',
    bg: 'rgba(244,114,182,0.1)',
    border: 'rgba(244,114,182,0.25)',
  },
];

const PORTALS = [
  { num: '01', name: 'Super Admin Control Plane', route: '/portals/super-admin', tag: 'Governance', color: '#EF4444' },
  { num: '02', name: 'Academic Administration Office', route: '/portals/academic-admin', tag: 'Administration', color: '#F97316' },
  { num: '03', name: 'Teacher & Exam Creator Studio', route: '/portals/teacher', tag: 'Authoring', color: '#EAB308' },
  { num: '04', name: 'OCR & Document Review Studio', route: '/portals/ocr-review', tag: 'Digitization', color: '#22C55E' },
  { num: '05', name: 'AI Evaluation Diagnostics Engine', route: '/portals/ai-evaluation', tag: 'ML Scoring', color: '#06B6D4' },
  { num: '06', name: 'Teacher Evaluator & Moderator', route: '/portals/evaluator', tag: 'Moderation', color: '#6366F1' },
  { num: '07', name: 'Academic Integrity & Collusion', route: '/portals/integrity', tag: 'Integrity', color: '#8B5CF6' },
  { num: '08', name: 'Student Academic Results Hub', route: '/portals/student', tag: 'Student', color: '#EC4899' },
  { num: '09', name: 'Analytics & Psychometric Dashboard', route: '/portals/analytics', tag: 'Analytics', color: '#14B8A6' },
  { num: '10', name: 'AI Research & Model Lab', route: '/portals/research-lab', tag: 'Research', color: '#84CC16' },
];

const TESTIMONIALS = [
  {
    name: 'Dr. Suresh Iyer', role: 'Dean of Examinations, AMAES',
    quote: 'IntelliGrade slashed our result turnaround from 3 weeks to 48 hours. The AI evaluation scores match expert faculty grades with 91% agreement. This is the future of institutional assessment.',
    avatar: 'SI',
    avatarColor: '#6366F1',
  },
  {
    name: 'Prof. Meera Krishnan', role: 'Head of Academic Affairs, BITS Pilani',
    quote: 'The collusion heatmap caught two cases our manual process would have missed entirely. The evidence-span highlighting makes disciplinary proceedings so much simpler to justify.',
    avatar: 'MK',
    avatarColor: '#22C55E',
  },
  {
    name: 'Arjun Reddy', role: 'MCA Student, 24MCA01',
    quote: 'Seeing exactly which concepts I covered and which I missed — with the AI\'s justification — helps me understand not just my score, but how to actually improve. Game changer.',
    avatar: 'AR',
    avatarColor: '#F59E0B',
  },
];

export const StudyMateLanding: React.FC = () => {
  const navigate = useNavigate();
  const [countersStart, setCountersStart] = useState(false);
  const [activeTestimonial, setActiveTestimonial] = useState(0);
  const [activePortalHover, setActivePortalHover] = useState<number | null>(null);
  const statsRef = useRef<HTMLDivElement>(null);

  const c1 = useCounter(50000, 1800, countersStart);
  const c2 = useCounter(1200000, 1800, countersStart);
  const c3 = useCounter(99, 1200, countersStart);
  const c4 = useCounter(10, 900, countersStart);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) setCountersStart(true); },
      { threshold: 0.3 }
    );
    if (statsRef.current) observer.observe(statsRef.current);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    const iv = setInterval(() => setActiveTestimonial(t => (t + 1) % TESTIMONIALS.length), 5000);
    return () => clearInterval(iv);
  }, []);

  return (
    <div style={{ background: '#070B14', minHeight: '100vh', overflowX: 'hidden', fontFamily: "'Inter', system-ui, sans-serif" }}>

      {/* ══════════════════ NAV ══════════════════ */}
      <nav style={{
        position: 'sticky', top: 0, zIndex: 100,
        background: 'rgba(7,11,20,0.85)', backdropFilter: 'blur(20px)',
        borderBottom: '1px solid rgba(255,255,255,0.06)',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '0 5%', height: '68px',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{
            width: 38, height: 38, borderRadius: 10,
            background: 'linear-gradient(135deg, #6366F1, #818CF8)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/>
            </svg>
          </div>
          <div>
            <span style={{ fontSize: '1.15rem', fontWeight: 800, color: '#F8FAFC', letterSpacing: '-0.02em' }}>
              Intelli<span style={{ color: '#818CF8' }}>Grade</span>
            </span>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '2.5rem', alignItems: 'center' }}>
          {['Features', 'Portals', 'ML Research', 'About'].map(item => (
            <a key={item} href={`#${item.toLowerCase().replace(' ', '-')}`}
              style={{ color: '#94A3B8', fontSize: '0.88rem', textDecoration: 'none', fontWeight: 500, transition: 'color 0.2s' }}
              onMouseEnter={e => (e.currentTarget.style.color = '#F8FAFC')}
              onMouseLeave={e => (e.currentTarget.style.color = '#94A3B8')}
            >{item}</a>
          ))}
        </div>

        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button
            onClick={() => navigate('/login')}
            style={{
              padding: '0.5rem 1.25rem', borderRadius: 8, border: '1px solid rgba(255,255,255,0.12)',
              background: 'transparent', color: '#CBD5E1', fontSize: '0.88rem', fontWeight: 600,
              cursor: 'pointer', transition: 'all 0.2s',
            }}
            onMouseEnter={e => { e.currentTarget.style.borderColor = 'rgba(99,102,241,0.5)'; e.currentTarget.style.color = '#F8FAFC'; }}
            onMouseLeave={e => { e.currentTarget.style.borderColor = 'rgba(255,255,255,0.12)'; e.currentTarget.style.color = '#CBD5E1'; }}
          >Sign In</button>
          <button
            onClick={() => navigate('/login')}
            style={{
              padding: '0.5rem 1.25rem', borderRadius: 8, border: 'none',
              background: 'linear-gradient(135deg, #6366F1, #4F46E5)',
              color: '#fff', fontSize: '0.88rem', fontWeight: 700,
              cursor: 'pointer', transition: 'all 0.2s',
              boxShadow: '0 0 20px rgba(99,102,241,0.4)',
            }}
            onMouseEnter={e => e.currentTarget.style.boxShadow = '0 0 30px rgba(99,102,241,0.6)'}
            onMouseLeave={e => e.currentTarget.style.boxShadow = '0 0 20px rgba(99,102,241,0.4)'}
          >Get Access</button>
        </div>
      </nav>

      {/* ══════════════════ HERO ══════════════════ */}
      <section style={{ position: 'relative', padding: '6rem 5% 5rem', overflow: 'hidden' }}>
        {/* Background Grid */}
        <div style={{
          position: 'absolute', inset: 0,
          backgroundImage: `linear-gradient(rgba(99,102,241,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(99,102,241,0.04) 1px, transparent 1px)`,
          backgroundSize: '60px 60px',
        }} />
        {/* Glow Orbs */}
        <div style={{ position: 'absolute', top: '10%', left: '15%', width: 400, height: 400, borderRadius: '50%', background: 'radial-gradient(circle, rgba(99,102,241,0.15) 0%, transparent 70%)', pointerEvents: 'none' }} />
        <div style={{ position: 'absolute', top: '20%', right: '10%', width: 300, height: 300, borderRadius: '50%', background: 'radial-gradient(circle, rgba(34,211,238,0.1) 0%, transparent 70%)', pointerEvents: 'none' }} />

        <div style={{ position: 'relative', maxWidth: 800, margin: '0 auto', textAlign: 'center' }}>
          {/* Badge */}
          <div style={{
            display: 'inline-flex', alignItems: 'center', gap: '0.5rem',
            padding: '0.35rem 1rem', borderRadius: 100,
            border: '1px solid rgba(99,102,241,0.4)',
            background: 'rgba(99,102,241,0.1)',
            marginBottom: '1.5rem',
          }}>
            <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#818CF8', animation: 'pulse 2s infinite' }} />
            <span style={{ fontSize: '0.78rem', color: '#A5B4FC', fontWeight: 600, letterSpacing: '0.06em', textTransform: 'uppercase' }}>
              AI-Powered Academic Assessment Platform
            </span>
          </div>

          {/* Headline */}
          <h1 style={{
            fontSize: 'clamp(2.5rem, 6vw, 4.2rem)',
            fontWeight: 900, lineHeight: 1.08, letterSpacing: '-0.04em',
            color: '#F8FAFC', marginBottom: '1.25rem',
          }}>
            The Future of{' '}
            <span style={{
              background: 'linear-gradient(135deg, #818CF8, #6366F1, #A78BFA)',
              WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
            }}>
              Examination
            </span>
            {' '}Intelligence
          </h1>

          <p style={{ fontSize: '1.1rem', color: '#94A3B8', lineHeight: 1.7, maxWidth: 620, margin: '0 auto 2.5rem' }}>
            IntelliGrade automates answer-script digitization, AI evaluation, integrity checking, and academic analytics — all running <strong style={{ color: '#CBD5E1' }}>100% locally</strong> with zero cloud dependency.
          </p>

          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap', marginBottom: '3.5rem' }}>
            <button
              onClick={() => navigate('/login')}
              style={{
                padding: '0.85rem 2rem', borderRadius: 10, border: 'none',
                background: 'linear-gradient(135deg, #6366F1, #4F46E5)',
                color: '#fff', fontSize: '0.95rem', fontWeight: 700,
                cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.5rem',
                boxShadow: '0 0 30px rgba(99,102,241,0.5), 0 4px 15px rgba(0,0,0,0.3)',
                transition: 'all 0.25s',
              }}
              onMouseEnter={e => e.currentTarget.style.transform = 'translateY(-2px)'}
              onMouseLeave={e => e.currentTarget.style.transform = 'translateY(0)'}
            >
              Access Platform
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
            </button>
            <a href="#portals" style={{
              padding: '0.85rem 2rem', borderRadius: 10,
              border: '1px solid rgba(255,255,255,0.1)',
              background: 'rgba(255,255,255,0.04)',
              color: '#CBD5E1', fontSize: '0.95rem', fontWeight: 600,
              textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.5rem',
              transition: 'all 0.2s',
            }}
              onMouseEnter={e => { (e.currentTarget as HTMLAnchorElement).style.borderColor = 'rgba(255,255,255,0.2)'; (e.currentTarget as HTMLAnchorElement).style.background = 'rgba(255,255,255,0.08)'; }}
              onMouseLeave={e => { (e.currentTarget as HTMLAnchorElement).style.borderColor = 'rgba(255,255,255,0.1)'; (e.currentTarget as HTMLAnchorElement).style.background = 'rgba(255,255,255,0.04)'; }}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><polygon points="10 8 16 12 10 16 10 8"/></svg>
              View All Portals
            </a>
          </div>

          {/* Hero Dashboard Preview */}
          <div style={{
            background: 'linear-gradient(180deg, rgba(20,30,50,0.95) 0%, rgba(11,18,30,0.98) 100%)',
            border: '1px solid rgba(255,255,255,0.08)',
            borderRadius: 16,
            overflow: 'hidden',
            boxShadow: '0 25px 80px rgba(0,0,0,0.6), 0 0 0 1px rgba(99,102,241,0.15)',
          }}>
            {/* Browser Bar */}
            <div style={{ background: 'rgba(0,0,0,0.4)', padding: '0.6rem 1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
              <div style={{ display: 'flex', gap: '0.4rem' }}>
                {['#EF4444', '#F59E0B', '#22C55E'].map((c, i) => <div key={i} style={{ width: 10, height: 10, borderRadius: '50%', background: c, opacity: 0.8 }} />)}
              </div>
              <div style={{ flex: 1, background: 'rgba(255,255,255,0.05)', borderRadius: 6, padding: '0.25rem 0.75rem', fontSize: '0.72rem', color: '#64748B', textAlign: 'center' }}>
                localhost:5173/portals/ai-evaluation
              </div>
            </div>

            {/* Dashboard Content Preview */}
            <div style={{ padding: '1.25rem', display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: '0.75rem' }}>
              {[
                { label: 'Scripts Scored', value: '42', color: '#818CF8', icon: '📄' },
                { label: 'Avg AI Confidence', value: '91.3%', color: '#22C55E', icon: '🎯' },
                { label: 'Avg Score Time', value: '2.1s', color: '#F59E0B', icon: '⚡' },
                { label: 'Concept Hit Rate', value: '87.4%', color: '#38BDF8', icon: '🧠' },
              ].map((kpi, i) => (
                <div key={i} style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 10, padding: '0.85rem', textAlign: 'left' }}>
                  <div style={{ fontSize: '1rem', marginBottom: '0.35rem' }}>{kpi.icon}</div>
                  <div style={{ fontSize: '1.4rem', fontWeight: 800, color: kpi.color, lineHeight: 1 }}>{kpi.value}</div>
                  <div style={{ fontSize: '0.68rem', color: '#64748B', marginTop: '0.25rem' }}>{kpi.label}</div>
                </div>
              ))}
            </div>
            <div style={{ padding: '0 1.25rem 1.25rem', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
              {/* Score bar */}
              <div style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 10, padding: '1rem' }}>
                <div style={{ fontSize: '0.72rem', color: '#64748B', marginBottom: '0.65rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>Concept Coverage — Q1</div>
                {[['Atomicity', 100], ['Consistency', 100], ['Isolation', 90], ['Durability', 85], ['Examples', 70]].map(([c, v]) => (
                  <div key={c as string} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.4rem' }}>
                    <div style={{ width: 80, fontSize: '0.68rem', color: '#94A3B8', flexShrink: 0 }}>{c}</div>
                    <div style={{ flex: 1, height: 5, background: 'rgba(255,255,255,0.05)', borderRadius: 3, overflow: 'hidden' }}>
                      <div style={{ height: '100%', width: `${v}%`, background: (v as number) > 85 ? 'linear-gradient(90deg,#22C55E,#86EFAC)' : 'linear-gradient(90deg,#F59E0B,#FCD34D)', borderRadius: 3 }} />
                    </div>
                    <span style={{ fontSize: '0.65rem', color: '#64748B', width: 28, textAlign: 'right' }}>{v}%</span>
                  </div>
                ))}
              </div>
              {/* Evidence spans */}
              <div style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 10, padding: '1rem' }}>
                <div style={{ fontSize: '0.72rem', color: '#64748B', marginBottom: '0.65rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>Evidence-Grounded Transcript</div>
                <p style={{ fontSize: '0.75rem', color: '#94A3B8', lineHeight: 1.65 }}>
                  ACID stands for{' '}
                  <mark style={{ background: 'rgba(99,102,241,0.3)', color: '#A5B4FC', borderRadius: 3, padding: '1px 3px' }}>Atomicity, Consistency, Isolation, and Durability</mark>.
                  {' '}These ensure database transactions are{' '}
                  <mark style={{ background: 'rgba(34,211,238,0.2)', color: '#67E8F9', borderRadius: 3, padding: '1px 3px' }}>processed reliably</mark>.
                  {' '}Atomicity ensures{' '}
                  <mark style={{ background: 'rgba(99,102,241,0.3)', color: '#A5B4FC', borderRadius: 3, padding: '1px 3px' }}>all operations complete or none do</mark>.
                </p>
                <div style={{ marginTop: '0.75rem', display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
                  <span style={{ fontSize: '0.62rem', padding: '2px 7px', borderRadius: 4, background: 'rgba(99,102,241,0.2)', color: '#A5B4FC', border: '1px solid rgba(99,102,241,0.3)' }}>keyword</span>
                  <span style={{ fontSize: '0.62rem', padding: '2px 7px', borderRadius: 4, background: 'rgba(34,211,238,0.15)', color: '#67E8F9', border: '1px solid rgba(34,211,238,0.25)' }}>concept</span>
                  <span style={{ marginLeft: 'auto', fontSize: '0.62rem', color: '#22C55E', fontWeight: 700 }}>Score: 9.2/10 ✓</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ══════════════════ STATS ══════════════════ */}
      <section ref={statsRef} style={{ padding: '3rem 5%', borderTop: '1px solid rgba(255,255,255,0.05)', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
        <div style={{ maxWidth: 1100, margin: '0 auto', display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: '2rem', textAlign: 'center' }}>
          {[
            { val: c1, suffix: '+', label: 'Exams Processed', color: '#818CF8' },
            { val: c2, suffix: '+', label: 'Student Answers Evaluated', color: '#22D3EE' },
            { val: c3, suffix: '.9%', label: 'System Uptime', color: '#22C55E' },
            { val: c4, suffix: '', label: 'Isolated Role Portals', color: '#F59E0B' },
          ].map((s, i) => (
            <div key={i}>
              <div style={{ fontSize: 'clamp(2rem,4vw,3rem)', fontWeight: 900, color: s.color, letterSpacing: '-0.04em', lineHeight: 1 }}>
                {s.val.toLocaleString()}{s.suffix}
              </div>
              <div style={{ fontSize: '0.85rem', color: '#64748B', marginTop: '0.4rem', fontWeight: 500 }}>{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ══════════════════ FEATURES ══════════════════ */}
      <section id="features" style={{ padding: '6rem 5%' }}>
        <div style={{ maxWidth: 1100, margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '3.5rem' }}>
            <div style={{ fontSize: '0.75rem', color: '#6366F1', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '0.75rem' }}>Platform Capabilities</div>
            <h2 style={{ fontSize: 'clamp(2rem,4vw,2.8rem)', fontWeight: 900, color: '#F8FAFC', letterSpacing: '-0.03em', marginBottom: '0.75rem' }}>
              Every Tool Your Institution Needs
            </h2>
            <p style={{ color: '#64748B', fontSize: '1rem', maxWidth: 520, margin: '0 auto' }}>
              From paper answer sheet to certified published grade — fully automated, fully auditable.
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem' }}>
            {FEATURES.map((f, i) => (
              <div key={i}
                style={{
                  background: 'rgba(255,255,255,0.025)', border: `1px solid ${f.border}`,
                  borderRadius: 14, padding: '1.75rem',
                  transition: 'all 0.3s', cursor: 'default',
                  position: 'relative', overflow: 'hidden',
                }}
                onMouseEnter={e => {
                  e.currentTarget.style.background = `${f.bg}`;
                  e.currentTarget.style.transform = 'translateY(-3px)';
                  e.currentTarget.style.boxShadow = `0 12px 35px rgba(0,0,0,0.3), 0 0 0 1px ${f.border}`;
                }}
                onMouseLeave={e => {
                  e.currentTarget.style.background = 'rgba(255,255,255,0.025)';
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = 'none';
                }}
              >
                <div style={{
                  width: 44, height: 44, borderRadius: 11,
                  background: f.bg, border: `1px solid ${f.border}`,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  color: f.color, marginBottom: '1rem',
                }}>
                  <div style={{ width: 22, height: 22 }}>{f.icon}</div>
                </div>
                <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#F8FAFC', marginBottom: '0.5rem' }}>{f.title}</h3>
                <p style={{ fontSize: '0.85rem', color: '#64748B', lineHeight: 1.65 }}>{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ══════════════════ PORTALS ══════════════════ */}
      <section id="portals" style={{ padding: '6rem 5%', background: 'rgba(255,255,255,0.015)', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
        <div style={{ maxWidth: 1100, margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '3.5rem' }}>
            <div style={{ fontSize: '0.75rem', color: '#6366F1', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '0.75rem' }}>Multi-Portal Architecture</div>
            <h2 style={{ fontSize: 'clamp(2rem,4vw,2.8rem)', fontWeight: 900, color: '#F8FAFC', letterSpacing: '-0.03em', marginBottom: '0.75rem' }}>
              10 Isolated Role Workspaces
            </h2>
            <p style={{ color: '#64748B', fontSize: '1rem' }}>Each portal has its own JWT-scoped workspace, features, and data access rights.</p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '0.85rem' }}>
            {PORTALS.map((p, i) => (
              <div
                key={i}
                onClick={() => navigate('/login')}
                onMouseEnter={() => setActivePortalHover(i)}
                onMouseLeave={() => setActivePortalHover(null)}
                style={{
                  display: 'flex', alignItems: 'center', gap: '1rem',
                  padding: '1rem 1.25rem',
                  background: activePortalHover === i ? 'rgba(255,255,255,0.05)' : 'rgba(255,255,255,0.02)',
                  border: `1px solid ${activePortalHover === i ? `${p.color}40` : 'rgba(255,255,255,0.06)'}`,
                  borderRadius: 10, cursor: 'pointer',
                  transition: 'all 0.2s',
                  transform: activePortalHover === i ? 'translateX(4px)' : 'translateX(0)',
                }}
              >
                <div style={{
                  width: 36, height: 36, borderRadius: 8, flexShrink: 0,
                  background: `${p.color}18`, border: `1px solid ${p.color}30`,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: '0.7rem', fontWeight: 800, color: p.color, fontFamily: 'monospace',
                }}>{p.num}</div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontWeight: 600, color: '#E2E8F0', fontSize: '0.88rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{p.name}</div>
                  <div style={{ fontSize: '0.7rem', color: p.color, fontWeight: 600, marginTop: 1 }}>{p.tag}</div>
                </div>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#64748B" strokeWidth="2.5">
                  <path d="M5 12h14M12 5l7 7-7 7"/>
                </svg>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ══════════════════ ML RESEARCH ══════════════════ */}
      <section id="ml-research" style={{ padding: '6rem 5%' }}>
        <div style={{ maxWidth: 1100, margin: '0 auto', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '4rem', alignItems: 'center' }}>
          <div>
            <div style={{ fontSize: '0.75rem', color: '#6366F1', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '0.75rem' }}>Kaggle Benchmarks</div>
            <h2 style={{ fontSize: 'clamp(1.75rem,3.5vw,2.5rem)', fontWeight: 900, color: '#F8FAFC', letterSpacing: '-0.03em', marginBottom: '1rem', lineHeight: 1.15 }}>
              ML Models Verified Against Global Benchmarks
            </h2>
            <p style={{ color: '#64748B', fontSize: '0.92rem', lineHeight: 1.7, marginBottom: '2rem' }}>
              IntelliGrade's scoring engine was benchmarked against Kaggle's Automated Essay Scoring dataset, achieving Top 15% performance out-of-the-box on standard NLP evaluation metrics.
            </p>
            {[
              { dataset: 'ASAP AES (Essay Scoring)', metric: 'QWK', score: '0.784', rank: 'Top 15%', color: '#22C55E' },
              { dataset: 'STS-Benchmark (Similarity)', metric: 'Pearson r', score: '0.867', rank: 'Top 10%', color: '#818CF8' },
              { dataset: 'Mohler Short-Answer QA', metric: 'QWK', score: '0.721', rank: 'Top 20%', color: '#F59E0B' },
            ].map((b, i) => (
              <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.85rem 1rem', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: 10, marginBottom: '0.6rem' }}>
                <div>
                  <div style={{ fontWeight: 600, color: '#E2E8F0', fontSize: '0.88rem' }}>{b.dataset}</div>
                  <div style={{ fontSize: '0.72rem', color: '#64748B', marginTop: 2 }}>{b.metric}: <strong style={{ color: b.color }}>{b.score}</strong></div>
                </div>
                <span style={{ fontSize: '0.72rem', padding: '0.25rem 0.65rem', borderRadius: 20, background: `${b.color}18`, color: b.color, fontWeight: 700, border: `1px solid ${b.color}30` }}>{b.rank}</span>
              </div>
            ))}
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: 14, padding: '1.5rem' }}>
              <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '1rem' }}>Cronbach's α — Test Reliability</div>
              <div style={{ textAlign: 'center', padding: '1rem 0' }}>
                <div style={{ fontSize: '3.5rem', fontWeight: 900, color: '#818CF8', lineHeight: 1 }}>0.84</div>
                <div style={{ fontSize: '0.8rem', color: '#22C55E', fontWeight: 700, marginTop: '0.35rem' }}>✓ Good Reliability</div>
              </div>
              <div style={{ height: 6, background: 'rgba(255,255,255,0.05)', borderRadius: 3, marginTop: '0.75rem' }}>
                <div style={{ height: '100%', width: '84%', background: 'linear-gradient(90deg,#6366F1,#818CF8)', borderRadius: 3 }} />
              </div>
            </div>
            {[
              ['Active Embedding Model', 'SentenceBERT 768d'],
              ['Scoring Method', 'Cosine Similarity'],
              ['AI-Human Agreement', '91.2%'],
              ['Hardware Mode', '100% Local CPU'],
            ].map(([k, v], i) => (
              <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.65rem 1rem', background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 8 }}>
                <span style={{ color: '#64748B', fontSize: '0.82rem' }}>{k}</span>
                <span style={{ color: '#CBD5E1', fontWeight: 600, fontSize: '0.82rem', fontFamily: 'monospace' }}>{v}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ══════════════════ TESTIMONIALS ══════════════════ */}
      <section style={{ padding: '6rem 5%', background: 'rgba(255,255,255,0.015)', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
        <div style={{ maxWidth: 780, margin: '0 auto', textAlign: 'center' }}>
          <h2 style={{ fontSize: 'clamp(1.75rem,3.5vw,2.5rem)', fontWeight: 900, color: '#F8FAFC', letterSpacing: '-0.03em', marginBottom: '3rem' }}>
            Trusted by Educators & Students
          </h2>

          {/* Testimonial Card */}
          <div style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 16, padding: '2.5rem', position: 'relative', minHeight: 200, transition: 'all 0.4s' }}>
            <div style={{ fontSize: '2.5rem', color: 'rgba(99,102,241,0.4)', lineHeight: 1, marginBottom: '1rem', fontFamily: 'Georgia, serif' }}>"</div>
            <p style={{ color: '#CBD5E1', fontSize: '1rem', lineHeight: 1.75, marginBottom: '1.5rem', fontStyle: 'italic' }}>
              {TESTIMONIALS[activeTestimonial].quote}
            </p>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.85rem' }}>
              <div style={{
                width: 44, height: 44, borderRadius: '50%',
                background: `linear-gradient(135deg, ${TESTIMONIALS[activeTestimonial].avatarColor}, ${TESTIMONIALS[activeTestimonial].avatarColor}80)`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontWeight: 800, fontSize: '0.85rem', color: '#fff',
              }}>
                {TESTIMONIALS[activeTestimonial].avatar}
              </div>
              <div style={{ textAlign: 'left' }}>
                <div style={{ fontWeight: 700, color: '#F8FAFC', fontSize: '0.9rem' }}>{TESTIMONIALS[activeTestimonial].name}</div>
                <div style={{ fontSize: '0.75rem', color: '#64748B' }}>{TESTIMONIALS[activeTestimonial].role}</div>
              </div>
            </div>
          </div>

          {/* Dots */}
          <div style={{ display: 'flex', justifyContent: 'center', gap: '0.5rem', marginTop: '1.5rem' }}>
            {TESTIMONIALS.map((_, i) => (
              <button key={i} onClick={() => setActiveTestimonial(i)} style={{
                width: i === activeTestimonial ? 24 : 8, height: 8,
                borderRadius: 4, border: 'none', cursor: 'pointer',
                background: i === activeTestimonial ? '#6366F1' : 'rgba(255,255,255,0.15)',
                transition: 'all 0.3s',
              }} />
            ))}
          </div>
        </div>
      </section>

      {/* ══════════════════ CTA ══════════════════ */}
      <section style={{ padding: '6rem 5%' }}>
        <div style={{
          maxWidth: 900, margin: '0 auto',
          background: 'linear-gradient(135deg, rgba(99,102,241,0.15), rgba(79,70,229,0.1))',
          border: '1px solid rgba(99,102,241,0.3)', borderRadius: 20,
          padding: '4rem', textAlign: 'center',
          boxShadow: '0 0 80px rgba(99,102,241,0.1)',
          position: 'relative', overflow: 'hidden',
        }}>
          <div style={{ position: 'absolute', top: -60, right: -60, width: 200, height: 200, borderRadius: '50%', background: 'radial-gradient(circle, rgba(99,102,241,0.2), transparent)' }} />
          <h2 style={{ fontSize: 'clamp(1.75rem,4vw,3rem)', fontWeight: 900, color: '#F8FAFC', letterSpacing: '-0.03em', marginBottom: '1rem' }}>
            Ready to Transform Your Institution?
          </h2>
          <p style={{ color: '#94A3B8', fontSize: '1rem', marginBottom: '2.5rem', maxWidth: 500, margin: '0 auto 2.5rem' }}>
            Access all 10 institutional portals and experience AI-powered academic assessment built for the modern university.
          </p>
          <button
            onClick={() => navigate('/login')}
            style={{
              padding: '1rem 2.5rem', borderRadius: 12, border: 'none',
              background: 'linear-gradient(135deg, #6366F1, #4F46E5)',
              color: '#fff', fontSize: '1rem', fontWeight: 700,
              cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: '0.6rem',
              boxShadow: '0 0 40px rgba(99,102,241,0.5)',
              transition: 'all 0.25s',
            }}
            onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-3px)'; e.currentTarget.style.boxShadow = '0 0 60px rgba(99,102,241,0.7)'; }}
            onMouseLeave={e => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = '0 0 40px rgba(99,102,241,0.5)'; }}
          >
            Enter IntelliGrade Platform
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
          </button>
        </div>
      </section>

      {/* ══════════════════ FOOTER ══════════════════ */}
      <footer style={{ borderTop: '1px solid rgba(255,255,255,0.05)', padding: '2.5rem 5%' }}>
        <div style={{ maxWidth: 1100, margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <div style={{ width: 28, height: 28, borderRadius: 7, background: 'linear-gradient(135deg, #6366F1, #818CF8)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/>
              </svg>
            </div>
            <span style={{ color: '#475569', fontSize: '0.82rem' }}>IntelliGrade © 2026 — AI-Powered Academic Assessment Platform. All rights reserved.</span>
          </div>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            {[
              { text: '🌐 Local-Only', color: '#22C55E' },
              { text: '🔒 Secure', color: '#818CF8' },
              { text: '⚡ Real-time', color: '#F59E0B' },
            ].map((b, i) => (
              <span key={i} style={{ fontSize: '0.72rem', padding: '0.2rem 0.6rem', borderRadius: 20, background: `${b.color}15`, color: b.color, border: `1px solid ${b.color}25`, fontWeight: 600 }}>{b.text}</span>
            ))}
          </div>
        </div>
      </footer>

      <style>{`
        @keyframes pulse { 0%,100%{opacity:1}50%{opacity:0.4} }
      `}</style>
    </div>
  );
};
