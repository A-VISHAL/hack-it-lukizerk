const Resume = require('../models/Resume');
const Result = require('../models/Result');
const { parseResumeText } = require('../utils/resumeParser');
const { calculateMatchScore } = require('../utils/shortlistLogic');
const Job = require('../models/Job');

exports.uploadResume = async (req, res) => {
    try {
        if (!req.file) return res.status(400).send({ error: 'Please upload a PDF file.' });

        const resume = new Resume({
            user: req.user._id,
            filePath: req.file.path,
            status: 'Processing'
        });
        await resume.save();

        // Background processing
        parseResumeText(req.file.path).then(async (extractedData) => {
            resume.extractedData = extractedData;
            resume.status = 'Pending'; // Waiting for admin to trigger shortlist or auto-match?
            // "Student should NOT manually enter any data"
            // Let's assume after extraction it's ready for matching.
            await resume.save();
        }).catch(err => {
            console.error("AI Extraction Error:", err);
            resume.status = 'Rejected'; // Or handle error
            resume.save();
        });

        res.status(202).send(resume);
    } catch (e) {
        res.status(500).send(e);
    }
};

exports.getStudentResumeStatus = async (req, res) => {
    try {
        const resume = await Resume.findOne({ user: req.user._id }).sort({ createdAt: -1 });
        if (!resume) return res.status(404).send();

        // Find results for this resume
        const results = await Result.find({ resume: resume._id }).populate('job');
        res.send({ resume, results });
    } catch (e) {
        res.status(500).send();
    }
};
