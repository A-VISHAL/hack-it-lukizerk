import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { Mail, Lock, User as UserIcon, ShieldCheck } from 'lucide-react';

const Register = ({ onLogin }) => {
    const [formData, setFormData] = useState({ name: '', email: '', password: '', role: 'student' });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        try {
            const { data } = await axios.post('http://localhost:5000/api/auth/register', formData);
            onLogin(data);
            navigate(data.user.role === 'admin' ? '/admin-dashboard' : '/student-dashboard');
        } catch (err) {
            setError(err.response?.data?.error || 'Registration failed');
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
                <h2 className="text-3xl font-bold mb-8 text-center text-white">Create Account</h2>
                {error && <div className="bg-red-500/10 border border-red-500/20 text-red-500 p-3 rounded-lg mb-6 text-sm">{error}</div>}
                <form onSubmit={handleSubmit} className="space-y-5">
                    <div>
                        <label className="block text-sm font-medium text-slate-400 mb-2">Full Name</label>
                        <div className="relative">
                            <UserIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                            <input
                                type="text"
                                required
                                className="w-full bg-white/5 border border-white/10 rounded-xl py-3 pl-11 pr-4 focus:ring-2 focus:ring-indigo-500 outline-none transition-all"
                                placeholder="John Doe"
                                value={formData.name}
                                onChange={e => setFormData({ ...formData, name: e.target.value })}
                            />
                        </div>
                    </div>
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
                    <div>
                        <label className="block text-sm font-medium text-slate-400 mb-2">Role</label>
                        <div className="flex gap-4">
                            {['student', 'admin'].map(role => (
                                <button
                                    key={role}
                                    type="button"
                                    onClick={() => setFormData({ ...formData, role })}
                                    className={`flex-1 py-3 rounded-xl border transition-all capitalize ${formData.role === role
                                            ? 'bg-indigo-600 border-indigo-600 text-white'
                                            : 'bg-white/5 border-white/10 text-slate-400 hover:bg-white/10'
                                        }`}
                                >
                                    {role}
                                </button>
                            ))}
                        </div>
                    </div>
                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full py-4 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white rounded-xl font-bold transition-all transform hover:scale-[1.02] active:scale-95 neon-glow mt-4"
                    >
                        {loading ? 'Creating Account...' : 'Continue'}
                    </button>
                </form>
                <p className="mt-8 text-center text-slate-400">
                    Already have an account? <Link to="/login" className="text-indigo-400 hover:text-indigo-300 font-medium">Log in</Link>
                </p>
            </motion.div>
        </div>
    );
};

export default Register;
