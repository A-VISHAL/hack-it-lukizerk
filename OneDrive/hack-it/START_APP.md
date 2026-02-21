# 🚀 How to Start the Application

## Method 1: Using the Batch File (Easiest)

1. **Double-click** `run_app.bat` in the project folder
2. A command window will open showing Streamlit starting
3. Wait for the message: "You can now view your Streamlit app in your browser"
4. The app should automatically open, or go to: **http://localhost:8501**

## Method 2: Using Command Prompt

1. Open **Command Prompt** or **PowerShell**
2. Navigate to the project folder:
   ```bash
   cd C:\Users\56vis\OneDrive\hack-it
   ```
3. Run:
   ```bash
   streamlit run app.py
   ```
4. Wait for the startup message
5. Open browser to: **http://localhost:8501**

## Method 3: Using Python Directly

1. Open **Command Prompt** or **PowerShell**
2. Navigate to the project folder
3. Run:
   ```bash
   python -m streamlit run app.py
   ```
4. Open browser to: **http://localhost:8501**

## 🔧 Troubleshooting

### If you get "Connection Refused":

1. **Check if port 8501 is in use:**
   ```bash
   netstat -ano | findstr :8501
   ```
   If something is running, kill it:
   ```bash
   taskkill /PID <process_id> /F
   ```

2. **Try a different port:**
   ```bash
   streamlit run app.py --server.port 8502
   ```
   Then access: **http://localhost:8502**

3. **Check Windows Firewall:**
   - Allow Python through Windows Firewall if prompted
   - Or temporarily disable firewall to test

4. **Clear browser cache:**
   - Press Ctrl+Shift+Delete
   - Clear cached images and files
   - Try again

5. **Try different browsers:**
   - Chrome
   - Firefox
   - Edge

### If you see import errors:

Run this to install missing packages:
```bash
pip install streamlit opencv-python numpy scikit-image scikit-learn reportlab Pillow matplotlib qrcode
```

### If the app crashes:

Check the error message in the command window and share it for troubleshooting.

## ✅ Success Indicators

When the app starts successfully, you should see:
- A command window with Streamlit output
- Message: "You can now view your Streamlit app in your browser"
- URL: "http://localhost:8501"
- Browser opens automatically (or you can click the URL)

## 📱 Access from Other Devices

Once running, you can access from other devices on your network:
1. Find your computer's IP address: `ipconfig` (look for IPv4 Address)
2. Access from other device: `http://YOUR_IP:8501`
3. Make sure both devices are on the same network

---

**Need help?** Check the error messages in the command window and share them for assistance.
