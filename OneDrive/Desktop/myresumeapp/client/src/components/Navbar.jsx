import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { LayoutDashboard, LogOut, User, FileText, ToggleLeft, ToggleRight } from 'lucide-react';

const Navbar = ({ user, onLogout, onLogin }) => {
  const navigate = useNavigate();

  const handleLogout = () => {
    onLogout();
    navigate('/');
  };

  const devLogin = (role) => {
    const userData = {
      user: {
        name: role === 'admin' ? 'Admin User' : 'Student User',
        email: role === 'admin' ? 'admin@example.com' : 'student@example.com',
        role: role,
        _id: role === 'admin' ? 'dummy_admin_id' : 'dummy_student_id' // Will not be used by backend since we bypass
      },
      token: role === 'admin' ? 'dev-token-admin' : 'dev-token-student'
    };
    onLogin(userData);
    navigate(role === 'admin' ? '/admin-dashboard' : '/student-dashboard');
  };

  return (
    <nav className="border-b border-white/10 bg-dark/50 backdrop-blur-md sticky top-0 z-50">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2">
          <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center neon-glow">
            <FileText className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-bold gradient-text">ResumeAI</span>
        </Link>

        <div className="flex items-center gap-6">
          {/* DEV SWITCH */}
          <div className="flex bg-white/5 rounded-lg p-1 border border-white/10">
            <button
              onClick={() => devLogin('student')}
              className={`px-3 py-1 text-xs rounded-md transition-all ${user?.role === 'student' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'}`}
            >
              Student
            </button>
            <button
              onClick={() => devLogin('admin')}
              className={`px-3 py-1 text-xs rounded-md transition-all ${user?.role === 'admin' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'}`}
            >
              Admin
            </button>
          </div>

          {user ? (
            <>
              <Link
                to={user.role === 'admin' ? '/admin-dashboard' : '/student-dashboard'}
                className="flex items-center gap-2 text-slate-300 hover:text-white transition-colors"
              >
                <LayoutDashboard className="w-4 h-4" />
                <span>Dashboard</span>
              </Link>
              <div className="flex items-center gap-2 px-3 py-1 bg-white/5 rounded-full border border-white/10">
                <User className="w-4 h-4 text-indigo-400" />
                <span className="text-sm font-medium">{user.name}</span>
              </div>
              <button
                onClick={handleLogout}
                className="p-2 text-slate-400 hover:text-red-400 transition-colors"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </>
          ) : (
            <div className="flex items-center gap-4">
              <Link to="/login" className="text-slate-300 hover:text-white transition-colors">Login</Link>
              <Link to="/register" className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition-all transform hover:scale-105 active:scale-95 neon-glow">
                Get Started
              </Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
