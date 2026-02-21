# AI Resume Shortlisting Web App

A full-stack application that uses AI to parse resumes and automatically shortlist candidates based on job descriptions.

## Tech Stack
- **Frontend:** React.js, Tailwind CSS, Framer Motion
- **Backend:** Node.js, Express, Multer, PDF-Parse
- **AI:** OpenAI GPT-4o
- **Database:** MongoDB

## Features
- **Student Portal:** Upload PDF resume, view AI-extracted details, and track shortlisting status.
- **Admin Portal:** Create/Delete Job Descriptions, trigger AI shortlisting, and view detailed reports with match scores.
- **Smart Extraction:** Automatically extracts Name, Email, CGPA, Skills, Domain, and Experience using GPT-4o.
- **Matching Logic:** Calculates match scores based on CGPA, Skills, Experience, and Domain.

## Setup Instructions

### 1. Backend Setup
1. `cd server`
2. `npm install`
3. Create a `.env` file with:
   ```env
   PORT=5000
   MONGODB_URI=your_mongodb_uri
   JWT_SECRET=your_jwt_secret
   OPENAI_API_KEY=your_openai_key
   ```
4. `npm start` (or `node index.js`)

### 2. Frontend Setup
1. `cd client`
2. `npm install`
3. `npm run dev`

### 3. Usage
1. Register as a **Student** to upload your resume.
2. Register as an **Admin** to create Job Descriptions.
3. Once a job is created and a resume is uploaded, click **Trigger Shortlisting** in the Admin Dashboard.
4. View the results on both Student and Admin portals.
