import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import './InstitutionalLogin.css';

interface RoleWorkspace {
  id: string;
  name: string;
  icon: string;
  email: string;
  defaultPass: string;
  targetRoute: string;
  description: string;
}

const ROLE_WORKSPACES: RoleWorkspace[] = [
  {
    id: 'super_admin',
    name: '1. Super Admin',
    icon: '🛡️',
    email: 'superadmin@amaes.edu',
    defaultPass: 'Admin@1234',
    targetRoute: '/portals/super-admin',
    description: 'Platform health, user governance & model approvals',
  },
  {
    id: 'academic_admin',
    name: '2. Academic Admin',
    icon: '🏛️',
    email: 'academic_admin@amaes.edu',
    defaultPass: 'Admin@1234',
    targetRoute: '/portals/academic-admin',
    description: 'Departments, calendar, enrolment & publication',
  },
  {
    id: 'teacher',
    name: '3. Teacher Creator',
    icon: '📚',
    email: 'teacher@amaes.edu',
    defaultPass: 'Teacher@1234',
    targetRoute: '/portals/teacher',
    description: 'Exam authoring, rubrics & model answers',
  },
  {
    id: 'ocr_review',
    name: '4. OCR Reviewer',
    icon: '👁️',
    email: 'ocr@amaes.edu',
    defaultPass: 'Teacher@1234',
    targetRoute: '/portals/ocr-review',
    description: 'Split-screen canvas, bounding boxes & transcripts',
  },
  {
    id: 'ai_evaluation',
    name: '5. AI Evaluation',
    icon: '🤖',
    email: 'ai_eval@amaes.edu',
    defaultPass: 'Teacher@1234',
    targetRoute: '/portals/ai-evaluation',
    description: 'Semantic scoring, concept coverage & evidence spans',
  },
  {
    id: 'evaluator',
    name: '6. Evaluator Moderator',
    icon: '✍️',
    email: 'evaluator@amaes.edu',
    defaultPass: 'Teacher@1234',
    targetRoute: '/portals/evaluator',
    description: 'Side-by-side script review & moderation',
  },
  {
    id: 'integrity',
    name: '7. Academic Integrity',
    icon: '⚖️',
    email: 'integrity@amaes.edu',
    defaultPass: 'Admin@1234',
    targetRoute: '/portals/integrity',
    description: 'Pairwise collusion matrix & similarity analysis',
  },
  {
    id: 'student',
    name: '8. Student Portal',
    icon: '🎓',
    email: 'student@amaes.edu',
    defaultPass: 'Student@1234',
    targetRoute: '/portals/student',
    description: 'Arjun Kumar: Grade cards & feedback',
  },
  {
    id: 'analytics',
    name: '9. Analytics & QA',
    icon: '📊',
    email: 'analytics@amaes.edu',
    defaultPass: 'Admin@1234',
    targetRoute: '/portals/analytics',
    description: 'Score distribution, difficulty index & psychometrics',
  },
  {
    id: 'research_lab',
    name: '10. AI Research Lab',
    icon: '🧪',
    email: 'research@amaes.edu',
    defaultPass: 'Admin@1234',
    targetRoute: '/portals/research-lab',
    description: 'Model fine-tuning, hardware telemetry & benchmark suites',
  },
];

