import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { Mail, Lock, User as UserIcon } from 'lucide-react';

const Login = ({ onLogin }) => {
    const [formData, setFormData] = useState({ email: '', password: '' });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        try {
            const { data } = await axios.post('http://localhost:5000/api/auth/login', formData);
            onLogin(data);
            navigate(data.user.role === 'admin' ? '/admin-dashboard' : '/student-dashboard');
        } catch (err) {
            setError(err.response?.data?.error || 'Login failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex items-center justify-center min-h-[80vh]">
            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="glass-card p-10 w-full max-w-md"
            >
                <h2 className="text-3xl font-bold mb-8 text-center">Welcome Back</h2>
                {error && <div className="bg-red-500/10 border border-red-500/20 text-red-500 p-3 rounded-lg mb-6 text-sm">{error}</div>}
                <form onSubmit={handleSubmit} className="space-y-6">
                    <div>
                        <label className="block text-sm font-medium text-slate-400 mb-2">Email Address</label>
                        <div className="relative">
                            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                            <input
                                type="email"
                                required
                                className="w-full bg-white/5 border border-white/10 rounded-xl py-3 pl-11 pr-4 focus:ring-2 focus:ring-indigo-500 outline-none transition-all"
                                placeholder="name@example.com"
                                value={formData.email}
                                onChange={e => setFormData({ ...formData, email: e.target.value })}
                            />
                        </div>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-slate-400 mb-2">Password</label>
                        <div className="relative">
                            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                            <input
                                type="password"
                                required
                                className="w-full bg-white/5 border border-white/10 rounded-xl py-3 pl-11 pr-4 focus:ring-2 focus:ring-indigo-500 outline-none transition-all"
                                placeholder="••••••••"
                                value={formData.password}
                                onChange={e => setFormData({ ...formData, password: e.target.value })}
                            />
                        </div>
                    </div>
                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full py-4 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white rounded-xl font-bold transition-all transform hover:scale-[1.02] active:scale-95 neon-glow"
                    >
                        {loading ? 'Signing in...' : 'Sign In'}
                    </button>
                </form>
                <div className="mt-6 grid grid-cols-2 gap-4">
                    <button
                        type="button"
                        onClick={() => setFormData({ email: 'student@example.com', password: 'password123' })}
                        className="text-xs py-2 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition-colors text-slate-400"
                    >
                        Fill Student Demo
                    </button>
                    <button
                        type="button"
                        onClick={() => setFormData({ email: 'admin@example.com', password: 'password123' })}
                        className="text-xs py-2 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition-colors text-slate-400"
                    >
                        Fill Admin Demo
                    </button>
                </div>
                <p className="mt-8 text-center text-slate-400">
                    Don't have an account? <Link to="/register" className="text-indigo-400 hover:text-indigo-300 font-medium">Create one</Link>
                </p>
            </motion.div>
        </div>
    );
};

export default Login;
