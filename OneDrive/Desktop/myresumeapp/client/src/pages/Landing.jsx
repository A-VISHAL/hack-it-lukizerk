import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { Sparkles, CheckCircle, Zap, Shield } from 'lucide-react';

const Landing = () => {
    return (
        <div className="flex flex-col items-center justify-center pt-20">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-center max-w-4xl"
            >
                <span className="px-4 py-2 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-sm font-medium mb-6 inline-block">
                    AI-Powered Talent Matching
                </span>
                <h1 className="text-6xl font-extrabold mb-6 leading-tight">
                    Next-Gen Resume <br />
                    <span className="gradient-text">Shortlisting Platform</span>
                </h1>
                <p className="text-xl text-slate-400 mb-10 max-w-2xl mx-auto">
                    Automate your recruitment process with AI that understands experience, skills, and potential.
                    Perfect matching between students and job descriptions.
                </p>

                <div className="flex gap-4 justify-center">
                    <Link to="/register" className="px-8 py-4 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-bold text-lg transition-all transform hover:scale-105 neon-glow">
                        Start Uploading
                    </Link>
                    <Link to="/login" className="px-8 py-4 bg-white/5 hover:bg-white/10 text-white border border-white/10 rounded-xl font-bold text-lg transition-all">
                        Admin Portal
                    </Link>
                </div>
            </motion.div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-32 w-full max-w-5xl">
                {[
                    { icon: <Zap className="text-amber-400" />, title: "Instant Extraction", desc: "AI parses name, email, CGPA, and skills in seconds." },
                    { icon: <CheckCircle className="text-emerald-400" />, title: "Auto-Matching", desc: "Rigorous matching logic based on job requirements." },
                    { icon: <Shield className="text-blue-400" />, title: "Bi-Role Support", desc: "Dedicated portals for both Students and Admins." }
                ].map((feature, i) => (
                    <motion.div
                        key={i}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.1 }}
                        className="glass-card p-8 text-center"
                    >
                        <div className="w-12 h-12 bg-white/5 rounded-2xl flex items-center justify-center mx-auto mb-6">
                            {feature.icon}
                        </div>
                        <h3 className="text-xl font-bold mb-3">{feature.title}</h3>
                        <p className="text-slate-400">{feature.desc}</p>
                    </motion.div>
                ))}
            </div>
        </div>
    );
};

export default Landing;
