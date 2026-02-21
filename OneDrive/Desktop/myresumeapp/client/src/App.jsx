import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import Landing from './pages/Landing';
import Login from './pages/Login';
import Register from './pages/Register';
import StudentDashboard from './pages/StudentDashboard';
import AdminDashboard from './pages/AdminDashboard';

function App() {
    const [user, setUser] = useState(JSON.parse(localStorage.getItem('user')));

    const handleLogin = (userData) => {
        localStorage.setItem('user', JSON.stringify(userData.user));
        localStorage.setItem('token', userData.token);
        setUser(userData.user);
    };

    const handleLogout = () => {
        localStorage.removeItem('user');
        localStorage.removeItem('token');
        setUser(null);
    };

    return (
        <Router>
            <div className="min-h-screen bg-dark text-slate-100">
                <Navbar user={user} onLogout={handleLogout} onLogin={handleLogin} />
                <main className="container mx-auto px-4 py-8">
                    <Routes>
                        <Route path="/" element={<Landing />} />
                        <Route path="/login" element={<Login onLogin={handleLogin} />} />
                        <Route path="/register" element={<Register onLogin={handleLogin} />} />

                        <Route
                            path="/student-dashboard"
                            element={user?.role === 'student' ? <StudentDashboard /> : <Navigate to="/login" />}
                        />
                        <Route
                            path="/admin-dashboard"
                            element={user?.role === 'admin' ? <AdminDashboard /> : <Navigate to="/login" />}
                        />
                    </Routes>
                </main>
            </div>
        </Router>
    );
}

export default App;