export const Login: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();

  // Active form state
  const [selectedInstitution, setSelectedInstitution] = useState('Amrita Vishwa Vidyapeetham (AMAES)');
  const [selectedWorkspace, setSelectedWorkspace] = useState<RoleWorkspace>(ROLE_WORKSPACES[2]); // Default Teacher Creator
  const [email, setEmail] = useState(ROLE_WORKSPACES[2].email);
  const [password, setPassword] = useState(ROLE_WORKSPACES[2].defaultPass);
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [activeTab, setActiveTab] = useState<'login' | 'signup'>('login');

  const handleSelectWorkspace = (ws: RoleWorkspace) => {
    setSelectedWorkspace(ws);
    setEmail(ws.email);
    setPassword(ws.defaultPass);
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Please provide your institutional email and password.');
      return;
    }

    setError(null);
    setIsSubmitting(true);

    try {
      await login(email, password);
      // Navigate to the role's assigned portal workspace
      navigate(selectedWorkspace.targetRoute);
    } catch (err: unknown) {
      const errorMsg =
        err && typeof err === 'object' && 'response' in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : null;
      setError(errorMsg || 'Authentication failed. Please verify institutional credentials.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="ig-login-page">
      {/* ─────────────────────────────────────────────────────────────
          LEFT PANEL: EDITORIAL INSTITUTIONAL BRANDING & SHOWCASE
      ───────────────────────────────────────────────────────────── */}
      <section className="ig-hero-pane">
        {/* Brand Lockup */}
        <div className="ig-brand-row">
          <div className="ig-logo-lockup">
            <div className="ig-logo-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M22 10v6M2 10l10-5 10 5-10 5z"/>
                <path d="M6 12v5c3 3 9 3 12 0v-5"/>
              </svg>
            </div>
            <div className="ig-brand-text">
              <h2>Intelli<span>Grade</span></h2>
              <p>AI-Powered Academic Assessment Platform</p>
            </div>
          </div>

          <div className="ig-trusted-badge">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#60A5FA" strokeWidth="2.5">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            </svg>
            <span>Trusted by Educational Institutions</span>
          </div>
        </div>

        {/* Hero Title & Features */}
        <div className="ig-hero-content">
          <div className="ig-eyebrow">
            FAIR • ACCURATE • TRANSPARENT • AI-POWERED
          </div>

          <h1 className="ig-hero-headline">
            Empowering Educational<br />
            Institutions with <span className="ai-glow">AI</span>
          </h1>

          <p className="ig-hero-subtext">
            Digitize, evaluate, and manage academic assessments with advanced AI — all in one secure platform for your institution.
          </p>

          <div className="ig-features-list">
            <div className="ig-feature-item">
              <div className="ig-feature-icon-box purple">
                📄
              </div>
              <div className="ig-feature-text">
                <h4>Automated Evaluation</h4>
                <p>OCR, AI grading and detailed analytics</p>
              </div>
            </div>

            <div className="ig-feature-item">
              <div className="ig-feature-icon-box blue">
                🛡️
              </div>
              <div className="ig-feature-text">
                <h4>Academic Integrity</h4>
                <p>Plagiarism and collusion detection</p>
              </div>
            </div>

            <div className="ig-feature-item">
              <div className="ig-feature-icon-box green">
                📊
              </div>
              <div className="ig-feature-text">
                <h4>Institution Management</h4>
                <p>Departments, faculty, students and more</p>
              </div>
            </div>

            <div className="ig-feature-item">
              <div className="ig-feature-icon-box orange">
                🎓
              </div>
              <div className="ig-feature-text">
                <h4>Transparent Results</h4>
                <p>Detailed feedback and performance insights</p>
              </div>
            </div>
          </div>
        </div>

        {/* Campus Photo Card */}
        <div className="ig-campus-card">
          <img 
            src="/campus_university_night.jpg" 
            alt="University Campus Architecture" 
            className="ig-campus-img"
          />
          <div className="ig-campus-script">
            Education with Integrity for a Brighter Tomorrow
          </div>
        </div>

        {/* Stats Bar */}
        <div className="ig-stats-bar">
          <div className="ig-stat-col">
            <span className="ig-stat-icon">🏛️</span>
            <div className="ig-stat-meta">
              <div className="stat-val">100+</div>
              <div className="stat-lbl">Institutions</div>
            </div>
          </div>

          <div className="ig-stat-col">
            <span className="ig-stat-icon">👥</span>
            <div className="ig-stat-meta">
              <div className="stat-val">1M+</div>
              <div className="stat-lbl">Students</div>
            </div>
          </div>

          <div className="ig-stat-col">
            <span className="ig-stat-icon">📖</span>
            <div className="ig-stat-meta">
              <div className="stat-val">50K+</div>
              <div className="stat-lbl">Exams Processed</div>
            </div>
          </div>

          <div className="ig-stat-col">
            <span className="ig-stat-icon">🟢</span>
            <div className="ig-stat-meta">
              <div className="stat-val">99.9%</div>
              <div className="stat-lbl">Uptime</div>
            </div>
          </div>
        </div>

        {/* Footer Quote & Badges */}
        <div className="ig-hero-footer">
          <div className="ig-tagline-quote">
            “Transforming education through responsible and accessible AI.”
          </div>

          <div className="ig-trust-badges">
            <span className="ig-trust-badge">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="2" y1="12" x2="22" y2="12"></line>
                <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
              </svg>
              100% Local Deployment
            </span>
            <span className="ig-trust-badge">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M18 10h-1.26A8 8 0 1 0 9 20h9a5 5 0 0 0 0-10z"></path>
              </svg>
              No Cloud API Costs
            </span>
            <span className="ig-trust-badge">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
              </svg>
              Secure & Private
            </span>
            <span className="ig-trust-badge">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
              </svg>
              Free to Use Forever
            </span>
          </div>
        </div>
      </section>

      {/* ─────────────────────────────────────────────────────────────
          RIGHT PANEL: AUTHENTIC INSTITUTIONAL LOGIN FORM
      ───────────────────────────────────────────────────────────── */}
      <section className="ig-form-pane">
        <div className="ig-form-pane-inner">
          {/* Top English Selector */}
          <div className="ig-lang-row">
            <button type="button" className="ig-lang-select">
              <span>🌐</span> English ⌄
            </button>
          </div>

          {/* Centered Logo in Card */}
          <div className="ig-right-brand">
            <div className="ig-right-logo-box">
              <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M22 10v6M2 10l10-5 10 5-10 5z"/>
                <path d="M6 12v5c3 3 9 3 12 0v-5"/>
              </svg>
            </div>
            <h3>Intelli<span>Grade</span></h3>
            <p>AI-Powered Academic Assessment Platform</p>
          </div>

          {/* Tab Selector: Login | Sign Up */}
          <div className="ig-tabs-pill">
            <button 
              type="button" 
              className={`ig-tab-btn ${activeTab === 'login' ? 'active' : ''}`}
              onClick={() => setActiveTab('login')}
            >
              Login
            </button>
            <button 
              type="button" 
              className={`ig-tab-btn ${activeTab === 'signup' ? 'active' : ''}`}
              onClick={() => setActiveTab('signup')}
            >
              Sign Up
            </button>
          </div>

          {/* Heading */}
          <div className="ig-welcome-header">
            <h2>Welcome Back</h2>
            <p>Sign in to your institutional account</p>
          </div>

          {error && (
            <div style={{ background: '#FEE2E2', border: '1px solid #FCA5A5', color: '#991B1B', borderRadius: 8, padding: '0.65rem 0.85rem', fontSize: '0.82rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span>⚠️</span>
              <span>{error}</span>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {/* Institution Dropdown */}
            <div className="ig-form-group">
              <label htmlFor="inst-select">Institution</label>
              <div className="ig-input-box">
                <span className="ig-input-icon">🏛️</span>
                <select
                  id="inst-select"
                  value={selectedInstitution}
                  onChange={(e) => setSelectedInstitution(e.target.value)}
                >
                  <option value="Amrita Vishwa Vidyapeetham (AMAES)">Amrita Vishwa Vidyapeetham (AMAES)</option>
                  <option value="Indian Institute of Technology Delhi (IITD)">Indian Institute of Technology Delhi (IITD)</option>
                  <option value="Stanford University">Stanford University</option>
                  <option value="Massachusetts Institute of Technology (MIT)">Massachusetts Institute of Technology (MIT)</option>
                  <option value="University of Cambridge">University of Cambridge</option>
                </select>
              </div>
            </div>

            {/* Portal Workspace Quick-Selector */}
            <div className="ig-workspace-picker-box">
              <div className="ig-workspace-header">
                <span>Select Target Portal Workspace</span>
                <span style={{ fontSize: '0.68rem', color: '#4F46E5', fontWeight: 700 }}>
                  Dest: {selectedWorkspace.targetRoute}
                </span>
              </div>
              <div className="ig-workspace-grid">
                {ROLE_WORKSPACES.map((ws) => {
                  const isCurrent = ws.id === selectedWorkspace.id;
                  return (
                    <button
                      key={ws.id}
                      type="button"
                      id={`ws-btn-${ws.id}`}
                      className={`ig-role-pill ${isCurrent ? 'active' : ''}`}
                      onClick={() => handleSelectWorkspace(ws)}
                      title={ws.description}
                    >
                      <span className="role-icon">{ws.icon}</span>
                      <span>{ws.name}</span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Email Address */}
            <div className="ig-form-group">
              <label htmlFor="email-input">Email Address</label>
              <div className="ig-input-box">
                <span className="ig-input-icon">✉️</span>
                <input
                  id="email-input"
                  type="email"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
            </div>

            {/* Password */}
            <div className="ig-form-group">
              <div className="ig-form-label-row">
                <label htmlFor="pass-input">Password</label>
                <a href="#forgot" onClick={(e) => { e.preventDefault(); alert('Password reset link sent to your institutional administrator.'); }} className="ig-forgot-link">
                  Forgot Password?
                </a>
              </div>
              <div className="ig-input-box">
                <span className="ig-input-icon">🔒</span>
                <input
                  id="pass-input"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
                <button
                  type="button"
                  className="ig-eye-toggle"
                  onClick={() => setShowPassword(!showPassword)}
                  title={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? '👁️' : '👁️‍🗨️'}
                </button>
              </div>
            </div>

            {/* Remember Me */}
            <div className="ig-remember-row">
              <input
                id="remember-check"
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
              />
              <label htmlFor="remember-check">Remember me</label>
            </div>

            {/* Submit Button */}
            <button
              id="signin-btn-submit"
              type="submit"
              className="ig-btn-signin"
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <span className="spinner-border spinner-border-sm" style={{ width: 16, height: 16, borderWidth: 2 }} />
                  <span>Authenticating & Routing...</span>
                </>
              ) : (
                <>
                  <span>Sign In</span>
                  <span>→</span>
                </>
              )}
            </button>

            {/* OR Divider */}
            <div className="ig-divider">
              <span>OR</span>
            </div>

            {/* Google Institutional Button */}
            <button
              id="google-signin-btn"
              type="button"
              className="ig-btn-google"
              onClick={() => {
                // Instant demo single sign-on using the selected workspace
                handleSubmit({ preventDefault: () => {} } as React.FormEvent);
              }}
            >
              <svg width="18" height="18" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.665-5.17 3.665-9.17z"/>
                <path fill="#34A853" d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.33 24 12 24z"/>
                <path fill="#FBBC05" d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.18 0 9.99 0 12s.45 3.82 1.25 5.42l4.03-3.15z"/>
                <path fill="#EA4335" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.33 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z"/>
              </svg>
              <span>Sign in with Google (Institutional)</span>
            </button>
          </form>

          {/* Bottom Card */}
          <div className="ig-register-box">
            <div className="ig-register-text">
              <p>Don't have an account?</p>
              <span>Register your institution to get started with IntelliGrade.</span>
            </div>
            <button
              type="button"
              className="ig-btn-create-inst"
              onClick={() => alert('Institutional Onboarding Portal: Contact enterprise-support@intelligrade.edu for campus domain registration.')}
            >
              Create Institution Account
            </button>
          </div>
        </div>
      </section>
    </div>
  );
};
