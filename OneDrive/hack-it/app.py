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
if 'ml_prediction' not in st.session_state:
    st.session_state.ml_prediction = None

# Initialize ML predictor
@st.cache_resource
def load_ml_predictor():
    """Load ML/DL models (cached)."""
    try:
        from utils.ml_predictor import IrisHealthPredictor
        predictor = IrisHealthPredictor()
        # Check if any models are loaded
        if predictor.ml_model is None and predictor.dl_model is None:
            return None
        return predictor
    except Exception as e:
        st.warning(f"ML models not available: {str(e)}")
        return None

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
    
    # Convert PIL Image to bytes for Streamlit
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf


def getting_started_page():
    """Getting started page with introduction and navigation."""
    st.header("👋 Welcome to INDIAN IRIS")
    
    st.markdown("""
    ### Your Advanced Iris Health Analysis System
    
    INDIAN IRIS is a cutting-edge AI-powered application that analyzes iris images to provide 
    comprehensive health assessments with explainable AI technology.
    """)
    
    # Feature highlights
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🤖 AI-Powered")
        st.write("Advanced ML/DL models with SHAP explainable AI")
    
    with col2:
        st.markdown("### 📊 Comprehensive")
        st.write("Detailed sector analysis and feature extraction")
    
    with col3:
        st.markdown("### 📄 Professional")
        st.write("Generate PDF reports for healthcare professionals")
    
    st.markdown("---")
    
    # Quick start guide
    st.subheader("🚀 Quick Start Guide")
    
    st.markdown("""
    **Step 1:** Learn about eye conditions
    - Click "Eye Diseases Info" to understand various eye conditions
    - Know the symptoms to watch for
    
    **Step 2:** Capture or upload an iris image
    - Use "Live Scan" for real-time camera capture
    - Or "Upload & Compare" to analyze existing images
    
    **Step 3:** Complete the assessment
    - Fill in patient information
    - Answer symptom questionnaire
    - Get AI-powered analysis with SHAP explanations
    
    **Step 4:** Review and share results
    - View detailed analysis with sector heatmaps
    - Generate professional PDF reports
    - Submit to healthcare professionals
    """)
    
    st.markdown("---")
    
    # Call to action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📚 Learn About Eye Diseases", type="primary", width="stretch"):
            st.session_state.navigate_to = "Eye Diseases Info"
            st.rerun()
    
    with col2:
        if st.button("📸 Start Live Scan", type="secondary", width="stretch"):
            st.session_state.navigate_to = "Live Scan"
            st.rerun()
    
    with col3:
        if st.button("📤 Upload Image", type="secondary", width="stretch"):
            st.session_state.navigate_to = "Upload & Compare"
            st.rerun()
    
    st.markdown("---")
    
    # Important disclaimer
    st.warning(
        "⚠️ **IMPORTANT:** This is a screening tool, not a diagnostic device. "
        "Always consult qualified healthcare professionals for medical diagnosis and treatment."
    )


