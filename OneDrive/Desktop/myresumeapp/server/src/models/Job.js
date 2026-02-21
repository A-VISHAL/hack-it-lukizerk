const mongoose = require('mongoose');

const jobSchema = new mongoose.Schema({
    title: { type: String, required: true },
    minCGPA: { type: Number, required: true },
    requiredSkills: [{ type: String }],
    preferredDomain: { type: String, required: true },
    minExperience: { type: Number, required: true }, // in years
    createdBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User' }
}, { timestamps: true });

module.exports = mongoose.model('Job', jobSchema);
