const mongoose = require('mongoose');

const resultSchema = new mongoose.Schema({
    resume: { type: mongoose.Schema.Types.ObjectId, ref: 'Resume', required: true },
    job: { type: mongoose.Schema.Types.ObjectId, ref: 'Job', required: true },
    status: { type: String, enum: ['Shortlisted', 'Rejected'], required: true },
    score: { type: Number, required: true },
    reason: { type: String, required: true }
}, { timestamps: true });

module.exports = mongoose.model('Result', resultSchema);
