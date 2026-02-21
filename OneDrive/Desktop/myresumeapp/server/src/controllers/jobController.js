const Job = require('../models/Job');
const Resume = require('../models/Resume');
const Result = require('../models/Result');
const { calculateMatchScore } = require('../utils/shortlistLogic');

exports.createJob = async (req, res) => {
    try {
        const job = new Job({ ...req.body, createdBy: req.user._id });
        await job.save();
        res.status(201).send(job);
    } catch (e) {
        res.status(400).send(e);
    }
};

exports.getJobs = async (req, res) => {
    try {
        const jobs = await Job.find({});
        res.send(jobs);
    } catch (e) {
        res.status(500).send();
    }
};

exports.deleteJob = async (req, res) => {
    try {
        const job = await Job.findByIdAndDelete(req.params.id);
        if(!job) return res.status(404).send();
        res.send(job);
    } catch (e) {
        res.status(500).send();
    }
};

exports.triggerShortlisting = async (req, res) => {
    try {
        const jobs = await Job.find({});
        const resumes = await Resume.find({ status: { $ne: 'Processing' } });
        
        let evaluations = 0;
        for (const job of jobs) {
            for (const resume of resumes) {
                // Check if already evaluated
                const existing = await Result.findOne({ resume: resume._id, job: job._id });
                if (existing) continue;

                const analysis = calculateMatchScore(resume.extractedData, job);
                const result = new Result({
                    resume: resume._id,
                    job: job._id,
                    ...analysis
                });
                await result.save();
                
                // Update resume status if needed (e.g., if shortlisted for at least one job)
                if (analysis.status === 'Shortlisted') {
                   resume.status = 'Shortlisted';
                   await resume.save();
                } else if (resume.status === 'Pending') {
                   resume.status = 'Rejected';
                   await resume.save();
                }
                evaluations++;
            }
        }
        res.send({ message: `Shortlisting completed. ${evaluations} new evaluations created.` });
    } catch (e) {
        console.error(e);
        res.status(500).send(e);
    }
};

exports.getShortlistReport = async (req, res) => {
    try {
        const results = await Result.find({})
            .populate({ path: 'resume', populate: { path: 'user' } })
            .populate('job');
        res.send(results);
    } catch (e) {
        res.status(500).send();
    }
};
