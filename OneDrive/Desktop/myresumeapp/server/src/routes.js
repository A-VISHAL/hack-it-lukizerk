const express = require('express');
const multer = require('multer');
const path = require('path');
const { auth, adminAuth } = require('./middleware/auth');
const authController = require('./controllers/authController');
const resumeController = require('./controllers/resumeController');
const jobController = require('./controllers/jobController');

const router = express.Router();

// Multer Config
const storage = multer.diskStorage({
    destination: (req, file, cb) => cb(null, 'uploads/'),
    filename: (req, file, cb) => cb(null, Date.now() + path.extname(file.originalname))
});
const upload = multer({ 
    storage,
    fileFilter: (req, file, cb) => {
        if (file.mimetype === 'application/pdf') cb(null, true);
        else cb(new Error('Only PDF files are allowed'), false);
    }
});

// Auth
router.post('/auth/register', authController.register);
router.post('/auth/login', authController.login);

// Student
router.post('/student/upload', auth, upload.single('resume'), resumeController.uploadResume);
router.get('/student/status', auth, resumeController.getStudentResumeStatus);

// Admin
router.post('/admin/jobs', auth, adminAuth, jobController.createJob);
router.get('/admin/jobs', auth, adminAuth, jobController.getJobs);
router.delete('/admin/jobs/:id', auth, adminAuth, jobController.deleteJob);
router.post('/admin/trigger-shortlisting', auth, adminAuth, jobController.triggerShortlisting);
router.get('/admin/report', auth, adminAuth, jobController.getShortlistReport);

module.exports = router;
