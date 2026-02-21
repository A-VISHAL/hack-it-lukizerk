# 🚀 Quick Start Guide

## Installation (3 Steps)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
streamlit run app.py
```

### 3. Open Browser
The app will automatically open at `http://localhost:8501`

## 📸 Testing with Sample Image

1. **Prepare an eye image**: Use a clear photo of an eye/iris (PNG, JPG, or JPEG)
2. **Upload**: Click "Choose an eye image file" in the app
3. **Process**: Click "🔍 Process & Compare"
4. **View Results**: See the comparison score and detailed differences
5. **Download PDF**: Click "📥 Generate & Download PDF Report"

## 🎯 Key Features

✅ **Iris Segmentation** - Automatic iris detection and extraction  
✅ **Feature Extraction** - Color, texture, contour, and spot analysis  
✅ **Comparison Engine** - Pixel-level difference calculation  
✅ **Scoring System** - 0-100 difference score with interpretation  
✅ **PDF Reports** - Comprehensive downloadable reports  
✅ **QR Code Access** - Mobile-friendly scanner demo mode  
✅ **Anti-Hallucination Guard** - Prevents diagnostic claims  

## ⚠️ Important Notes

- This is a **NON-DIAGNOSTIC** tool
- Results are for **informational purposes only**
- Always consult healthcare professionals for medical evaluation
- The system only measures **real pixel-level differences**

## 🐛 Troubleshooting

**Issue**: Import errors  
**Solution**: Run `pip install -r requirements.txt` again

**Issue**: Image not processing  
**Solution**: Ensure image is clear and well-lit, try different image

**Issue**: Segmentation fails  
**Solution**: Use images with better iris visibility and contrast

## 📱 Mobile Access

1. Go to "Scanner Demo Mode" in sidebar
2. Enter your app URL (or use default)
3. Scan QR code with phone
4. Access app on mobile device

## 📚 Full Documentation

See [README.md](README.md) for complete documentation.

---

**Ready to go!** Just run `streamlit run app.py` and start comparing! 👁️
