"""
Comprehensive Medical Questionnaire Module
Hospital-grade symptom assessment following EMR standards
"""

import streamlit as st


def render_medical_questionnaire():
    """
    Render comprehensive medical questionnaire with hospital-style inputs.
    Returns dictionary with all collected data.
    """
    st.markdown("### 📋 Medical Assessment Form")
    st.info("💡 This helps us understand your eye health better. Answer what you can - you can skip questions if unsure.")
    
    questionnaire_data = {}
    
    # ============================================================================
    # SECTION 1: Current Symptoms
    # ============================================================================
    st.markdown("---")
    st.markdown("#### 👁️ Current Eye Symptoms")
    st.caption("Tell us what you're experiencing right now")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Do you have eye pain?**")
        questionnaire_data['eye_pain'] = st.radio(
            "How bad is it?",
            ["No pain", "Mild (slight discomfort)", "Moderate (noticeable)", "Severe (very painful)"],
            key="eye_pain",
            horizontal=False,
            label_visibility="collapsed",
            help="Choose the level that best describes your pain"
        )
        
        st.markdown("**Is your eye red?**")
        questionnaire_data['redness'] = st.radio(
            "How red?",
            ["Not red", "Slightly pink", "Moderately red", "Very red"],
            key="redness",
            horizontal=False,
            label_visibility="collapsed",
            help="Look in a mirror and compare to your normal eye color"
        )
    
    with col2:
        st.markdown("**Is your vision blurry?**")
        questionnaire_data['vision_blur'] = st.radio(
            "How often?",
            ["Clear vision", "Sometimes blurry", "Always blurry", "Suddenly became blurry"],
            key="vision_blur",
            horizontal=False,
            label_visibility="collapsed",
            help="Think about the last few days"
        )
        
        st.markdown("**Are lights bothering you?**")
        questionnaire_data['light_sensitivity'] = st.radio(
            "How sensitive?",
            ["Lights are fine", "Slightly bothered", "Very bothered", "Can't tolerate light"],
            key="light_sensitivity",
            horizontal=False,
            label_visibility="collapsed",
            help="Do you need to wear sunglasses indoors?"
        )
    
    # Additional symptoms in expandable section
    with st.expander("➕ More Symptoms (Optional)"):
        col1, col2 = st.columns(2)
        
        with col1:
            questionnaire_data['tearing'] = st.radio(
                "**Watery eyes?**",
                ["No", "A little", "Very watery"],
                key="tearing",
                horizontal=True
            )
            
            questionnaire_data['itching'] = st.radio(
                "**Itchy eyes?**",
                ["No", "A little itchy", "Very itchy"],
                key="itching",
                horizontal=True
            )
        
        with col2:
            questionnaire_data['foreign_body'] = st.radio(
                "**Feels like something in your eye?**",
                ["No", "Yes"],
                key="foreign_body",
                horizontal=True
            )
            
            questionnaire_data['dryness'] = st.radio(
                "**Dry eyes?**",
                ["No", "A little dry", "Moderately dry", "Very dry"],
                key="dryness",
                horizontal=True
            )
    
    # ============================================================================
    # SECTION 2: Vision Changes
    # ============================================================================
    st.markdown("---")
    st.markdown("#### 🔍 Vision Changes")
    st.caption("Have you noticed any of these?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        questionnaire_data['floaters'] = st.radio(
            "**Floaters** (dark spots or strings floating in vision)",
            ["No floaters", "A few (normal)", "Many new ones", "⚠️ Sudden shower of floaters"],
            key="floaters",
            help="Floaters are normal, but sudden increase needs attention"
        )
        
        questionnaire_data['flashes'] = st.radio(
            "**Flashes of light** (like camera flash)",
            ["No flashes", "Occasionally", "Frequently"],
            key="flashes",
            horizontal=True
        )
    
    with col2:
        questionnaire_data['double_vision'] = st.radio(
            "**Seeing double?**",
            ["No", "Yes - side by side", "Yes - up and down"],
            key="double_vision",
            horizontal=True
        )
        
        questionnaire_data['halos'] = st.radio(
            "**Halos around lights?** (rainbow circles)",
            ["No", "Sometimes", "Always"],
            key="halos",
            horizontal=True
        )
    
    # ============================================================================
    # SECTION 3: Timeline
    # ============================================================================
    st.markdown("---")
    st.markdown("#### ⏱️ When Did This Start?")
    
    questionnaire_data['duration'] = st.selectbox(
        "How long have you had these symptoms?",
        [
            "Just today",
            "2-3 days ago",
            "About a week ago",
            "About 2 weeks ago",
            "More than a month"
        ],
        key="duration",
        help="Pick the closest timeframe"
    )
    
    questionnaire_data['affected_eye'] = st.radio(
        "**Which eye has the problem?**",
        ["Right eye only", "Left eye only", "Both eyes"],
        key="affected_eye",
        horizontal=True
    )
    
    # ============================================================================
    # SECTION 4: Recent Events
    # ============================================================================
    st.markdown("---")
    st.markdown("#### 🤕 Did Anything Happen Recently?")
    st.caption("Select all that apply (last 2 weeks)")
    
    recent_events_options = {
        "Nothing unusual": "None",
        "Poked or injured my eye": "Eye injury",
        "Got chemicals in my eye": "Chemical exposure",
        "Been rubbing my eye a lot": "Rubbing eye frequently",
        "Had a cold or fever": "Recent infection or fever",
        "Wore contact lenses too long": "Contact lens overuse"
    }
    
    selected_events = st.multiselect(
        "Recent events",
        list(recent_events_options.keys()),
        key="recent_events",
        label_visibility="collapsed"
    )
    questionnaire_data['recent_events'] = [recent_events_options[e] for e in selected_events]
    
    # ============================================================================
    # SECTION 5: Your Health History
    # ============================================================================
    st.markdown("---")
    st.markdown("#### 🏥 Your Health History")
    st.caption("This helps us understand your overall health")
    
    with st.expander("📊 Medical Conditions", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            questionnaire_data['diabetes'] = st.radio(
                "**Do you have diabetes?**",
                ["No", "Yes", "Pre-diabetic (borderline)"],
                key="diabetes",
                help="High blood sugar can affect eyes"
            )
            
            questionnaire_data['hypertension'] = st.radio(
                "**Do you have high blood pressure?**",
                ["No", "Yes"],
                key="hypertension",
                horizontal=True
            )
        
        with col2:
            questionnaire_data['thyroid'] = st.radio(
                "**Any thyroid problems?**",
                ["No", "Yes"],
                key="thyroid",
                horizontal=True
            )
            
            questionnaire_data['autoimmune'] = st.radio(
                "**Any autoimmune disease?** (like lupus, arthritis)",
                ["No", "Yes"],
                key="autoimmune",
                horizontal=True
            )
    
    with st.expander("👁️ Previous Eye Treatments"):
        questionnaire_data['eye_surgeries'] = st.multiselect(
            "Have you had any eye surgery?",
            ["LASIK (vision correction)", "Cataract surgery", "Glaucoma surgery", "Retinal surgery", "Other surgery", "No surgeries"],
            key="eye_surgeries"
        )
        
        questionnaire_data['family_history'] = st.multiselect(
            "Does anyone in your family have eye problems?",
            ["Glaucoma", "Eye inflammation (uveitis)", "Macular degeneration", "Cataracts", "No family history"],
            key="family_history"
        )
    
    # ============================================================================
    # SECTION 6: Daily Habits
    # ============================================================================
    st.markdown("---")
    st.markdown("#### 💊 Medications & Daily Habits")
    
    with st.expander("💊 Medications & Lifestyle", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            questionnaire_data['steroid_drops'] = st.radio(
                "**Using steroid eye drops?**",
                ["No", "Yes"],
                key="steroid_drops",
                horizontal=True,
                help="Prescription drops for inflammation"
            )
            
            questionnaire_data['contact_lenses'] = st.radio(
                "**Wear contact lenses daily?**",
                ["No", "Yes"],
                key="contact_lenses",
                horizontal=True
            )
            
            questionnaire_data['smoking'] = st.radio(
                "**Smoking status**",
                ["Never smoked", "Used to smoke", "Currently smoke"],
                key="smoking"
            )
        
        with col2:
            questionnaire_data['screen_time'] = st.selectbox(
                "**Daily screen time** (phone, computer, TV)",
                ["Less than 2 hours", "2-4 hours", "4-6 hours", "6-8 hours", "More than 8 hours"],
                key="screen_time"
            )
            
            questionnaire_data['allergies'] = st.text_input(
                "**Any allergies?** (optional)",
                placeholder="e.g., pollen, dust, pet dander",
                key="allergies"
            )
            
            questionnaire_data['long_term_meds'] = st.text_input(
                "**Regular medications?** (optional)",
                placeholder="e.g., blood pressure pills, diabetes meds",
                key="long_term_meds"
            )
    
    # ============================================================================
    # SECTION 7: Anything Else?
    # ============================================================================
    st.markdown("---")
    st.markdown("#### 📝 Anything Else We Should Know?")
    
    questionnaire_data['additional_notes'] = st.text_area(
        "Tell us more about your symptoms (optional)",
        placeholder="Example: 'The pain started after I was working on the computer for 8 hours' or 'My vision gets worse at night'",
        key="additional_notes",
        height=100,
        help="Any details that might help us understand your situation better"
    )
    
    return questionnaire_data


def display_questionnaire_summary(data):
    """
    Display a clean summary of questionnaire responses.
    
    Args:
        data: Dictionary with questionnaire responses
    """
    st.markdown("---")
    st.markdown("### 📊 Your Answers Summary")
    st.caption("Quick review of what you told us")
    
    # Main symptoms box
    st.markdown("#### 🔍 Main Symptoms")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        pain = data.get('eye_pain', 'Not answered')
        if 'No pain' in pain:
            st.success(f"👁️ **Pain:** None")
        elif 'Severe' in pain:
            st.error(f"👁️ **Pain:** {pain}")
        else:
            st.info(f"👁️ **Pain:** {pain}")
    
    with col2:
        redness = data.get('redness', 'Not answered')
        if 'Not red' in redness:
            st.success(f"🔴 **Redness:** None")
        elif 'Very red' in redness:
            st.error(f"🔴 **Redness:** {redness}")
        else:
            st.info(f"🔴 **Redness:** {redness}")
    
    with col3:
        blur = data.get('vision_blur', 'Not answered')
        if 'Clear' in blur:
            st.success(f"👓 **Vision:** Clear")
        elif 'Suddenly' in blur:
            st.error(f"👓 **Vision:** {blur}")
        else:
            st.info(f"👓 **Vision:** {blur}")
    
    # Timeline
    st.markdown("#### ⏱️ Timeline")
    col1, col2 = st.columns(2)
    
    with col1:
        duration = data.get('duration', 'Not specified')
        st.write(f"**Started:** {duration}")
    
    with col2:
        affected = data.get('affected_eye', 'Not specified')
        st.write(f"**Affected:** {affected}")
    
    # Health conditions
    health_issues = []
    if data.get('diabetes') == "Yes":
        health_issues.append("Diabetes")
    if data.get('hypertension') == "Yes":
        health_issues.append("High blood pressure")
    if data.get('contact_lenses') == "Yes":
        health_issues.append("Contact lens wearer")
    if 'Currently smoke' in data.get('smoking', ''):
        health_issues.append("Smoker")
    
    if health_issues:
        st.markdown("#### 🏥 Health Notes")
        st.write(", ".join(health_issues))
    
    # Critical warnings
    warnings = []
    if '⚠️' in data.get('floaters', ''):
        warnings.append("⚠️ **URGENT:** Sudden floaters - needs immediate attention!")
    if 'very painful' in data.get('eye_pain', '').lower():
        warnings.append("⚠️ **URGENT:** Severe pain - needs immediate attention!")
    if any('injury' in str(e).lower() for e in data.get('recent_events', [])):
        warnings.append("⚠️ **URGENT:** Recent injury - needs immediate attention!")
    
    if warnings:
        st.markdown("#### 🚨 Important Alerts")
        for warning in warnings:
            st.error(warning)
        st.error("**Please see an eye doctor as soon as possible!**")


def generate_clinical_correlation(questionnaire_data, comparison_result):
    """
    Generate clinical correlation between symptoms and iris findings.
    
    Args:
        questionnaire_data: Dictionary with questionnaire responses
        comparison_result: Dictionary with iris comparison results
    
    Returns:
        list: Clinical correlation statements
    """
    correlations = []
    
    # Light sensitivity correlation
    if 'Very bothered' in questionnaire_data.get('light_sensitivity', '') or 'Can\'t tolerate' in questionnaire_data.get('light_sensitivity', ''):
        if comparison_result.get('score', 0) > 40:
            correlations.append(
                "💡 Your light sensitivity matches the iris changes we found. "
                "This could mean inflammation or pupil issues."
            )
    
    # Vision blur correlation
    if 'Always blurry' in questionnaire_data.get('vision_blur', '') or 'Suddenly' in questionnaire_data.get('vision_blur', ''):
        correlations.append(
            "👓 Your blurry vision matches the iris patterns we detected. "
            "The iris structure might be affecting how light enters your eye."
        )
    
    # Diabetes correlation
    if questionnaire_data.get('diabetes') == "Yes":
        correlations.append(
            "🩸 Since you have diabetes, the iris changes we found could be related. "
            "We recommend a complete eye exam to check your retina too."
        )
    
    # Floaters correlation
    if '⚠️' in questionnaire_data.get('floaters', ''):
        correlations.append(
            "🚨 URGENT: Sudden floaters can mean retinal problems. "
            "Please see an eye doctor TODAY to check for retinal detachment."
        )
    
    # Hypertension correlation
    if questionnaire_data.get('hypertension') == "Yes":
        correlations.append(
            "💓 High blood pressure can affect eye blood vessels. "
            "Your doctor should check your retina for any changes."
        )
    
    # Contact lens correlation
    if questionnaire_data.get('contact_lenses') == "Yes" and 'red' in questionnaire_data.get('redness', '').lower():
        correlations.append(
            "👁️ Contact lenses + redness could mean an infection or irritation. "
            "Stop wearing contacts and see your eye doctor."
        )
    
    # Trauma correlation
    if any('injury' in str(e).lower() for e in questionnaire_data.get('recent_events', [])):
        correlations.append(
            "🤕 Eye injuries can cause iris damage. "
            "Your doctor should do a detailed exam to check for internal damage."
        )
    
    if not correlations:
        correlations.append(
            "✅ Your symptoms don't strongly match the iris findings. "
            "This is good news! Regular check-ups are still recommended."
        )
    
    return correlations
