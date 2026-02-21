import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, FileText, CheckCircle2, XCircle, Loader2, Info } from 'lucide-react';

const StudentDashboard = () => {
    const [file, setFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    const fetchStatus = async () => {
        try {
            const token = localStorage.getItem('token');
            const { data } = await axios.get('http://localhost:5000/api/student/status', {
                headers: { Authorization: `Bearer ${token}` }
            });
            setData(data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchStatus();
        const interval = setInterval(fetchStatus, 5000); // Poll every 5s if processing
        return () => clearInterval(interval);
    }, []);

    const handleUpload = async (e) => {
        const selectedFile = e.target.files[0];
        if (!selectedFile || selectedFile.type !== 'application/pdf') {
            alert('Please select a valid PDF file.');
            return;
        }

        const formData = new FormData();
        formData.append('resume', selectedFile);

        setUploading(true);
        try {
            const token = localStorage.getItem('token');
            await axios.post('http://localhost:5000/api/student/upload', formData, {
                headers: { Authorization: `Bearer ${token}` }
            });
            fetchStatus();
        } catch (err) {
            alert('Upload failed. Try again.');
        } finally {
            setUploading(false);
        }
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'Shortlisted': return 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20';
            case 'Rejected': return 'text-red-400 bg-red-400/10 border-red-400/20';
            case 'Processing': return 'text-amber-400 bg-amber-400/10 border-amber-400/20';
            default: return 'text-slate-400 bg-slate-400/10 border-slate-400/20';
        }
    };

    if (loading) return (
        <div className="flex items-center justify-center min-h-[60vh]">
            <Loader2 className="w-10 h-10 text-indigo-500 animate-spin" />
        </div>
    );

    return (
        <div className="max-w-5xl mx-auto space-y-8">
            <div className="flex justify-between items-end">
                <div>
                    <h1 className="text-3xl font-bold mb-2">My Applications</h1>
                    <p className="text-slate-400">Track your resume status and AI evaluation results.</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Upload Section */}
                <div className="lg:col-span-1">
                    <div className="glass-card p-6 sticky top-24">
                        <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
                            <Upload className="w-5 h-5 text-indigo-400" />
                            Upload Resume
                        </h3>
                        <label className="group relative flex flex-col items-center justify-center w-full h-64 border-2 border-dashed border-white/10 rounded-2xl hover:border-indigo-500/50 hover:bg-white/5 transition-all cursor-pointer overflow-hidden">
                            {uploading ? (
                                <div className="flex flex-col items-center gap-4">
                                    <Loader2 className="w-10 h-10 text-indigo-500 animate-spin" />
                                    <span className="text-sm text-slate-400">Analyzing Resume...</span>
                                </div>
                            ) : (
                                <div className="flex flex-col items-center justify-center pt-5 pb-6">
                                    <FileText className="w-12 h-12 text-slate-500 group-hover:text-indigo-400 transition-colors mb-4" />
                                    <p className="text-sm text-slate-400 group-hover:text-slate-300">
                                        <span className="font-bold">Click to upload</span> or drag and drop
                                    </p>
                                    <p className="text-xs text-slate-500 mt-2">PDF Only (max 5MB)</p>
                                </div>
                            )}
                            <input type="file" className="hidden" accept=".pdf" onChange={handleUpload} disabled={uploading} />
                        </label>
                        <div className="mt-6 space-y-3">
                            <div className="flex items-start gap-3 bg-white/5 p-3 rounded-lg border border-white/10 text-xs text-slate-400">
                                <Info className="w-4 h-4 text-indigo-400 flex-shrink-0" />
                                <span>Our AI automatically extracts your details. No manual entry needed.</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Status Section */}
                <div className="lg:col-span-2 space-y-6">
                    <AnimatePresence mode="wait">
                        {!data?.resume ? (
                            <motion.div
                                initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                                className="glass-card p-12 text-center flex flex-col items-center justify-center bg-white/5"
                            >
                                <FileText className="w-16 h-16 text-slate-600 mb-6" />
                                <h3 className="text-2xl font-bold mb-2">No Resume Found</h3>
                                <p className="text-slate-400 max-w-sm">Upload your professional resume in PDF format to start the AI shortlisting process.</p>
                            </motion.div>
                        ) : (
                            <motion.div
                                key={data.resume._id}
                                initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
                                className="space-y-6"
                            >
                                {/* Extraction Summary */}
                                <div className="glass-card p-8">
                                    <div className="flex justify-between items-start mb-8">
                                        <div>
                                            <h2 className="text-2xl font-bold mb-1">{data.resume.extractedData?.name || 'Processing...'}</h2>
                                            <p className="text-slate-400">{data.resume.extractedData?.email}</p>
                                        </div>
                                        <span className={`px-4 py-1.5 rounded-full border text-sm font-bold flex items-center gap-2 ${getStatusColor(data.resume.status)}`}>
                                            {data.resume.status === 'Processing' && <Loader2 className="w-4 h-4 animate-spin" />}
                                            {data.resume.status === 'Shortlisted' && <CheckCircle2 className="w-4 h-4" />}
                                            {data.resume.status === 'Rejected' && <XCircle className="w-4 h-4" />}
                                            {data.resume.status}
                                        </span>
                                    </div>

                                    {data.resume.extractedData && (
                                        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                                            <div className="p-4 bg-white/5 rounded-xl border border-white/10">
                                                <p className="text-xs text-slate-500 uppercase font-bold mb-1">CGPA</p>
                                                <p className="text-xl font-bold text-indigo-400">{data.resume.extractedData.cgpa || 'N/A'}</p>
                                            </div>
                                            <div className="p-4 bg-white/5 rounded-xl border border-white/10">
                                                <p className="text-xs text-slate-500 uppercase font-bold mb-1">Experience</p>
                                                <p className="text-xl font-bold text-amber-400">{data.resume.extractedData.experience || 0} Yrs</p>
                                            </div>
                                            <div className="p-4 bg-white/5 rounded-xl border border-white/10">
                                                <p className="text-xs text-slate-500 uppercase font-bold mb-1">Domain</p>
                                                <p className="text-lg font-bold text-slate-200 truncate">{data.resume.extractedData.domain || 'N/A'}</p>
                                            </div>
                                            <div className="p-4 bg-white/5 rounded-xl border border-white/10">
                                                <p className="text-xs text-slate-500 uppercase font-bold mb-1">Education</p>
                                                <p className="text-lg font-bold text-slate-200 truncate">{data.resume.extractedData.education || 'N/A'}</p>
                                            </div>
                                        </div>
                                    )}

                                    <div className="mt-8">
                                        <p className="text-sm font-bold text-slate-400 mb-3 uppercase tracking-wider">Top Skills Extracted</p>
                                        <div className="flex flex-wrap gap-2">
                                            {data.resume.extractedData?.skills?.map((skill, i) => (
                                                <span key={i} className="px-3 py-1 bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 rounded-lg text-sm">
                                                    {skill}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                </div>

                                {/* Job Matching Results */}
                                <h3 className="text-xl font-bold">Matching Results</h3>
                                <div className="space-y-4">
                                    {data.results.length === 0 ? (
                                        <div className="bg-white/5 p-6 rounded-xl border border-white/10 text-slate-400 italic">
                                            Matching pending. Refresh once the admin triggers shortlisting.
                                        </div>
                                    ) : (
                                        data.results.map((res) => (
                                            <div key={res._id} className="glass-card p-6 flex flex-col md:flex-row md:items-center justify-between gap-6">
                                                <div className="flex-1">
                                                    <h4 className="text-lg font-bold mb-1">{res.job.title}</h4>
                                                    <div className={`text-sm font-medium mb-3 flex items-center gap-2 ${res.status === 'Shortlisted' ? 'text-emerald-400' : 'text-red-400'}`}>
                                                        {res.status === 'Shortlisted' ? <CheckCircle2 className="w-4 h-4" /> : <XCircle className="w-4 h-4" />}
                                                        {res.status} • Match Score: {res.score}%
                                                    </div>
                                                    <p className="text-sm text-slate-400 leading-relaxed bg-white/5 p-3 rounded-lg border border-white/5 italic">
                                                        "{res.reason}"
                                                    </p>
                                                </div>
                                                <div className="flex flex-col items-center justify-center p-4 bg-white/5 rounded-2xl min-w-[100px]">
                                                    <span className="text-xs text-slate-500 uppercase font-bold">Match Score</span>
                                                    <span className={`text-3xl font-black ${res.score > 70 ? 'text-emerald-400' : 'text-amber-400'}`}>{res.score}</span>
                                                </div>
                                            </div>
                                        ))
                                    )}
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </div>
        </div>
    );
};

export default StudentDashboard;
