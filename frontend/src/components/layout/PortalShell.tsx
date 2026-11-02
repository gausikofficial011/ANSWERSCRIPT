import React, { useState } from 'react';
import { Link, Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import {
  ShieldAlert, Layers, BookOpen, Eye, Cpu, UserCheck,
  Shield, Award, BarChart2, Terminal, LogOut, User,
  Menu, ChevronDown, Search, Sun, Moon, Activity,
  Bell, ChevronRight, X
} from 'lucide-react';

interface PortalMeta {
  id: string;
  name: string;
  shortName: string;
  route: string;
  badge: string;
  icon: React.ReactNode;
  description: string;
  color: string;
}

export const PORTALS: PortalMeta[] = [
  { id: 'super_admin',     name: 'Super Admin Control Plane',     shortName: 'Super Admin',    route: '/portals/super-admin',    badge: 'admin',     color: '#EF4444', icon: <ShieldAlert size={16} />, description: 'System health, governance & AI config' },
  { id: 'academic_admin',  name: 'Academic Administration',       shortName: 'Academic Admin', route: '/portals/academic-admin', badge: 'admin',     color: '#F97316', icon: <Layers size={16} />,     description: 'Departments, calendar, enrolments' },
  { id: 'teacher',         name: 'Teacher & Exam Creator',        shortName: 'Teacher',        route: '/portals/teacher',        badge: 'teacher',   color: '#EAB308', icon: <BookOpen size={16} />,   description: 'Exam builder, rubrics, batch upload' },
  { id: 'ocr_review',      name: 'OCR & Document Review Studio',  shortName: 'OCR Studio',     route: '/portals/ocr-review',     badge: 'ocr',       color: '#22C55E', icon: <Eye size={16} />,        description: 'Canvas, bounding boxes, transcripts' },
  { id: 'ai_evaluation',   name: 'AI Evaluation Diagnostics',     shortName: 'AI Evaluation',  route: '/portals/ai-evaluation',  badge: 'eval',      color: '#06B6D4', icon: <Cpu size={16} />,        description: 'Semantic scoring, concept coverage' },
  { id: 'evaluator',       name: 'Teacher Evaluator & Moderator', shortName: 'Evaluator',      route: '/portals/evaluator',      badge: 'eval',      color: '#6366F1', icon: <UserCheck size={16} />,  description: 'Score overrides, moderation' },
  { id: 'integrity',       name: 'Academic Integrity & Collusion',shortName: 'Integrity',      route: '/portals/integrity',      badge: 'integrity', color: '#8B5CF6', icon: <Shield size={16} />,     description: 'Pairwise collusion matrix' },
  { id: 'student',         name: 'Student Academic Results',      shortName: 'Student Hub',    route: '/portals/student',        badge: 'student',   color: '#EC4899', icon: <Award size={16} />,      description: 'Grade cards, feedback, appeals' },
  { id: 'analytics',       name: 'Academic Analytics & QA',       shortName: 'Analytics',      route: '/portals/analytics',      badge: 'analytics', color: '#14B8A6', icon: <BarChart2 size={16} />,  description: 'Distributions, psychometrics' },
  { id: 'research_lab',    name: 'AI Research & Model Lab',       shortName: 'Research Lab',   route: '/portals/research-lab',   badge: 'research',  color: '#84CC16', icon: <Terminal size={16} />,   description: 'Datasets, benchmarks, ML terminal' },
];

export const PortalShell: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [themeDark, setThemeDark] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchFocused, setSearchFocused] = useState(false);
  const [notifOpen, setNotifOpen] = useState(false);

  const activePortal = PORTALS.find(p => location.pathname.startsWith(p.route)) ?? PORTALS[2];

  const toggleTheme = () => {
    setThemeDark(d => !d);
    document.body.classList.toggle('theme-light');
  };

  const handleLogout = async () => { await logout(); navigate('/login'); };

  const GROUP1 = PORTALS.slice(0, 5);
  const GROUP2 = PORTALS.slice(5);

  return (
    <div style={{
      display: 'flex', minHeight: '100vh',
      background: '#070B14', fontFamily: "'Inter', system-ui, sans-serif",
    }}>

      {/* ════════════════════════════════
          SIDEBAR
      ════════════════════════════════ */}
      <aside style={{
        width: sidebarOpen ? 240 : 64,
        minHeight: '100vh',
        background: 'linear-gradient(180deg, #0A1020 0%, #0B1428 100%)',
        borderRight: '1px solid rgba(255,255,255,0.06)',
        display: 'flex', flexDirection: 'column',
        transition: 'width 0.3s cubic-bezier(0.4,0,0.2,1)',
        overflow: 'hidden',
        position: 'sticky', top: 0, height: '100vh',
        flexShrink: 0,
        zIndex: 50,
      }}>

        {/* Brand */}
        <div style={{
          display: 'flex', alignItems: 'center', gap: '0.75rem',
          padding: '1.25rem 1rem', borderBottom: '1px solid rgba(255,255,255,0.05)',
          cursor: 'pointer', flexShrink: 0,
        }} onClick={() => navigate('/')}>
          <div style={{
            width: 36, height: 36, borderRadius: 9, flexShrink: 0,
            background: 'linear-gradient(135deg, #6366F1, #4F46E5)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 0 16px rgba(99,102,241,0.45)',
          }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/>
            </svg>
          </div>
          {sidebarOpen && (
            <div style={{ overflow: 'hidden' }}>
              <div style={{ fontSize: '1.05rem', fontWeight: 800, color: '#F8FAFC', letterSpacing: '-0.02em', whiteSpace: 'nowrap' }}>
                Intelli<span style={{ color: '#818CF8' }}>Grade</span>
              </div>
              <div style={{ fontSize: '0.6rem', color: '#334155', textTransform: 'uppercase', letterSpacing: '0.08em', fontWeight: 600 }}>Academic Intelligence</div>
            </div>
          )}
        </div>

        {/* Nav Groups */}
        <nav style={{ flex: 1, overflowY: 'auto', overflowX: 'hidden', padding: '0.75rem 0', scrollbarWidth: 'none' }}>

          {/* Group 1 — Core Ops */}
          {sidebarOpen && (
            <div style={{ fontSize: '0.62rem', fontWeight: 700, color: '#1E293B', textTransform: 'uppercase', letterSpacing: '0.1em', padding: '0.5rem 1rem 0.3rem', marginTop: '0.25rem' }}>
              Core Operations
            </div>
          )}
          {GROUP1.map(portal => {
            const isActive = location.pathname.startsWith(portal.route);
            return (
              <Link
                key={portal.id}
                to={portal.route}
                style={{
                  display: 'flex', alignItems: 'center', gap: '0.75rem',
                  padding: sidebarOpen ? '0.6rem 1rem' : '0.75rem',
                  justifyContent: sidebarOpen ? 'flex-start' : 'center',
                  color: isActive ? '#F8FAFC' : '#475569',
                  textDecoration: 'none',
                  borderRadius: 9,
                  margin: '0 0.5rem',
                  transition: 'all 0.18s',
                  background: isActive ? `${portal.color}18` : 'transparent',
                  borderLeft: isActive && sidebarOpen ? `2px solid ${portal.color}` : '2px solid transparent',
                  position: 'relative',
                }}
                title={!sidebarOpen ? portal.name : ''}
                onMouseEnter={e => { if (!isActive) { e.currentTarget.style.background = 'rgba(255,255,255,0.04)'; e.currentTarget.style.color = '#94A3B8'; } }}
                onMouseLeave={e => { if (!isActive) { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = '#475569'; } }}
              >
                <div style={{ color: isActive ? portal.color : 'inherit', flexShrink: 0 }}>{portal.icon}</div>
                {sidebarOpen && (
                  <span style={{ fontSize: '0.82rem', fontWeight: isActive ? 700 : 500, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {portal.shortName}
                  </span>
                )}
                {isActive && sidebarOpen && (
                  <div style={{ marginLeft: 'auto', width: 5, height: 5, borderRadius: '50%', background: portal.color, flexShrink: 0, boxShadow: `0 0 6px ${portal.color}` }} />
                )}
              </Link>
            );
          })}

          {/* Group 2 — Analysis */}
          {sidebarOpen && (
            <div style={{ fontSize: '0.62rem', fontWeight: 700, color: '#1E293B', textTransform: 'uppercase', letterSpacing: '0.1em', padding: '0.75rem 1rem 0.3rem', marginTop: '0.5rem' }}>
              Analysis & Research
            </div>
          )}
          {!sidebarOpen && <div style={{ height: 12 }} />}
          {GROUP2.map(portal => {
            const isActive = location.pathname.startsWith(portal.route);
            return (
              <Link
                key={portal.id}
                to={portal.route}
                style={{
                  display: 'flex', alignItems: 'center', gap: '0.75rem',
                  padding: sidebarOpen ? '0.6rem 1rem' : '0.75rem',
                  justifyContent: sidebarOpen ? 'flex-start' : 'center',
                  color: isActive ? '#F8FAFC' : '#475569',
                  textDecoration: 'none',
                  borderRadius: 9,
                  margin: '0 0.5rem',
                  transition: 'all 0.18s',
                  background: isActive ? `${portal.color}18` : 'transparent',
                  borderLeft: isActive && sidebarOpen ? `2px solid ${portal.color}` : '2px solid transparent',
                }}
                title={!sidebarOpen ? portal.name : ''}
                onMouseEnter={e => { if (!isActive) { e.currentTarget.style.background = 'rgba(255,255,255,0.04)'; e.currentTarget.style.color = '#94A3B8'; } }}
                onMouseLeave={e => { if (!isActive) { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = '#475569'; } }}
              >
                <div style={{ color: isActive ? portal.color : 'inherit', flexShrink: 0 }}>{portal.icon}</div>
                {sidebarOpen && (
                  <span style={{ fontSize: '0.82rem', fontWeight: isActive ? 700 : 500, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {portal.shortName}
                  </span>
                )}
                {isActive && sidebarOpen && (
                  <div style={{ marginLeft: 'auto', width: 5, height: 5, borderRadius: '50%', background: portal.color, flexShrink: 0, boxShadow: `0 0 6px ${portal.color}` }} />
                )}
              </Link>
            );
          })}
        </nav>

        {/* Sidebar Footer */}
        <div style={{ padding: '0.75rem', borderTop: '1px solid rgba(255,255,255,0.05)', flexShrink: 0 }}>
          {/* Online Indicator */}
          {sidebarOpen && (
            <div style={{
              display: 'flex', alignItems: 'center', gap: '0.5rem',
              padding: '0.5rem 0.75rem', borderRadius: 8,
              background: 'rgba(21,128,61,0.1)', border: '1px solid rgba(21,128,61,0.2)',
              marginBottom: '0.5rem',
            }}>
              <div style={{ width: 7, height: 7, borderRadius: '50%', background: '#22C55E', animation: 'pulse 2s infinite', boxShadow: '0 0 6px rgba(34,197,94,0.7)' }} />
              <span style={{ fontSize: '0.7rem', color: '#4ADE80', fontWeight: 600 }}>Local Mode — Online</span>
            </div>
          )}
          {/* User Row */}
          {sidebarOpen ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', padding: '0.5rem 0.75rem' }}>
              <div style={{
                width: 30, height: 30, borderRadius: '50%', flexShrink: 0,
                background: 'linear-gradient(135deg, #6366F1, #4F46E5)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <User size={15} color="#fff" />
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#E2E8F0', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {user?.full_name || user?.username || 'Faculty User'}
                </div>
                <div style={{ fontSize: '0.65rem', color: '#475569', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  {user?.role || 'Authenticated'}
                </div>
              </div>
              <button onClick={handleLogout} title="Sign Out" style={{
                background: 'none', border: 'none', cursor: 'pointer',
                color: '#334155', padding: '0.25rem', borderRadius: 6, transition: 'color 0.18s',
              }}
                onMouseEnter={e => e.currentTarget.style.color = '#EF4444'}
                onMouseLeave={e => e.currentTarget.style.color = '#334155'}
              >
                <LogOut size={15} />
              </button>
            </div>
          ) : (
            <button onClick={handleLogout} title="Sign Out" style={{
              width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center',
              padding: '0.6rem', borderRadius: 8, background: 'none', border: 'none',
              cursor: 'pointer', color: '#334155', transition: 'all 0.18s',
            }}
              onMouseEnter={e => { e.currentTarget.style.background = 'rgba(239,68,68,0.1)'; e.currentTarget.style.color = '#EF4444'; }}
              onMouseLeave={e => { e.currentTarget.style.background = 'none'; e.currentTarget.style.color = '#334155'; }}
            >
              <LogOut size={16} />
            </button>
          )}
        </div>
      </aside>

      {/* ════════════════════════════════
          MAIN AREA
      ════════════════════════════════ */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0, overflow: 'hidden' }}>

        {/* ── TOP HEADER BAR ── */}
        <header style={{
          height: 58,
          background: 'rgba(10,16,32,0.95)',
          backdropFilter: 'blur(20px)',
          borderBottom: '1px solid rgba(255,255,255,0.06)',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          padding: '0 1.75rem', gap: '1rem',
          position: 'sticky', top: 0, zIndex: 40, flexShrink: 0,
        }}>
          {/* Left: Toggle + Breadcrumb */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
            <button
              onClick={() => setSidebarOpen(o => !o)}
              style={{
                width: 32, height: 32, border: 'none', borderRadius: 8,
                background: 'rgba(255,255,255,0.05)', color: '#64748B',
                cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center',
                transition: 'all 0.2s',
              }}
              onMouseEnter={e => { e.currentTarget.style.background = 'rgba(99,102,241,0.15)'; e.currentTarget.style.color = '#818CF8'; }}
              onMouseLeave={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.05)'; e.currentTarget.style.color = '#64748B'; }}
            >
              <Menu size={16} />
            </button>

            {/* Breadcrumb */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.8rem' }}>
              <span style={{ color: '#334155', cursor: 'pointer' }} onClick={() => navigate('/')}>AMAES</span>
              <ChevronRight size={12} color="#1E293B" />
              <span style={{ color: '#334155' }}>Portals</span>
              <ChevronRight size={12} color="#1E293B" />
              <span style={{ color: activePortal.color, fontWeight: 700 }}>{activePortal.shortName}</span>
            </div>
          </div>

          {/* Center: Portal indicator */}
          <div style={{
            display: 'flex', alignItems: 'center', gap: '0.5rem',
            padding: '0.3rem 0.85rem', borderRadius: 100,
            background: `${activePortal.color}12`,
            border: `1px solid ${activePortal.color}30`,
          }}>
            <div style={{ color: activePortal.color, display: 'flex', alignItems: 'center' }}>{activePortal.icon}</div>
            <span style={{ fontSize: '0.75rem', fontWeight: 700, color: activePortal.color }}>
              {activePortal.shortName}
            </span>
          </div>

          {/* Right: Search + Status + Theme + Notif + User */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>

            {/* Search */}
            <div style={{
              display: 'flex', alignItems: 'center', gap: '0.5rem',
              padding: '0.4rem 0.85rem',
              background: searchFocused ? 'rgba(99,102,241,0.08)' : 'rgba(255,255,255,0.04)',
              border: `1px solid ${searchFocused ? 'rgba(99,102,241,0.4)' : 'rgba(255,255,255,0.08)'}`,
              borderRadius: 9, transition: 'all 0.2s', width: 220,
            }}>
              <Search size={14} color="#334155" />
              <input
                type="text"
                placeholder="Search..."
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                onFocus={() => setSearchFocused(true)}
                onBlur={() => setSearchFocused(false)}
                style={{
                  background: 'none', border: 'none', outline: 'none',
                  fontSize: '0.82rem', color: '#F8FAFC', width: '100%',
                  fontFamily: 'inherit',
                }}
              />
            </div>

            {/* Celery Status */}
            <div style={{
              display: 'flex', alignItems: 'center', gap: '0.4rem',
              padding: '0.3rem 0.75rem', borderRadius: 100,
              background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.25)',
              fontSize: '0.72rem', color: '#A5B4FC', fontWeight: 600,
            }}>
              <Activity size={12} style={{ animation: 'spin 2s linear infinite' }} />
              Celery: 6 Ready
            </div>

            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              style={{
                width: 32, height: 32, borderRadius: 8,
                background: 'rgba(255,255,255,0.05)',
                border: '1px solid rgba(255,255,255,0.08)',
                color: '#64748B', cursor: 'pointer',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                transition: 'all 0.2s',
              }}
              onMouseEnter={e => e.currentTarget.style.color = '#94A3B8'}
              onMouseLeave={e => e.currentTarget.style.color = '#64748B'}
            >
              {themeDark ? <Sun size={15} /> : <Moon size={15} />}
            </button>

            {/* Notifications */}
            <div style={{ position: 'relative' }}>
              <button
                onClick={() => setNotifOpen(o => !o)}
                style={{
                  width: 32, height: 32, borderRadius: 8,
                  background: 'rgba(255,255,255,0.05)',
                  border: '1px solid rgba(255,255,255,0.08)',
                  color: '#64748B', cursor: 'pointer',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  transition: 'all 0.2s', position: 'relative',
                }}
              >
                <Bell size={15} />
                <div style={{ position: 'absolute', top: 6, right: 6, width: 7, height: 7, borderRadius: '50%', background: '#EF4444', boxShadow: '0 0 6px rgba(239,68,68,0.7)' }} />
              </button>
              {notifOpen && (
                <div style={{
                  position: 'absolute', right: 0, top: '110%', width: 300, zIndex: 100,
                  background: '#0A1020', border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: 12, overflow: 'hidden',
                  boxShadow: '0 20px 40px rgba(0,0,0,0.5)',
                }}>
                  <div style={{ padding: '0.85rem 1rem', borderBottom: '1px solid rgba(255,255,255,0.06)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontWeight: 700, color: '#E2E8F0', fontSize: '0.85rem' }}>Notifications</span>
                    <button onClick={() => setNotifOpen(false)} style={{ background: 'none', border: 'none', color: '#475569', cursor: 'pointer' }}><X size={14} /></button>
                  </div>
                  {[
                    { icon: '✅', text: 'MCA301 batch AI evaluation complete. 42 scripts scored.', time: '5m ago', color: '#22C55E' },
                    { icon: '⚠️', text: '2 high-similarity pairs flagged by Integrity module.', time: '12m ago', color: '#F59E0B' },
                    { icon: '📄', text: 'OCR job Q#47-B completed. 6 low-confidence boxes queued for review.', time: '28m ago', color: '#06B6D4' },
                  ].map((n, i) => (
                    <div key={i} style={{ padding: '0.75rem 1rem', borderBottom: '1px solid rgba(255,255,255,0.04)', display: 'flex', gap: '0.75rem', cursor: 'pointer', transition: 'background 0.15s' }}
                      onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,255,255,0.03)'}
                      onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                    >
                      <span style={{ fontSize: '1rem', flexShrink: 0 }}>{n.icon}</span>
                      <div>
                        <p style={{ fontSize: '0.78rem', color: '#94A3B8', lineHeight: 1.45, margin: 0 }}>{n.text}</p>
                        <span style={{ fontSize: '0.68rem', color: '#334155', marginTop: 2, display: 'block' }}>{n.time}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* User Pill */}
            <div style={{
              display: 'flex', alignItems: 'center', gap: '0.55rem',
              padding: '0.3rem 0.75rem 0.3rem 0.4rem',
              background: 'rgba(255,255,255,0.04)',
              border: '1px solid rgba(255,255,255,0.08)',
              borderRadius: 100,
              cursor: 'default',
            }}>
              <div style={{
                width: 26, height: 26, borderRadius: '50%',
                background: 'linear-gradient(135deg, #6366F1, #4F46E5)',
                display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
              }}>
                <User size={13} color="#fff" />
              </div>
              <div>
                <div style={{ fontSize: '0.78rem', fontWeight: 700, color: '#E2E8F0', lineHeight: 1 }}>
                  {user?.full_name?.split(' ')[0] || user?.username || 'User'}
                </div>
                <div style={{ fontSize: '0.6rem', color: '#334155', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  {user?.role || 'Auth'}
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* ── PAGE CONTENT ── */}
        <main style={{
          flex: 1, overflowY: 'auto', overflowX: 'hidden',
          padding: '1.75rem 2rem',
          scrollbarWidth: 'thin',
          scrollbarColor: 'rgba(99,102,241,0.3) transparent',
        }}>
          <Outlet />
        </main>
      </div>

      <style>{`
        @keyframes pulse { 0%,100%{opacity:1;box-shadow:0 0 6px rgba(34,197,94,0.7)}50%{opacity:0.6;box-shadow:0 0 12px rgba(34,197,94,0.3)} }
        @keyframes spin { to { transform: rotate(360deg); } }
        * { box-sizing: border-box; }
        ::-webkit-scrollbar { width: 5px; height: 5px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: rgba(99,102,241,0.4); }
      `}</style>
    </div>
  );
};
