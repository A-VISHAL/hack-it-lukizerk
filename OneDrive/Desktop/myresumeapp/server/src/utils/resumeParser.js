const { GoogleGenerativeAI } = require('@google/generative-ai');
const pdf = require('pdf-parse');
const fs = require('fs');

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

const parseResumeText = async (filePath) => {
    const dataBuffer = fs.readFileSync(filePath);
    const data = await pdf(dataBuffer);
    const text = data.text;

    const model = genAI.getGenerativeModel({ model: "gemini-flash-latest" });

    const prompt = `
    Extract the following information from the resume text in JSON format:
    - name
    - email
    - cgpa (as a number out of 10 or 4, normalize to 10 if possible)
    - skills (list of strings)
    - domain (e.g., Web Development, Data Science, etc.)
    - experience (number of years, internships count as 0.5 each)
    - education (highest degree)

    Ensure the output is valid JSON and only the JSON. Do not include markdown code blocks.
    Text: ${text}
    `;

    const result = await model.generateContent(prompt);
    const response = await result.response;
    let textResponse = response.text();
    
    // Clean up potential markdown code blocks
    textResponse = textResponse.replace(/^```json\n?/, '').replace(/\n?```$/, '');

    return JSON.parse(textResponse);
};

module.exports = { parseResumeText };
