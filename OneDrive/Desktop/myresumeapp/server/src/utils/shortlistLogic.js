const calculateMatchScore = (resumeData, jobData) => {
    let score = 0;
    let reasons = [];
    let isShortlisted = true;

    // 1. CGPA Check
    if (resumeData.cgpa >= jobData.minCGPA) {
        score += 25;
    } else {
        isShortlisted = false;
        reasons.push(`CGPA ${resumeData.cgpa} is below minimum requirement of ${jobData.minCGPA}`);
    }

    // 2. Experience Check
    if (resumeData.experience >= jobData.minExperience) {
        score += 25;
    } else {
        isShortlisted = false;
        reasons.push(`Experience ${resumeData.experience} years is less than required ${jobData.minExperience} years`);
    }

    // 3. Skills Check
    const skillsMatch = jobData.requiredSkills.filter(skill => 
        resumeData.skills.some(s => s.toLowerCase().includes(skill.toLowerCase()))
    );
    const skillMatchPercentage = (skillsMatch.length / jobData.requiredSkills.length) * 100;
    score += (skillMatchPercentage / 100) * 30; // Max 30 points for skills

    if (skillsMatch.length === 0 && jobData.requiredSkills.length > 0) {
        isShortlisted = false;
        reasons.push("None of the required skills match");
    }

    // 4. Domain Check
    if (resumeData.domain && resumeData.domain.toLowerCase().includes(jobData.preferredDomain.toLowerCase())) {
        score += 20;
    } else {
        // Domain mismatch doesn't necessarily reject if skills are high, but user req says "Domain matches job role"
        // I'll make it a hard requirement based on user rules
        isShortlisted = false;
        reasons.push(`Domain ${resumeData.domain} does not match preferred domain ${jobData.preferredDomain}`);
    }

    if (isShortlisted) {
        reasons.push("Meets all minimum criteria for CGPA, Experience, Skills, and Domain.");
    }

    return {
        score: Math.round(score),
        status: isShortlisted ? 'Shortlisted' : 'Rejected',
        reason: reasons.join('. ')
    };
};

module.exports = { calculateMatchScore };
