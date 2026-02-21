"""
INDIAN IRIS - Real-Time Iris Comparison System
Main Streamlit Application
"""

import streamlit as st
import cv2
import numpy as np
from pathlib import Path
import json
import qrcode
from PIL import Image as PILImage
import io
import base64

# Import custom modules
from utils.segmentation import segment_iris, create_sector_map
from utils.features import extract_all_features, analyze_sectors
from utils.compare import compare_iris
from utils.guard import validate_comparison_result
from utils.report import generate_pdf_report

# Page configuration
st.set_page_config(
    page_title="INDIAN IRIS - Real-Time Iris Comparison",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'uploaded_image' not in st.session_state:
    st.session_state.uploaded_image = None
if 'segmented_iris' not in st.session_state:
    st.session_state.segmented_iris = None
if 'features' not in st.session_state:
    st.session_state.features = None
if 'comparison_result' not in st.session_state:
    st.session_state.comparison_result = None
if 'symptoms' not in st.session_state:
    st.session_state.symptoms = None
if 'sector_map' not in st.session_state:
    st.session_state.sector_map = None

# Create necessary directories
Path("uploads").mkdir(exist_ok=True)
Path("reports").mkdir(exist_ok=True)

# Constants
GOOD_IRIS_PATH = "reference/good_iris_features.json"


def generate_qr_code(url):
    """Generate QR code for the application URL."""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img


def main():
    """Main application function."""
    
    # Header
    st.title("👁️ INDIAN IRIS")
    st.markdown("### Real-Time Iris Comparison System")
    
    # Important disclaimer
    st.warning(
        "⚠️ **NON-DIAGNOSTIC TOOL**: This application measures pixel-level structural differences only. "
        "It does NOT diagnose diseases, predict health outcomes, or provide medical interpretations. "
        "Results are for informational purposes only. Always consult qualified healthcare professionals."
    )
    
    # Sidebar
    with st.sidebar:
        st.header("📋 Navigation")
        page = st.radio(
            "Select Mode",
            ["Upload & Compare", "Live Scan", "Scanner Demo Mode", "About"]
        )
        
        st.markdown("---")
        st.header("ℹ️ Information")
        st.info(
            "This tool compares your iris image with a reference healthy iris baseline "
            "and generates a structural difference score."
        )
    
    # Main content based on selected page
    if page == "Upload & Compare":
        upload_and_compare_page()
    elif page == "Live Scan":
        live_scan_page()
    elif page == "Scanner Demo Mode":
        scanner_demo_page()
    else:
        about_page()


def symptom_questionnaire():
    """Display symptom questionnaire and return responses."""
    st.subheader("📋 Symptom Questionnaire")
    st.info("Please answer these questions to help correlate visual findings with symptoms.")
    
    symptoms = {}
    
    col1, col2 = st.columns(2)
    
    with col1:
        symptoms['pain'] = st.select_slider(
            "1. Eye Pain Level",
            options=["None", "Mild", "Moderate", "Severe"],
            help="Rate your eye pain level"
        )
        
        symptoms['redness'] = st.select_slider(
            "2. Eye Redness",
            options=["None", "Slight", "Moderate", "Severe"],
            help="How red is your eye?"
        )
        
        symptoms['vision_blur'] = st.select_slider(
            "3. Vision Blur",
            options=["None", "Slight", "Moderate", "Severe"],
            help="Do you experience blurred vision?"
        )
    
    with col2:
        symptoms['light_sensitivity'] = st.select_slider(
            "4. Light Sensitivity",
            options=["None", "Mild", "Moderate", "Severe"],
            help="Are you sensitive to light?"
        )
        
        symptoms['duration'] = st.selectbox(
            "5. Symptom Duration",
            options=["Less than 1 day", "1-3 days", "4-7 days", "1-2 weeks", "More than 2 weeks"],
            help="How long have you had these symptoms?"
        )
    
    return symptoms


def upload_and_compare_page():
    """Main upload and comparison page."""
    
    st.header("📤 Upload Iris Image")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose an eye image file",
        type=['png', 'jpg', 'jpeg'],
        help="Upload a clear image of the eye/iris"
    )
    
    if uploaded_file is not None:
        # Save uploaded file
        upload_path = Path("uploads") / uploaded_file.name
        with open(upload_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.session_state.uploaded_image = str(upload_path)
        
        # Display uploaded image
        st.subheader("📷 Uploaded Image Preview")
        col1, col2 = st.columns(2)
        
        with col1:
            st.image(uploaded_file, caption="Original Image", use_container_width=True)
        
        # Symptom questionnaire
        st.markdown("---")
        symptoms = symptom_questionnaire()
        st.session_state.symptoms = symptoms
        
        # Process button
        if st.button("🔍 Process & Compare", type="primary"):
            process_and_compare()
        
        # Show results if available
        if st.session_state.comparison_result is not None:
            display_results()
    
    else:
        st.info("👆 Please upload an eye image to begin the comparison.")


def process_and_compare():
    """Process uploaded image and perform comparison."""
    
    with st.spinner("Processing iris image..."):
        try:
            # Step 1: Segment iris
            st.write("**Step 1:** Segmenting iris...")
            segmented_roi, original_image, circle_info = segment_iris(
                st.session_state.uploaded_image
            )
            st.session_state.segmented_iris = segmented_roi
            
            # Display segmented iris
            col1, col2 = st.columns(2)
            with col1:
                st.image(segmented_roi, caption="Segmented Iris ROI", use_container_width=True)
            
            # Create sector map
            st.write("**Step 1b:** Creating sector map...")
            sector_map, sector_analysis = create_sector_map(segmented_roi)
            st.session_state.sector_map = sector_map
            
            with col2:
                st.image(sector_map, caption="Iris Sector Map", use_container_width=True)
            
            if circle_info['detected']:
                st.success(f"✅ Iris detected: Center={circle_info['center']}, Radius={circle_info['radius']}")
            else:
                st.warning("⚠️ Using fallback segmentation (center region)")
            
            # Step 2: Extract features
            st.write("**Step 2:** Extracting features...")
            features = extract_all_features(segmented_roi)
            st.session_state.features = features
            
            # Add sector analysis to features
            features['sector_analysis'] = sector_analysis
            
            # Display features
            with st.expander("📊 Extracted Features"):
                st.json(features)
            
            # Step 3: Compare with good iris
            st.write("**Step 3:** Comparing with reference baseline...")
            comparison_result = compare_iris(features, GOOD_IRIS_PATH)
            
            # Step 4: Validate (anti-hallucination guard)
            validated_result = validate_comparison_result(comparison_result)
            
            # Add symptom correlation
            if st.session_state.symptoms:
                validated_result['symptoms'] = st.session_state.symptoms
                validated_result['symptom_correlation'] = correlate_symptoms(
                    validated_result, 
                    st.session_state.symptoms,
                    sector_analysis
                )
            
            st.session_state.comparison_result = validated_result
            
            st.success("✅ Comparison complete!")
            
        except Exception as e:
            st.error(f"❌ Error during processing: {str(e)}")
            st.exception(e)


def correlate_symptoms(comparison_result, symptoms, sector_analysis):
    """Correlate visual anomalies with reported symptoms."""
    correlations = []
    
    score = comparison_result.get('score', 0)
    
    # Light sensitivity correlation
    if symptoms['light_sensitivity'] in ['Moderate', 'Severe']:
        if score > 40:
            correlations.append("Visual anomalies detected may correlate with reported light sensitivity.")
        if any(s.get('variation', 0) > 15 for s in sector_analysis.values()):
            correlations.append("Sector color variations detected, which may relate to light sensitivity.")
    
    # Vision blur correlation
    if symptoms['vision_blur'] in ['Moderate', 'Severe']:
        if score > 50:
            correlations.append("Structural differences detected may correlate with reported vision blur.")
    
    # Redness correlation
    if symptoms['redness'] in ['Moderate', 'Severe']:
        correlations.append("Eye redness reported. Visual analysis focuses on structural patterns only.")
    
    # Pain correlation
    if symptoms['pain'] in ['Moderate', 'Severe']:
        correlations.append("Eye pain reported. Recommend professional examination.")
    
    # Duration consideration
    if symptoms['duration'] in ['1-2 weeks', 'More than 2 weeks']:
        correlations.append("Symptoms persisting for extended period. Professional consultation strongly recommended.")
    
    if not correlations:
        correlations.append("No strong correlations found between visual analysis and reported symptoms.")
    
    return correlations


def display_results():
    """Display comparison results."""
    
    result = st.session_state.comparison_result
    
    st.header("📊 Comparison Results")
    
    # Score display
    score = result.get('score', 0.0)
    interpretation = result.get('interpretation', {})
    category = interpretation.get('category', 'Unknown')
    
    # Color code based on score
    if score <= 25:
        score_color = "🟢"
        bar_color = "green"
    elif score <= 60:
        score_color = "🟡"
        bar_color = "orange"
    else:
        score_color = "🔴"
        bar_color = "red"
    
    # Score card
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Difference Score", f"{score:.2f}/100", delta=None)
    
    with col2:
        st.metric("Category", category)
    
    with col3:
        st.metric("Status", score_color)
    
    # Progress bar
    st.progress(score / 100.0)
    
    # Interpretation
    st.subheader("📝 Interpretation")
    sanitized_message = result.get('sanitized_message', interpretation.get('description', ''))
    st.info(sanitized_message)
    
    # Detailed differences
    st.subheader("🔬 Detailed Feature Differences")
    
    differences = result.get('differences', {})
    
    if differences:
        # Create feature comparison table
        diff_data = {
            'Feature': [],
            'Difference Value': [],
            'Category': []
        }
        
        for key, value in differences.items():
            if key == 'sector_analysis':
                continue
            diff_data['Feature'].append(key)
            diff_data['Difference Value'].append(f"{value:.4f}")
            
            if 'mean' in key.lower() or 'h_' in key or 's_' in key or 'v_' in key:
                diff_data['Category'].append('Color')
            elif 'lbp' in key.lower() or 'contrast' in key.lower() or 'entropy' in key.lower() or 'homogeneity' in key.lower():
                diff_data['Category'].append('Texture')
            elif 'edge' in key.lower() or 'circular' in key.lower():
                diff_data['Category'].append('Contour')
            elif 'spot' in key.lower():
                diff_data['Category'].append('Spots')
            else:
                diff_data['Category'].append('Other')
        
        st.dataframe(diff_data, use_container_width=True)
    
    # Sector analysis
    if st.session_state.sector_map is not None:
        st.subheader("🎯 Sector Analysis")
        col1, col2 = st.columns(2)
        
        with col1:
            st.image(st.session_state.segmented_iris, caption="Original Segmented Iris", use_container_width=True)
        
        with col2:
            st.image(st.session_state.sector_map, caption="Processed Sector Map", use_container_width=True)
        
        # Display sector anomalies
        sector_analysis = st.session_state.features.get('sector_analysis', {})
        if sector_analysis:
            st.write("**Anomalies Found:**")
            for sector_name, sector_data in sector_analysis.items():
                variation = sector_data.get('variation', 0)
                if variation > 10:
                    st.warning(f"• {sector_name} shows {variation:.1f}% color variation")
                else:
                    st.success(f"• {sector_name} shows {variation:.1f}% color variation (normal)")
    
    # Symptom correlation
    if 'symptom_correlation' in result:
        st.subheader("🔗 Symptom Correlation")
        correlations = result.get('symptom_correlation', [])
        for correlation in correlations:
            st.info(f"• {correlation}")
        
        # Display symptoms
        if 'symptoms' in result:
            with st.expander("📋 Reported Symptoms"):
                symptoms = result['symptoms']
                st.write(f"**Pain Level:** {symptoms.get('pain', 'N/A')}")
                st.write(f"**Redness:** {symptoms.get('redness', 'N/A')}")
                st.write(f"**Vision Blur:** {symptoms.get('vision_blur', 'N/A')}")
                st.write(f"**Light Sensitivity:** {symptoms.get('light_sensitivity', 'N/A')}")
                st.write(f"**Duration:** {symptoms.get('duration', 'N/A')}")
    
    # Disclaimers
    st.subheader("⚠️ Important Disclaimers")
    disclaimers = result.get('disclaimers', [])
    for disclaimer in disclaimers:
        st.caption(f"• {disclaimer}")
    
    # PDF Report Generation
    st.subheader("📄 Generate PDF Report")
    
    if st.button("📥 Generate & Download PDF Report", type="primary"):
        with st.spinner("Generating PDF report..."):
            try:
                report_path = generate_pdf_report(
                    result,
                    st.session_state.uploaded_image,
                    None,  # Good iris image path (optional)
                    sector_map_path=st.session_state.sector_map if st.session_state.sector_map is not None else None,
                    output_path=f"reports/report_{Path(st.session_state.uploaded_image).stem}.pdf"
                )
                
                # Read PDF and create download button
                with open(report_path, "rb") as pdf_file:
                    PDFbyte = pdf_file.read()
                
                st.download_button(
                    label="⬇️ Download PDF Report",
                    data=PDFbyte,
                    file_name="iris_comparison_report.pdf",
                    mime="application/pdf"
                )
                
                st.success("✅ PDF report generated successfully!")
                
            except Exception as e:
                st.error(f"❌ Error generating PDF: {str(e)}")


def scanner_demo_page():
    """Scanner demo mode page with QR code."""
    
    st.header("📱 Scanner Demo Mode")
    
    st.info(
        "This mode allows judges or team members to scan a QR code to access the web version "
        "of the application on their mobile devices."
    )
    
    # Get current URL (for demo, use placeholder)
    # In production, this would be the actual deployed URL
    demo_url = st.text_input(
        "Application URL",
        value="https://your-app-url.streamlit.app",
        help="Enter the URL where your Streamlit app is deployed"
    )
    
    if demo_url:
        st.subheader("📲 QR Code for Mobile Access")
        
        # Generate QR code
        qr_img = generate_qr_code(demo_url)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(qr_img, caption="Scan with your phone to access the app", use_container_width=True)
        
        st.markdown("---")
        st.subheader("📋 Instructions")
        st.markdown("""
        1. **Display this QR code** on your screen
        2. **Open camera/QR scanner** on your mobile device
        3. **Scan the QR code** to open the web application
        4. **Upload iris image** and perform comparison
        5. **Share results** with team members or judges
        
        **Alternative:** Share the URL directly: `{url}`
        """.format(url=demo_url))
        
        # Copy URL button
        st.code(demo_url, language=None)
        if st.button("📋 Copy URL to Clipboard"):
            st.success("✅ URL copied! (Use Ctrl+V to paste)")


def live_scan_page():
    """Live scan page with camera access and image enhancement options."""
    st.header("📸 Live Scan Mode")
    
    st.info(
        "Use your device's camera to capture an iris image. "
        "Enable Macro Mode for close-up shots and High Contrast for dim lighting."
    )
    
    # Image enhancement options
    col1, col2 = st.columns(2)
    
    with col1:
        macro_mode = st.toggle(
            "📷 Macro Mode",
            help="Enable for close-up iris photography. Optimizes focus for near-distance shots."
        )
    
    with col2:
        high_contrast = st.toggle(
            "🔆 High Contrast Mode",
            help="Enable in dim lighting conditions. Enhances image contrast for better iris detection."
        )
    
    st.markdown("---")
    
    # Camera input
    st.subheader("📸 Capture Image")
    camera_image = st.camera_input(
        "Take a picture of the eye/iris",
        help="Position the camera close to the eye and ensure good lighting"
    )
    
    if camera_image is not None:
        # Save captured image
        import time
        timestamp = int(time.time())
        capture_path = Path("uploads") / f"camera_capture_{timestamp}.jpg"
        
        with open(capture_path, "wb") as f:
            f.write(camera_image.getbuffer())
        
        # Apply image enhancements if needed
        if high_contrast or macro_mode:
            enhanced_path = enhance_image(
                str(capture_path), 
                high_contrast=high_contrast,
                macro_mode=macro_mode
            )
            st.session_state.uploaded_image = enhanced_path
        else:
            st.session_state.uploaded_image = str(capture_path)
        
        # Display captured image
        st.subheader("📷 Captured Image")
        col1, col2 = st.columns(2)
        
        with col1:
            st.image(camera_image, caption="Original Capture", use_container_width=True)
        
        if high_contrast or macro_mode:
            with col2:
                st.image(st.session_state.uploaded_image, caption="Enhanced Image", use_container_width=True)
        
        # Symptom questionnaire
        st.markdown("---")
        symptoms = symptom_questionnaire()
        st.session_state.symptoms = symptoms
        
        # Process button
        if st.button("🔍 Process & Compare", type="primary"):
            process_and_compare()
        
        # Show results if available
        if st.session_state.comparison_result is not None:
            display_results()
    
    else:
        st.info("👆 Click the camera button above to capture an iris image.")
        
        # Tips for better capture
        with st.expander("💡 Tips for Better Capture"):
            st.markdown("""
            **For Best Results:**
            
            1. **Lighting**: Ensure adequate lighting on the eye
               - Use natural light when possible
               - Enable High Contrast mode in dim conditions
            
            2. **Distance**: Position camera 4-6 inches from the eye
               - Enable Macro Mode for close-up shots
               - Keep the eye centered in frame
            
            3. **Focus**: Ensure the iris is in sharp focus
               - Hold steady for 2-3 seconds
               - Avoid motion blur
            
            4. **Eye Position**: Look directly at the camera
               - Keep eye wide open
               - Avoid squinting
            
            5. **Hackathon Hall Lighting**: 
               - Hall lighting is often terrible!
               - Always enable High Contrast mode
               - Use phone flashlight as additional light source if needed
            """)


def enhance_image(image_path, high_contrast=False, macro_mode=False):
    """
    Enhance captured image based on selected modes.
    
    Args:
        image_path: Path to the captured image
        high_contrast: Enable high contrast enhancement
        macro_mode: Enable macro mode optimization
    
    Returns:
        str: Path to enhanced image
    """
    import cv2
    
    # Read image
    img = cv2.imread(image_path)
    if img is None:
        return image_path
    
    enhanced = img.copy()
    
    # High contrast enhancement for dim lighting
    if high_contrast:
        # Convert to LAB color space
        lab = cv2.cvtColor(enhanced, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        
        # Merge channels
        enhanced = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
    
    # Macro mode optimization
    if macro_mode:
        # Sharpen the image for better detail
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]])
        enhanced = cv2.filter2D(enhanced, -1, kernel)
        
        # Denoise while preserving edges
        enhanced = cv2.bilateralFilter(enhanced, 9, 75, 75)
    
    # Save enhanced image
    enhanced_path = image_path.replace('.jpg', '_enhanced.jpg')
    cv2.imwrite(enhanced_path, enhanced)
    
    return enhanced_path


