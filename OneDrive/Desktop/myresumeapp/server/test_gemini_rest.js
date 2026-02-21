const https = require('https');
require('dotenv').config();
const fs = require('fs');

const logFile = 'test_rest_output.txt';
function log(msg) {
    fs.appendFileSync(logFile, msg + '\n');
    console.log(msg);
}

const apiKey = process.env.GEMINI_API_KEY;
const url = `https://generativelanguage.googleapis.com/v1beta/models?key=${apiKey}`;

fs.writeFileSync(logFile, '');
log("Testing REST API...");

https.get(url, (res) => {
  let data = '';
  res.on('data', (chunk) => data += chunk);
  res.on('end', () => {
    log("Status: " + res.statusCode);
    log("Body: " + data);
  });
}).on('error', (e) => {
  log("Error: " + e.message);
});
