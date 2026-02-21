const jwt = require('jsonwebtoken');
const User = require('../models/User');

const auth = async (req, res, next) => {
    try {
        const authHeader = req.header('Authorization');
        if (!authHeader) {
            throw new Error();
        }

        const token = authHeader.replace('Bearer ', '');

        // DEV BYPASS
        if (token === 'dev-token-student') {
            const user = await User.findOne({ email: 'student@example.com' });
            if (!user) return res.status(404).send({ error: 'Dev student user not found. Run seed.' });
            req.user = user; // Mongoose document
            return next();
        }
        if (token === 'dev-token-admin') {
            const user = await User.findOne({ email: 'admin@example.com' });
            if (!user) return res.status(404).send({ error: 'Dev admin user not found. Run seed.' });
            req.user = user; // Mongoose document
            return next();
        }

        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        req.user = decoded; // This is usually just the payload, not full doc. 
        // Note: Normal flow sets req.user to JWT payload. 
        // Dev bypass sets it to Mongoose doc. 
        // Ensure controllers handle both, or finding by ID works on both. 
        // Mongoose doc has _id. Payload usually has _id (if we put it there).
        next();
    } catch (e) {
        res.status(401).send({ error: 'Please authenticate.' });
    }
};

const adminAuth = (req, res, next) => {
    if (req.user.role !== 'admin') {
        return res.status(403).send({ error: 'Access denied. Admin only.' });
    }
    next();
};

module.exports = { auth, adminAuth };
