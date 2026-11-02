import React from 'react';
import { Link, Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { BookOpen, Users, ClipboardCheck, AlertTriangle, LogOut, User, Menu, GraduationCap } from 'lucide-react';

export const DashboardLayout: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = React.useState(true);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  interface NavItem {
    label: string;
    path: string;
    icon: React.ReactNode;
    disabled?: boolean;
  }

  const mainNavItems: NavItem[] = [
    { label: 'Dashboard', path: '/dashboard', icon: <ClipboardCheck size={20} /> },
    { label: 'Results & Review', path: '/results', icon: <GraduationCap size={20} /> },
    { label: 'Plagiarism Alerts', path: '/plagiarism', icon: <AlertTriangle size={20} /> },
  ];

  const adminNavItems: NavItem[] = [
    { label: 'Subjects & Exams', path: '/subjects', icon: <BookOpen size={20} /> },
    { label: 'Student Directory', path: '/students', icon: <Users size={20} /> },
  ];

  return (
    <div className="layout-container">
      {/* Sidebar Navigation */}
      <aside className={`sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-brand">
          <ClipboardCheck size={28} className="brand-icon" />
          <span className="brand-text">AI Evaluation</span>
        </div>
        <nav className="sidebar-nav">
          {sidebarOpen && <div className="nav-section-title">Evaluation System</div>}
          {mainNavItems.map((item, idx) => {
            const isActive = location.pathname.startsWith(item.path);
            return (
              <Link
                key={idx}
                to={item.path}
                className={`nav-item ${isActive ? 'active' : ''}`}
              >
                {item.icon}
                <span>{sidebarOpen ? item.label : ''}</span>
              </Link>
            );
          })}
          
          {sidebarOpen && <div className="nav-section-title">Administration</div>}
          {adminNavItems.map((item, idx) => {
            const isActive = location.pathname.startsWith(item.path);
            return (
              <Link
                key={idx}
                to={item.path}
                className={`nav-item ${isActive ? 'active' : ''}`}
              >
                {item.icon}
                <span>{sidebarOpen ? item.label : ''}</span>
              </Link>
            );
          })}
        </nav>
        <div className="sidebar-footer">
          <button className="nav-item btn-logout" onClick={handleLogout}>
            <LogOut size={20} />
            <span>{sidebarOpen ? 'Logout' : ''}</span>
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="main-area">
        {/* Header */}
        <header className="header">
          <button className="btn-toggle" onClick={() => setSidebarOpen(!sidebarOpen)} title="Toggle Sidebar" aria-label="Toggle Sidebar">
            <Menu size={20} />
          </button>
          
          <div className="header-user">
            <div className="user-icon">
              <User size={18} />
            </div>
            <div className="user-info">
              <span className="user-name">{user?.full_name || user?.username}</span>
              <span className="user-role">{user?.role}</span>
            </div>
          </div>
        </header>

        {/* Dynamic Nested View Router Outlet */}
        <main className="content-viewport">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
