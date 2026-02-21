const User = require('../models/User');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');

exports.register = async (req, res) => {
    try {
        const { name, email, password, role } = req.body;
        const user = new User({ name, email, password, role });
        await user.save();
        const token = jwt.sign({ _id: user._id, role: user.role }, process.env.JWT_SECRET);
        res.status(201).send({ user, token });
    } catch (e) {
        res.status(400).send(e);
    }
};

exports.login = async (req, res) => {
    try {
        const user = await User.findOne({ email: req.body.email });
        if (!user || !(await bcrypt.compare(req.body.password, user.password))) {
            return res.status(400).send({ error: 'Invalid login credentials' });
        }
        const token = jwt.sign({ _id: user._id, role: user.role }, process.env.JWT_SECRET);
        res.send({ user, token });
    } catch (e) {
        res.status(500).send();
    }
};