def eye_diseases_page():
    """Eye diseases information page."""
    from utils.eye_diseases_data import EYE_DISEASES, DISEASE_CATEGORIES
    
    st.header("📚 Eye Diseases Information")
    
    st.markdown("""
    ### Understanding Eye Conditions
    
    Eye conditions, however big or small, need timely attention and adequate care. 
    Learn about various eye conditions, symptoms to watch for, and treatment options.
    """)
    
    st.markdown("---")
    
    # Search and filter
    search_term = st.text_input("🔍 Search for a condition", placeholder="Type condition name...")
    
    # Category filter
    selected_category = st.selectbox(
        "Filter by Category",
        ["All Conditions"] + list(DISEASE_CATEGORIES.keys())
    )
    
    st.markdown("---")
    
    # Display diseases by category
    if selected_category == "All Conditions":
        # Show all diseases
        if search_term:
            filtered_diseases = {k: v for k, v in EYE_DISEASES.items() 
                               if search_term.lower() in k.lower()}
        else:
            filtered_diseases = EYE_DISEASES
        
        # Display in grid
        diseases_list = list(filtered_diseases.items())
        for i in range(0, len(diseases_list), 2):
            col1, col2 = st.columns(2)
            
            with col1:
                if i < len(diseases_list):
                    name, info = diseases_list[i]
                    with st.expander(f"{info['icon']} {name}"):
                        st.write(f"**Severity:** {info['severity']}")
                        st.write(f"**Treatment:** {info['treated']}")
                        st.write(f"\n{info['description']}")
            
            with col2:
                if i + 1 < len(diseases_list):
                    name, info = diseases_list[i + 1]
                    with st.expander(f"{info['icon']} {name}"):
                        st.write(f"**Severity:** {info['severity']}")
                        st.write(f"**Treatment:** {info['treated']}")
                        st.write(f"\n{info['description']}")
    else:
        # Show diseases in selected category
        st.subheader(f"📋 {selected_category}")
        
        diseases_in_category = DISEASE_CATEGORIES[selected_category]
        
        for disease_name in diseases_in_category:
            if disease_name in EYE_DISEASES:
                info = EYE_DISEASES[disease_name]
                
                if search_term and search_term.lower() not in disease_name.lower():
                    continue
                
                with st.expander(f"{info['icon']} {disease_name}"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(info['description'])
                    
                    with col2:
                        st.metric("Severity", info['severity'])
                        st.caption(info['treated'])
    
    st.markdown("---")
    
    # Statistics
    st.subheader("📊 Condition Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Conditions", len(EYE_DISEASES))
    
    with col2:
        emergency_count = len([d for d in EYE_DISEASES.values() if d['severity'] in ['Emergency', 'Life-threatening', 'Urgent']])
        st.metric("Emergency Conditions", emergency_count)
    
    with col3:
        common_count = len([d for d in EYE_DISEASES.values() if d['severity'] in ['Common', 'Very Common']])
        st.metric("Common Conditions", common_count)
    
    st.markdown("---")
    
    # Call to action
    st.info("💡 **Ready to analyze your iris?** Use our AI-powered scanning tool to get a comprehensive assessment.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📸 Start Live Scan", type="primary", width="stretch"):
            st.session_state.navigate_to = "Live Scan"
            st.rerun()
    
    with col2:
        if st.button("📤 Upload Image", type="secondary", width="stretch"):
            st.session_state.navigate_to = "Upload & Compare"
            st.rerun()


def main():
    """Main application function."""
    
    # Custom CSS for horizontal navbar
    st.markdown("""
    <style>
    /* Hide default sidebar */
    [data-testid="stSidebar"] {
        display: none;
    }
    
    /* Navbar styling */
    .navbar {
        background-color: #1f4788;
        padding: 1rem 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
        border-radius: 10px;
    }
    
    .navbar-brand {
        color: white;
        font-size: 1.8rem;
        font-weight: bold;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .navbar-links {
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
    }
    
    .stButton button {
        background-color: transparent;
        color: white;
        border: 2px solid white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s;
    }
    
    .stButton button:hover {
        background-color: white;
        color: #1f4788;
    }
    
    /* Active page styling */
    div[data-testid="stHorizontalBlock"] > div {
        padding: 0 0.25rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state for page navigation
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Getting Started"
    
    # Check if navigation was triggered
    if 'navigate_to' in st.session_state:
        st.session_state.current_page = st.session_state.navigate_to
        del st.session_state.navigate_to
    
    # Horizontal Navbar
    navbar_col1, navbar_col2 = st.columns([1, 3])
    
    with navbar_col1:
        st.markdown('<div class="navbar-brand">👁️ INDIAN IRIS</div>', unsafe_allow_html=True)
    
    with navbar_col2:
        nav_cols = st.columns(6)
        
        with nav_cols[0]:
            if st.button("🏠 Home", key="nav_home"):
                st.session_state.current_page = "Getting Started"
                st.rerun()
        
        with nav_cols[1]:
            if st.button("📚 Eye Diseases", key="nav_diseases"):
                st.session_state.current_page = "Eye Diseases Info"
                st.rerun()
        
        with nav_cols[2]:
            if st.button("📤 Upload", key="nav_upload"):
                st.session_state.current_page = "Upload & Compare"
                st.rerun()
        
        with nav_cols[3]:
            if st.button("📸 Live Scan", key="nav_live"):
                st.session_state.current_page = "Live Scan"
                st.rerun()
        
        with nav_cols[4]:
            if st.button("📱 Demo", key="nav_demo"):
                st.session_state.current_page = "Scanner Demo Mode"
                st.rerun()
        
        with nav_cols[5]:
            if st.button("ℹ️ About", key="nav_about"):
                st.session_state.current_page = "About"
                st.rerun()
    
    st.markdown("---")
    
    # Header
    st.title("👁️ INDIAN IRIS")
    st.markdown("### Real-Time Iris Comparison System")
    
    # Important disclaimer
    st.warning(
        "⚠️ **NON-DIAGNOSTIC TOOL**: This application measures pixel-level structural differences only. "
        "It does NOT diagnose diseases, predict health outcomes, or provide medical interpretations. "
        "Results are for informational purposes only. Always consult qualified healthcare professionals."
    )
    
    # Route to appropriate page based on current_page
    page = st.session_state.current_page
    
    if page == "Getting Started":
        getting_started_page()
    elif page == "Eye Diseases Info":
        eye_diseases_page()
    elif page == "Upload & Compare":
        upload_and_compare_page()
    elif page == "Live Scan":
        live_scan_page()
    elif page == "Scanner Demo Mode":
        scanner_demo_page()
    else:
        about_page()


def symptom_questionnaire():
    """Display comprehensive medical questionnaire and return responses."""
    from utils.medical_questionnaire import render_medical_questionnaire, display_questionnaire_summary
    
    st.markdown("---")
    questionnaire_data = render_medical_questionnaire()
    
    # Display summary
    if st.button("📋 Review Summary", key="review_summary"):
        display_questionnaire_summary(questionnaire_data)
    
    return questionnaire_data


def patient_information_form():
    """Collect patient information for the report."""
    st.subheader("👤 Patient Information")
    st.info("Please provide your information for the medical report.")
    
    patient_info = {}
    
    col1, col2 = st.columns(2)
    
    with col1:
        patient_info['name'] = st.text_input("Full Name", placeholder="John Doe")
        patient_info['age'] = st.number_input("Age", min_value=1, max_value=120, value=30)
        patient_info['gender'] = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to say"])
    
    with col2:
        patient_info['contact'] = st.text_input("Contact Number", placeholder="+1234567890")
        patient_info['email'] = st.text_input("Email Address", placeholder="patient@example.com")
        patient_info['date'] = st.date_input("Date of Examination").strftime("%Y-%m-%d")
    
    return patient_info


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
        st.subheader("📷 Image Comparison")
        col1, col2 = st.columns(2)
        
        # LEFT: Reference good iris (if exists)
        with col1:
            st.markdown("**Reference Healthy Iris (Baseline)**")
            reference_img_path = "reference/good_iris_reference.jpg"
            if Path(reference_img_path).exists():
                st.image(reference_img_path, caption="Healthy Iris Reference", use_container_width=True)
            else:
                st.info("📌 Reference image not set. Upload a healthy iris image to 'reference/good_iris_reference.jpg'")
        
        # RIGHT: User's uploaded image
        with col2:
            st.markdown("**Your Iris Image (For Analysis)**")
            st.image(uploaded_file, caption="Your Uploaded Image", use_container_width=True)
        
        # Patient information
        st.markdown("---")
        patient_info = patient_information_form()
        st.session_state.patient_info = patient_info
        
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
            st.subheader("🔬 Segmented Iris Comparison")
            col1, col2 = st.columns(2)
            
            # LEFT: Reference segmented iris (if exists)
            with col1:
                st.markdown("**Reference Iris (Segmented)**")
                reference_segmented_path = "reference/good_iris_segmented.jpg"
                if Path(reference_segmented_path).exists():
                    st.image(reference_segmented_path, caption="Healthy Iris ROI", use_container_width=True)
                else:
                    # Show placeholder or info
                    st.info("Reference segmented iris")
            
            # RIGHT: User's segmented iris
            with col2:
                st.markdown("**Your Iris (Segmented)**")
                st.image(segmented_roi, caption="Your Iris ROI", use_container_width=True)
            
            # Create sector map
            st.write("**Step 1b:** Creating sector map...")
            sector_map, sector_analysis = create_sector_map(segmented_roi)
            st.session_state.sector_map = sector_map
            
            st.subheader("🎯 Sector Map Comparison")
            col1, col2 = st.columns(2)
            
            # LEFT: Reference sector map (if exists)
            with col1:
                st.markdown("**Reference Sector Map**")
                reference_sector_path = "reference/good_iris_sector_map.jpg"
                if Path(reference_sector_path).exists():
                    st.image(reference_sector_path, caption="Healthy Iris Sectors", use_container_width=True)
                else:
                    st.info("Reference sector map")
            
            # RIGHT: User's sector map
            with col2:
                st.markdown("**Your Sector Map**")
                st.image(sector_map, caption="Your Iris Sectors", use_container_width=True)
            
            if circle_info['detected']:
                st.success(f"✅ Iris detected: Center={circle_info['center']}, Radius={circle_info['radius']}")
            else:
                st.warning("⚠️ Using fallback segmentation (center region)")
            
            # Step 2: ML/DL Health Prediction with SHAP
            st.write("**Step 2:** Running ML/DL health analysis with SHAP explanations...")
            predictor = load_ml_predictor()
            
            if predictor is not None:
                ml_result = predictor.calculate_health_score_with_shap(segmented_roi)
                st.session_state.ml_prediction = ml_result
                
                if ml_result:
                    st.success(f"✅ ML/DL Analysis Complete - Health Score: {ml_result['health_score']:.1f}/100")
                    
                    # Display ML prediction
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("ML Prediction", ml_result.get('ml_prediction', 'N/A'))
                    with col2:
                        st.metric("DL Prediction", ml_result.get('dl_prediction', 'N/A'))
                    with col3:
                        st.metric("Health Category", ml_result['category'])
                    
                    # SHAP status
                    if ml_result.get('shap_available', False):
                        st.info("✅ SHAP Explainable AI analysis included")
                    else:
                        st.info("ℹ️ SHAP explanations not available (library may not be installed)")
            else:
                st.info("ℹ️ ML/DL models not available. Using traditional feature comparison.")
            
            # Step 3: Extract features
            st.write("**Step 3:** Extracting features...")
            features = extract_all_features(segmented_roi)
            st.session_state.features = features
            
            # Add sector analysis to features
            features['sector_analysis'] = sector_analysis
            
            # Display features
            with st.expander("📊 Extracted Features"):
                st.json(features)
            
            # Step 4: Compare with good iris
            st.write("**Step 4:** Comparing with reference baseline...")
            comparison_result = compare_iris(features, GOOD_IRIS_PATH)
            
            # Step 5: Validate (anti-hallucination guard)
            validated_result = validate_comparison_result(comparison_result)
            
            # Add ML prediction to result
            if st.session_state.ml_prediction:
                validated_result['ml_prediction'] = st.session_state.ml_prediction
            
            # Add symptom correlation
            if st.session_state.symptoms:
                from utils.medical_questionnaire import generate_clinical_correlation
                
                validated_result['symptoms'] = st.session_state.symptoms
                validated_result['symptom_correlation'] = generate_clinical_correlation(
                    st.session_state.symptoms,
                    validated_result
                )
            
            st.session_state.comparison_result = validated_result
            
            st.success("✅ Complete analysis finished!")
            
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
    
    # ML/DL Prediction Results (if available)
    if 'ml_prediction' in result and result['ml_prediction']:
        st.subheader("🤖 AI Health Analysis")
        
        ml_pred = result['ml_prediction']
        health_score = ml_pred['health_score']
        
        # Health score visualization
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Health Score", f"{health_score:.1f}/100")
        
        with col2:
            st.metric("Category", ml_pred['category'])
        
        with col3:
            st.metric("ML Model", ml_pred.get('ml_prediction', 'N/A'))
        
        with col4:
            st.metric("DL Model", ml_pred.get('dl_prediction', 'N/A'))
        
        # Progress bar for health score
        if health_score <= 40:
            bar_color = "green"
        elif health_score <= 70:
            bar_color = "orange"
        else:
            bar_color = "red"
        
        st.progress(health_score / 100.0)
        
        # AI Recommendation
        st.info(f"**AI Recommendation:** {ml_pred['recommendation']}")
        
        # Confidence breakdown
        with st.expander("🔍 Detailed AI Analysis"):
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Probability Breakdown:**")
                st.write(f"• Healthy: {ml_pred['probabilities']['healthy']*100:.1f}%")
                st.write(f"• Unhealthy: {ml_pred['probabilities']['unhealthy']*100:.1f}%")
            with col2:
                st.write(f"**Confidence:** {ml_pred['confidence']*100:.1f}%")
                st.write(f"**Final Prediction:** {ml_pred['prediction_class']}")
        
        # SHAP Explainable AI Section
        if ml_pred.get('shap_available', False) and 'shap_data' in ml_pred:
            st.markdown("---")
            st.subheader("🔍 SHAP Explainable AI Analysis")
            
            st.info(
                "**What is SHAP?** SHAP (SHapley Additive exPlanations) shows which features "
                "influenced the AI's prediction. This makes the AI's decision-making transparent and trustworthy."
            )
            
            # SHAP Heatmap
            if 'sector_scores' in ml_pred and st.session_state.segmented_iris is not None:
                try:
                    from utils.shap_explainer import HeatmapGenerator
                    import tempfile
                    
                    # Generate heatmap
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                        heatmap_path = tmp.name
                    
                    HeatmapGenerator.create_sector_heatmap(
                        st.session_state.segmented_iris,
                        ml_pred['sector_scores'],
                        heatmap_path
                    )
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Original Iris**")
                        st.image(st.session_state.segmented_iris, use_container_width=True)
                    
                    with col2:
                        st.write("**SHAP Importance Heatmap**")
                        st.image(heatmap_path, use_container_width=True)
                    
                    st.caption("🔴 Red = High importance | 🟡 Yellow = Moderate | 🟢 Green = Low")
                    
                    # Sector importance table
                    st.write("**Sector Importance Scores:**")
                    sector_data = []
                    for sector, score in ml_pred['sector_scores'].items():
                        if score >= 0.7:
                            color = "🔴 High"
                        elif score >= 0.4:
                            color = "🟡 Moderate"
                        else:
                            color = "🟢 Low"
                        sector_data.append({
                            'Sector': sector,
                            'Importance': f"{score:.3f}",
                            'Level': color
                        })
                    
                    st.dataframe(sector_data, use_container_width=True)
                
                except Exception as e:
                    st.warning(f"Could not generate SHAP heatmap: {str(e)}")
            
            # Feature importance chart
            try:
                from utils.shap_explainer import HeatmapGenerator
                import tempfile
                
                shap_data = ml_pred['shap_data']
                shap_values = np.array(shap_data['shap_values'])
                feature_names = shap_data['feature_names']
                
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                    chart_path = tmp.name
                
                HeatmapGenerator.create_feature_importance_chart(
                    shap_values,
                    feature_names,
                    chart_path,
                    top_n=15
                )
                
                st.write("**Top 15 Feature Contributions:**")
                st.image(chart_path, use_container_width=True)
                st.caption("Red bars increase health concern score, blue bars decrease it")
            
            except Exception as e:
                st.warning(f"Could not generate feature importance chart: {str(e)}")
            
            # SHAP summary statistics
            with st.expander("📊 SHAP Summary Statistics"):
                abs_shap = np.abs(shap_values)
                total_magnitude = float(np.sum(abs_shap))
                positive_count = int(np.sum(shap_values > 0))
                negative_count = int(np.sum(shap_values < 0))
                most_important_idx = int(np.argmax(abs_shap))
                most_important_feature = feature_names[most_important_idx]
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Magnitude", f"{total_magnitude:.4f}")
                    st.metric("Features Increasing Score", positive_count)
                with col2:
                    st.metric("Features Decreasing Score", negative_count)
                    st.metric("Base Value", f"{shap_data['base_value']:.4f}")
                with col3:
                    st.write(f"**Most Important:**")
                    st.write(f"{most_important_feature}")
                    if 'sector_scores' in ml_pred:
                        most_important_sector = max(ml_pred['sector_scores'].items(), key=lambda x: x[1])[0]
                        st.write(f"**Key Sector:** {most_important_sector}")
        
        st.markdown("---")
    
    # Traditional comparison score
    st.subheader("📈 Traditional Feature Comparison")
    
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
        st.subheader("🎯 Sector Analysis Comparison")
        col1, col2 = st.columns(2)
        
        # LEFT: Reference images
        with col1:
            st.markdown("**Reference Healthy Iris**")
            
            # Original reference
            reference_img_path = "reference/good_iris_reference.jpg"
            if Path(reference_img_path).exists():
                st.image(reference_img_path, caption="Healthy Iris", use_container_width=True)
            
            # Reference sector map
            reference_sector_path = "reference/good_iris_sector_map.jpg"
            if Path(reference_sector_path).exists():
                st.image(reference_sector_path, caption="Healthy Sector Map", use_container_width=True)
        
        # RIGHT: User's images
        with col2:
            st.markdown("**Your Iris Analysis**")
            
            # User's segmented iris
            st.image(st.session_state.segmented_iris, caption="Your Segmented Iris", use_container_width=True)
            
            # User's sector map
            st.image(st.session_state.sector_map, caption="Your Sector Map", use_container_width=True)
        
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
        st.subheader("🔗 Clinical Symptom Correlation")
        
        # Display questionnaire summary
        if 'symptoms' in result:
            from utils.medical_questionnaire import display_questionnaire_summary
            display_questionnaire_summary(result['symptoms'])
        
        st.markdown("---")
        st.markdown("**Clinical Correlations:**")
        correlations = result.get('symptom_correlation', [])
        for correlation in correlations:
            if "CRITICAL" in correlation:
                st.error(f"• {correlation}")
            elif "⚠️" in correlation:
                st.warning(f"• {correlation}")
            else:
                st.info(f"• {correlation}")
    
    # Disclaimers
    st.subheader("⚠️ Important Disclaimers")
    disclaimers = result.get('disclaimers', [])
    for disclaimer in disclaimers:
        st.caption(f"• {disclaimer}")
    
    # PDF Report Generation
    st.subheader("📄 Generate PDF Report")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Generate & Download PDF Report", type="primary"):
            with st.spinner("Generating PDF report..."):
                try:
                    # Get patient info
                    patient_info = st.session_state.get('patient_info', {})
                    if result.get('ml_prediction'):
                        patient_info['ai_score'] = result['ml_prediction']['health_score']
                    patient_info['score'] = result.get('score', 0)
                    patient_info['category'] = result.get('interpretation', {}).get('category', 'Unknown')
                    
                    report_path = generate_pdf_report(
                        result,
                        st.session_state.uploaded_image,
                        None,  # Good iris image path (optional)
                        sector_map_path=st.session_state.sector_map if st.session_state.sector_map is not None else None,
                        patient_info=patient_info,
                        output_path=f"reports/report_{Path(st.session_state.uploaded_image).stem}.pdf"
                    )
                    
                    # Read PDF and create download button
                    with open(report_path, "rb") as pdf_file:
                        PDFbyte = pdf_file.read()
                    
                    st.download_button(
                        label="⬇️ Download PDF Report",
                        data=PDFbyte,
                        file_name="iris_analysis_report.pdf",
                        mime="application/pdf"
                    )
                    
                    st.success("✅ PDF report generated successfully!")
                    st.session_state.report_path = report_path
                    
                except Exception as e:
                    st.error(f"❌ Error generating PDF: {str(e)}")
    
    with col2:
        if st.session_state.get('report_path'):
            if st.button("📧 Submit Report to Doctor", type="secondary"):
                st.session_state.show_doctor_form = True
    
    # Doctor submission form
    if st.session_state.get('show_doctor_form', False):
        st.markdown("---")
        st.subheader("📧 Submit Report to Doctor")
        
        with st.form("doctor_submission_form"):
            st.write("Enter doctor's information to send the report via email:")
            
            col1, col2 = st.columns(2)
            
            with col1:
                doctor_name = st.text_input("Doctor's Name", placeholder="Dr. Smith")
                doctor_email = st.text_input("Doctor's Email", placeholder="doctor@hospital.com")
            
            with col2:
                doctor_specialty = st.selectbox(
                    "Specialty",
                    ["Ophthalmologist", "Optometrist", "General Practitioner", "Other"]
                )
                additional_notes = st.text_area("Additional Notes (Optional)", placeholder="Any specific concerns or questions...")
            
            submit_button = st.form_submit_button("Send Report to Doctor")
            
            if submit_button:
                if not doctor_email:
                    st.error("Please enter doctor's email address")
                else:
                    from utils.doctor_submission import send_report_to_doctor, save_doctor_submission_record
                    
                    # Prepare patient info for email
                    patient_info = st.session_state.get('patient_info', {})
                    patient_info['score'] = result.get('score', 0)
                    patient_info['category'] = result.get('interpretation', {}).get('category', 'Unknown')
                    if result.get('ml_prediction'):
                        patient_info['ai_score'] = f"{result['ml_prediction']['health_score']:.1f}"
                    
                    # Note: Email sending requires SMTP configuration
                    st.info("📧 Email submission feature requires SMTP configuration.")
                    st.info(f"Report would be sent to: {doctor_email}")
                    st.info("For production use, please configure SMTP settings in the application.")
                    
                    # Save submission record
                    save_doctor_submission_record(
                        st.session_state.report_path,
                        doctor_email,
                        patient_info
                    )
                    
                    st.success(f"✅ Submission recorded! Report details saved for {doctor_name} ({doctor_email})")
                    st.balloons()


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