def scanner_demo_page():
    """Scanner demo mode page with QR code."""
    
    st.header("📱 Scanner Demo Mode")
    
    st.info(
        "This mode allows judges or team members to scan a QR code to access the web version "
        "of the application on their mobile devices."
    )
    
    # Get current URL (for demo, use placeholder)
    # In production, this would be the actual deployed URL
    demo_url = st.text_input(
        "Application URL",
        value="https://your-app-url.streamlit.app",
        help="Enter the URL where your Streamlit app is deployed"
    )
    
    if demo_url:
        st.subheader("📲 QR Code for Mobile Access")
        
        # Generate QR code
        qr_img = generate_qr_code(demo_url)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(qr_img, caption="Scan with your phone to access the app", use_container_width=True)
        
        st.markdown("---")
        st.subheader("📋 Instructions")
        st.markdown("""
        1. **Display this QR code** on your screen
        2. **Open camera/QR scanner** on your mobile device
        3. **Scan the QR code** to open the web application
        4. **Upload iris image** and perform comparison
        5. **Share results** with team members or judges
        
        **Alternative:** Share the URL directly: `{url}`
        """.format(url=demo_url))
        
        # Copy URL button
        st.code(demo_url, language=None)
        if st.button("📋 Copy URL to Clipboard"):
            st.success("✅ URL copied! (Use Ctrl+V to paste)")


