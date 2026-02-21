const mongoose = require('mongoose');

const resumeSchema = new mongoose.Schema({
    user: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
    filePath: { type: String, required: true },
    extractedData: {
        name: String,
        email: String,
        cgpa: Number,
        skills: [String],
        domain: String,
        experience: Number, // years
        education: String
    },
    status: { 
        type: String, 
        enum: ['Processing', 'Shortlisted', 'Rejected', 'Pending'], 
        default: 'Processing' 
    }
}, { timestamps: true });

module.exports = mongoose.model('Resume', resumeSchema);
