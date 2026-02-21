import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Plus, Trash2, Users, Briefcase, Filter, Search,
    ChevronRight, CheckCircle2, XCircle, Play, Loader2, AlertCircle
} from 'lucide-react';

const AdminDashboard = () => {
    const [jobs, setJobs] = useState([]);
    const [reports, setReports] = useState([]);
    const [loading, setLoading] = useState(true);
    const [triggering, setTriggering] = useState(false);
    const [activeTab, setActiveTab] = useState('jobs'); // 'jobs' or 'candidates'

    // Job Form State
    const [showJobModal, setShowJobModal] = useState(false);
    const [newJob, setNewJob] = useState({
        title: '', minCGPA: 7.0, requiredSkills: '', preferredDomain: '', minExperience: 0
    });

    const fetchData = async () => {
        try {
            const token = localStorage.getItem('token');
            const headers = { Authorization: `Bearer ${token}` };
            const [jobsRes, reportRes] = await Promise.all([
                axios.get('http://localhost:5000/api/admin/jobs', { headers }),
                axios.get('http://localhost:5000/api/admin/report', { headers })
            ]);
            setJobs(jobsRes.data);
            setReports(reportRes.data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const handleCreateJob = async (e) => {
        e.preventDefault();
        try {
            const token = localStorage.getItem('token');
            await axios.post('http://localhost:5000/api/admin/jobs', {
                ...newJob,
                requiredSkills: newJob.requiredSkills.split(',').map(s => s.trim())
            }, { headers: { Authorization: `Bearer ${token}` } });
            setShowJobModal(false);
            fetchData();
        } catch (err) {
            alert('Failed to create job');
        }
    };

    const handleDeleteJob = async (id) => {
        if (!confirm('Delete this job?')) return;
        try {
            const token = localStorage.getItem('token');
            await axios.delete(`http://localhost:5000/api/admin/jobs/${id}`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            fetchData();
        } catch (err) {
            alert('Delete failed');
        }
    };

    const handleTrigger = async () => {
        setTriggering(true);
        try {
            const token = localStorage.getItem('token');
            await axios.post('http://localhost:5000/api/admin/trigger-shortlisting', {}, {
                headers: { Authorization: `Bearer ${token}` }
            });
            fetchData();
            alert('Shortlisting process completed!');
        } catch (err) {
            alert('Trigger failed');
        } finally {
            setTriggering(false);
        }
    };

    if (loading) return (
        <div className="flex items-center justify-center min-h-[60vh]">
            <Loader2 className="w-10 h-10 text-indigo-500 animate-spin" />
        </div>
    );

    return (
        <div className="max-w-7xl mx-auto space-y-8">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold mb-2">Admin Command Center</h1>
                    <p className="text-slate-400">Manage vacancies and monitor AI shortlisting results.</p>
                </div>
                <div className="flex gap-4">
                    <button
                        onClick={handleTrigger}
                        disabled={triggering}
                        className="flex items-center gap-2 px-6 py-3 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white rounded-xl font-bold transition-all transform hover:scale-105 neon-glow group"
                    >
                        {triggering ? <Loader2 className="w-5 h-5 animate-spin" /> : <Play className="w-5 h-5 group-hover:fill-current" />}
                        Trigger Shortlisting
                    </button>
                    <button
                        onClick={() => setShowJobModal(true)}
                        className="flex items-center gap-2 px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-bold transition-all transform hover:scale-105 neon-glow"
                    >
                        <Plus className="w-5 h-5" />
                        Post New Job
                    </button>
                </div>
            </div>

            <div className="flex gap-1 p-1 bg-white/5 border border-white/10 rounded-2xl w-fit">
                <button
                    onClick={() => setActiveTab('jobs')}
                    className={`flex items-center gap-2 px-6 py-2.5 rounded-xl transition-all font-medium ${activeTab === 'jobs' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white hover:bg-white/5'}`}
                >
                    <Briefcase className="w-4 h-4" />
                    Job Descriptions ({jobs.length})
                </button>
                <button
                    onClick={() => setActiveTab('candidates')}
                    className={`flex items-center gap-2 px-6 py-2.5 rounded-xl transition-all font-medium ${activeTab === 'candidates' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white hover:bg-white/5'}`}
                >
                    <Users className="w-4 h-4" />
                    Candidates ({reports.length})
                </button>
            </div>

            {/* Jobs Table */}
            {activeTab === 'jobs' ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {jobs.map(job => (
                        <motion.div
                            layout key={job._id}
                            className="glass-card p-6 border-white/10 flex flex-col justify-between"
                        >
                            <div>
                                <div className="flex justify-between items-start mb-4">
                                    <h3 className="text-xl font-bold text-indigo-400">{job.title}</h3>
                                    <button onClick={() => handleDeleteJob(job._id)} className="p-2 text-slate-500 hover:text-red-400 transition-colors">
                                        <Trash2 className="w-4 h-4" />
                                    </button>
                                </div>
                                <div className="space-y-3 mb-6 font-medium text-sm">
                                    <div className="flex justify-between">
                                        <span className="text-slate-500">Min CGPA</span>
                                        <span className="text-slate-200">{job.minCGPA}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-slate-500">Experience</span>
                                        <span className="text-slate-200">{job.minExperience} Yrs</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-slate-500">Domain</span>
                                        <span className="text-slate-200">{job.preferredDomain}</span>
                                    </div>
                                </div>
                                <div className="flex flex-wrap gap-2">
                                    {job.requiredSkills.map((s, i) => (
                                        <span key={i} className="px-2 py-1 bg-white/5 border border-white/10 rounded-md text-xs text-slate-400">{s}</span>
                                    ))}
                                </div>
                            </div>
                        </motion.div>
                    ))}
                    {jobs.length === 0 && (
                        <div className="col-span-full py-20 text-center glass-card">
                            <AlertCircle className="w-12 h-12 text-slate-600 mx-auto mb-4" />
                            <p className="text-slate-400 font-medium">No job descriptions posted yet.</p>
                        </div>
                    )}
                </div>
            ) : (
                /* Candidates Table */
                <div className="glass-card overflow-hidden">
                    <div className="overflow-x-auto">
                        <table className="w-full text-left">
                            <thead>
                                <tr className="border-b border-white/10 bg-white/5">
                                    <th className="px-6 py-4 text-xs uppercase font-bold text-slate-500">Candidate</th>
                                    <th className="px-6 py-4 text-xs uppercase font-bold text-slate-500">Job Title</th>
                                    <th className="px-6 py-4 text-xs uppercase font-bold text-slate-500">Match Score</th>
                                    <th className="px-6 py-4 text-xs uppercase font-bold text-slate-500">Status</th>
                                    <th className="px-6 py-4 text-xs uppercase font-bold text-slate-500">Evaluation</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-white/10">
                                {reports.map((report) => (
                                    <tr key={report._id} className="hover:bg-white/5 transition-colors group">
                                        <td className="px-6 py-4">
                                            <div className="flex flex-col">
                                                <span className="font-bold text-slate-200">{report.resume.user.name}</span>
                                                <span className="text-xs text-slate-500">{report.resume.user.email}</span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 font-medium">{report.job.title}</td>
                                        <td className="px-6 py-4">
                                            <div className="flex items-center gap-2">
                                                <span className={`text-lg font-black ${report.score > 70 ? 'text-emerald-400' : report.score > 40 ? 'text-amber-400' : 'text-red-400'}`}>
                                                    {report.score}%
                                                </span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4">
                                            <span className={`px-3 py-1 rounded-full text-xs font-bold border ${report.status === 'Shortlisted' ? 'bg-emerald-400/10 text-emerald-400 border-emerald-400/20' : 'bg-red-400/10 text-red-400 border-red-400/20'
                                                }`}>
                                                {report.status}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 max-w-xs text-xs text-slate-400 italic">
                                            {report.reason}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                        {reports.length === 0 && (
                            <div className="py-20 text-center">
                                <p className="text-slate-400">No candidates evaluated yet. Trigger shortlisting to begin.</p>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Create Job Modal */}
            <AnimatePresence>
                {showJobModal && (
                    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
                        <motion.div
                            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                            onClick={() => setShowJobModal(false)}
                            className="absolute inset-0 bg-dark/80 backdrop-blur-sm"
                        />
                        <motion.div
                            initial={{ opacity: 0, scale: 0.9, y: 20 }} animate={{ opacity: 1, scale: 1, y: 0 }} exit={{ opacity: 0, scale: 0.9, y: 20 }}
                            className="glass-card p-8 w-full max-w-2xl relative z-10"
                        >
                            <h2 className="text-2xl font-bold mb-6">Define Job Requirement</h2>
                            <form onSubmit={handleCreateJob} className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div className="col-span-2">
                                    <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Job Title</label>
                                    <input required className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 outline-none focus:border-indigo-500" placeholder="e.g. Senior Frontend Engineer"
                                        onChange={e => setNewJob({ ...newJob, title: e.target.value })} />
                                </div>
                                <div>
                                    <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Min. CGPA</label>
                                    <input required type="number" step="0.1" className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 outline-none focus:border-indigo-500"
                                        onChange={e => setNewJob({ ...newJob, minCGPA: parseFloat(e.target.value) })} />
                                </div>
                                <div>
                                    <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Min. Experience (Yrs)</label>
                                    <input required type="number" className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 outline-none focus:border-indigo-500"
                                        onChange={e => setNewJob({ ...newJob, minExperience: parseInt(e.target.value) })} />
                                </div>
                                <div className="col-span-2">
                                    <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Domain / Industry</label>
                                    <input required className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 outline-none focus:border-indigo-500" placeholder="e.g. Web Development"
                                        onChange={e => setNewJob({ ...newJob, preferredDomain: e.target.value })} />
                                </div>
                                <div className="col-span-2">
                                    <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Required Skills (Comma separated)</label>
                                    <input required className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 outline-none focus:border-indigo-500" placeholder="React, Node.js, MongoDB..."
                                        onChange={e => setNewJob({ ...newJob, requiredSkills: e.target.value })} />
                                </div>
                                <div className="col-span-2 pt-4 flex gap-4">
                                    <button type="submit" className="flex-1 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-bold transition-all transform hover:scale-105 neon-glow">
                                        Create Vacancy
                                    </button>
                                    <button type="button" onClick={() => setShowJobModal(false)} className="flex-1 py-3 bg-white/5 hover:bg-white/10 text-white rounded-xl font-bold transition-all">
                                        Cancel
                                    </button>
                                </div>
                            </form>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>
        </div>
    );
};

export default AdminDashboard;
