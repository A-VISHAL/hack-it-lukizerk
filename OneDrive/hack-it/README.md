# 👁️ INDIAN IRIS - Real-Time Iris Comparison System

A **NON-DIAGNOSTIC** medical support tool that compares a user's iris with a pre-stored healthy iris baseline and generates a structural difference score and comparison report.

## ⚠️ Important Disclaimer

This application is a **NON-DIAGNOSTIC** tool that measures pixel-level structural differences only. It does **NOT**:
- Diagnose diseases
- Predict health outcomes
- Provide medical interpretations
- Make health recommendations

Results are for **informational purposes only**. Always consult qualified healthcare professionals for medical evaluation.

## 📁 Project Structure

```
hack-it/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── utils/
│   ├── segmentation.py            # Iris segmentation module
│   ├── features.py                # Feature extraction module
│   ├── compare.py                 # Comparison engine
│   ├── guard.py                   # Anti-hallucination guard
│   └── report.py                  # PDF report generator
├── reference/
│   └── good_iris_features.json    # Baseline healthy iris features
├── uploads/                       # User uploaded images (auto-created)
└── reports/                        # Generated PDF reports (auto-created)
```

## 🚀 Installation & Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Clone or Download the Project

```bash
# If using git
git clone <repository-url>
cd hack-it

# Or simply navigate to the project directory
cd hack-it
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `streamlit` - Web application framework
- `opencv-python` - Image processing
- `numpy` - Numerical computations
- `scikit-image` - Image feature extraction
- `scikit-learn` - Machine learning utilities
- `reportlab` - PDF generation
- `Pillow` - Image handling
- `matplotlib` - Plotting
- `qrcode` - QR code generation

### Step 3: Verify Installation

```bash
python -c "import streamlit; import cv2; import numpy; print('All dependencies installed successfully!')"
```

## 🎯 Running the Application

### Local Development

```bash
streamlit run app.py
```

The application will automatically open in your default web browser at `http://localhost:8501`

### Access from Other Devices

1. Find your local IP address:
   - **Windows**: `ipconfig` (look for IPv4 Address)
   - **Mac/Linux**: `ifconfig` or `ip addr`
2. Run Streamlit with network access:
   ```bash
   streamlit run app.py --server.address 0.0.0.0
   ```
3. Access from other devices using: `http://YOUR_IP:8501`

## 📱 Usage Guide

### 1. Upload & Compare Mode

1. **Upload Image**: Click "Choose an eye image file" and select a clear eye/iris image (PNG, JPG, or JPEG)
2. **Preview**: The uploaded image will be displayed
3. **Process**: Click "🔍 Process & Compare" button
4. **View Results**: 
   - See the segmented iris ROI
   - View extracted features
   - Check comparison score and category
   - Review detailed feature differences
5. **Download Report**: Click "📥 Generate & Download PDF Report" to get a comprehensive PDF

### 2. Scanner Demo Mode

1. Navigate to "Scanner Demo Mode" in the sidebar
2. Enter your application URL (or use the default)
3. A QR code will be generated
4. Scan the QR code with a mobile device to access the web version
5. Share the URL or QR code with judges/team members

### 3. About Page

View detailed information about the application, its features, and technical stack.

## 🔬 How It Works

### Module 1: Iris Segmentation
- Uses OpenCV's Hough Circle Transform
- Detects iris region in the eye image
- Crops and resizes to 256×256 pixels
- Falls back to center region if detection fails

### Module 2: Feature Extraction
Extracts four categories of features:

1. **Color Features (HSV)**
   - `h_mean`: Hue mean value
   - `s_mean`: Saturation mean value
   - `v_mean`: Value (brightness) mean value

2. **Texture Features**
   - `lbp_mean`: Local Binary Pattern mean
   - `contrast`: GLCM contrast
   - `entropy`: GLCM entropy (dissimilarity)
   - `homogeneity`: GLCM homogeneity

3. **Contour Metrics**
   - `edge_deviation`: Standard deviation of edge distances
   - `circular_variance`: Deviation from perfect circle

4. **Spot Detection**
   - `spot_count`: Number of pigment-like anomalies
   - `avg_spot_size`: Average spot size

### Module 3: Comparison Engine
- Loads baseline features from `reference/good_iris_features.json`
- Calculates absolute differences for each feature
- Applies weighted scoring algorithm
- Generates 0-100 difference score:
  - **0-25**: Normal Deviation
  - **26-60**: Moderate Deviation
  - **61-100**: High Structural Deviation

### Module 4: Anti-Hallucination Guard
- Filters out noise-level differences (< 5.0 score)
- Prevents diagnostic claims
- Adds strict disclaimers
- Ensures scientific, deterministic comparisons only

### Module 5: PDF Report Generation
- Creates comprehensive PDF using ReportLab
- Includes images, comparison results, feature differences
- Provides doctor submission section
- Contains all necessary disclaimers

## 📊 Understanding Results

### Difference Score
- **0-25 (Normal Deviation)**: Minimal structural differences. Within expected variation range.
- **26-60 (Moderate Deviation)**: Noticeable structural differences. May warrant further examination.
- **61-100 (High Structural Deviation)**: Significant structural differences. Professional evaluation recommended.

### Feature Differences
The detailed comparison shows pixel-level differences in:
- Color characteristics
- Texture patterns
- Contour shapes
- Spot/anomaly presence

## 🛡️ Safety Features

1. **Noise Threshold**: Differences below 5.0 are considered noise
2. **No Diagnosis**: System explicitly does not diagnose diseases
3. **No Predictions**: No health outcome predictions
4. **Scientific Only**: Only measures real pixel-level differences
5. **Clear Disclaimers**: Multiple disclaimers throughout the application

## 🔧 Configuration

### Modifying Baseline Features

Edit `reference/good_iris_features.json` to update the healthy iris baseline:

```json
{
  "h_mean": 15.5,
  "s_mean": 45.2,
  "v_mean": 120.8,
  "lbp_mean": 8.3,
  "contrast": 12.5,
  "entropy": 3.2,
  "homogeneity": 0.85,
  "edge_deviation": 0.15,
  "circular_variance": 0.08,
  "spot_count": 2,
  "avg_spot_size": 8.5
}
```

### Adjusting Scoring Weights

Edit `utils/compare.py` to modify feature weights in the `calculate_difference_score()` function.

## 🚢 Deployment

### Streamlit Cloud (Recommended)

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Deploy the app
5. Share the generated URL

### Other Platforms

- **Heroku**: Use Procfile with `web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
- **AWS/Azure/GCP**: Deploy as containerized application
- **Local Server**: Use with reverse proxy (nginx)

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed: `pip install -r requirements.txt`
2. **Image Not Loading**: Check file format (PNG, JPG, JPEG) and file size
3. **Segmentation Fails**: Try images with better lighting and clearer iris visibility
4. **PDF Generation Error**: Ensure `reports/` directory exists and has write permissions

### Getting Help

- Check error messages in the Streamlit console
- Verify all dependencies are correctly installed
- Ensure Python version is 3.8+

## 📝 License

This project is provided as-is for educational and research purposes.

## 👥 Credits

Developed as a hackathon project for real-time iris comparison analysis.

---

**Remember**: This is a NON-DIAGNOSTIC tool. Always consult qualified healthcare professionals for medical evaluation.
