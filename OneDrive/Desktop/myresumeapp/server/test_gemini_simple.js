require('dotenv').config();
const { GoogleGenerativeAI } = require('@google/generative-ai');
const fs = require('fs');

const logFile = 'test_output.txt';
function log(msg) {
    fs.appendFileSync(logFile, msg + '\n');
    console.log(msg);
}

async function test() {
  fs.writeFileSync(logFile, ''); // clear file
  try {
    log("Testing Gemini API Key...");
    const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
    
    // Test the model currently configured in code
    const models = [
        "gemini-flash-latest",
        "gemini-1.5-flash"
    ];

    for (const modelName of models) {
        try {
            log(`Attempting ${modelName}...`);
            const model = genAI.getGenerativeModel({ model: modelName });
            const result = await model.generateContent("Hello");
            log(`SUCCESS with ${modelName}! Response: ` + result.response.text());
            return; 
        } catch (e) {
            log(`Failed with ${modelName}: ` + e.message);
        }
    }
    
  } catch (error) {
    log("FATAL ERROR: " + error.message);
  }
}
test();
