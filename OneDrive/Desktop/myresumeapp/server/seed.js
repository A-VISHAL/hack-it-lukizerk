const mongoose = require('mongoose');
const User = require('./src/models/User');
const Job = require('./src/models/Job');
const dotenv = require('dotenv');

dotenv.config();

mongoose.connect(process.env.MONGODB_URI)
    .then(() => console.log('Connected to MongoDB'))
    .catch(err => console.error('Could not connect to MongoDB', err));

const seedData = async () => {
    try {
        // Clear existing data (optional, be careful in prod)
        // await User.deleteMany({});
        // await Job.deleteMany({});

        // check if users exist
        const adminExists = await User.findOne({ email: 'admin@example.com' });
        if (!adminExists) {
            const admin = new User({
                name: 'Admin User',
                email: 'admin@example.com',
                password: 'password123',
                role: 'admin'
            });
            await admin.save();
            console.log('Admin created: admin@example.com / password123');
        } else {
            console.log('Admin already exists');
        }

        const studentExists = await User.findOne({ email: 'student@example.com' });
        if (!studentExists) {
            const student = new User({
                name: 'Student User',
                email: 'student@example.com',
                password: 'password123',
                role: 'student'
            });
            await student.save();
            console.log('Student created: student@example.com / password123');
        } else {
            console.log('Student already exists');
        }
        
        console.log('Seeding completed!');
        process.exit();
    } catch (err) {
        console.error(err);
        process.exit(1);
    }
};

seedData();