def about_page():
    """About page with application information."""
    
    st.header("ℹ️ About INDIAN IRIS")
    
    st.markdown("""
    ### 🎯 Project Overview
    
    **INDIAN IRIS** is a real-time iris comparison system designed as a **NON-DIAGNOSTIC** medical support tool.
    It compares a user's iris image with a pre-stored healthy iris baseline and generates a structural 
    difference score and comparison report.
    
    ### 🔬 How It Works
    
    1. **Iris Segmentation**: Uses OpenCV's Hough Circle Transform to detect and extract the iris region
    2. **Feature Extraction**: Extracts four categories of features:
       - **Color Features**: HSV mean values
       - **Texture Features**: LBP and GLCM-based metrics
       - **Contour Metrics**: Edge deviation and circular variance
       - **Spot Detection**: Pigment-like anomaly detection
    3. **Comparison**: Calculates pixel-level differences with a reference healthy iris
    4. **Scoring**: Generates a 0-100 difference score with interpretation
    5. **Reporting**: Creates a comprehensive PDF report
    
    ### 🛡️ Safety Features
    
    - **Anti-Hallucination Guard**: Prevents AI from making diagnostic claims
    - **Noise Threshold**: Filters out meaningless differences
    - **Strict Disclaimers**: Clear non-diagnostic messaging
    - **Scientific Approach**: Only measures real pixel-level differences
    
    ### ⚠️ Important Disclaimers
    
    - This tool does **NOT** diagnose diseases
    - It does **NOT** predict health outcomes
    - It does **NOT** provide medical interpretations
    - Results are for **informational purposes only**
    - Always consult qualified healthcare professionals
    
    ### 📚 Technical Stack
    
    - **Frontend**: Streamlit
    - **Image Processing**: OpenCV, scikit-image
    - **Feature Extraction**: NumPy, scikit-learn
    - **Report Generation**: ReportLab
    - **QR Code**: qrcode library
    
    ### 👥 Usage
    
    1. Upload an eye/iris image
    2. System automatically segments the iris
    3. Features are extracted and compared
    4. View results and download PDF report
    5. Share with healthcare professionals if needed
    
    ### 📞 Support
    
    For questions or issues, please refer to the project documentation or contact the development team.
    """)


if __name__ == "__main__":
    main()
