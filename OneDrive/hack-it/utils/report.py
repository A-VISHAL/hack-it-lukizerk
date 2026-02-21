"""
PDF Report Generator Module
Generates comprehensive PDF reports using ReportLab.
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from pathlib import Path
import json
import numpy as np
from datetime import datetime


def generate_pdf_report(comparison_result, user_image_path, good_image_path, sector_map_path=None, output_path="report.pdf", patient_info=None):
    """
    Generate comprehensive PDF report with detailed iris comparison.
    
    Args:
        comparison_result: Dictionary with comparison results
        user_image_path: Path to user iris image
        good_image_path: Path to good iris image (optional)
        sector_map_path: Path to sector map image (optional)
        output_path: Output PDF path
        patient_info: Dictionary with patient information (optional)
    
    Returns:
        str: Path to generated PDF
    """
    # Create PDF document
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    normal_style = styles['Normal']
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.red,
        fontName='Helvetica-Oblique'
    )
    
    # Title
    story.append(Paragraph("INDIAN IRIS", title_style))
    story.append(Paragraph("Comprehensive Iris Health Analysis Report", styles['Heading2']))
    story.append(Spacer(1, 0.2*inch))
    
    # Patient Information (if provided)
    if patient_info:
        story.append(Paragraph("<b>Patient Information</b>", heading_style))
        patient_table_data = [
            ['Patient Name:', patient_info.get('name', 'N/A')],
            ['Age:', str(patient_info.get('age', 'N/A'))],
            ['Gender:', patient_info.get('gender', 'N/A')],
            ['Contact:', patient_info.get('contact', 'N/A')],
            ['Date of Examination:', patient_info.get('date', date_str)]
        ]
        patient_table = Table(patient_table_data, colWidths=[2*inch, 3.5*inch])
        patient_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        story.append(patient_table)
        story.append(Spacer(1, 0.3*inch))
    
    # Date
    story.append(Paragraph(f"<b>Report Generated:</b> {date_str}", normal_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Disclaimer
    story.append(Paragraph("<b>⚠️ IMPORTANT DISCLAIMER</b>", heading_style))
    story.append(Paragraph(
        "This is a NON-DIAGNOSTIC structural comparison tool. It measures pixel-level differences "
        "between iris images and does NOT diagnose diseases, predict health outcomes, or provide "
        "medical interpretations. Results are for informational purposes only. Always consult "
        "qualified healthcare professionals for medical evaluation.",
        disclaimer_style
    ))
    story.append(Spacer(1, 0.3*inch))
    
    # Images section
    story.append(Paragraph("<b>Iris Images</b>", heading_style))
    
    # Create image table for side-by-side comparison
    image_data = []
    image_row = []
    
    # User image
    if Path(user_image_path).exists():
        try:
            img = Image(user_image_path, width=2*inch, height=2*inch)
            image_row.append(img)
        except Exception as e:
            image_row.append(Paragraph(f"<i>Could not load user image</i>", normal_style))
    
    # Sector map
    if sector_map_path and Path(sector_map_path).exists():
        try:
            # Save sector map if it's a numpy array
            if isinstance(sector_map_path, np.ndarray):
                import cv2
                temp_path = "reports/temp_sector_map.png"
                cv2.imwrite(temp_path, sector_map_path)
                sector_map_path = temp_path
            
            img = Image(sector_map_path, width=2*inch, height=2*inch)
            image_row.append(img)
        except Exception:
            pass
    
    if len(image_row) > 0:
        image_data.append([Paragraph("<b>Original Image</b>", normal_style), 
                          Paragraph("<b>Processed Sector Map</b>", normal_style)])
        image_data.append(image_row)
        
        img_table = Table(image_data, colWidths=[2.5*inch, 2.5*inch])
        img_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        story.append(img_table)
        story.append(Spacer(1, 0.3*inch))
    
    # Comparison Score
    score = comparison_result.get('score', 0.0)
    interpretation = comparison_result.get('interpretation', {})
    category = interpretation.get('category', 'Unknown')
    
    story.append(Paragraph("<b>Overall Comparison Results</b>", heading_style))
    
    score_data = [
        ['Metric', 'Value', 'Interpretation'],
        ['Structural Difference Score', f"{score:.2f}/100", category],
    ]
    
    # Add ML/DL prediction if available
    if 'ml_prediction' in comparison_result and comparison_result['ml_prediction']:
        ml_pred = comparison_result['ml_prediction']
        score_data.append(['AI Health Score', f"{ml_pred['health_score']:.1f}/100", ml_pred['category']])
        score_data.append(['AI Prediction', ml_pred['prediction_class'], f"{ml_pred['confidence']*100:.1f}% confidence"])
    
    score_table = Table(score_data, colWidths=[2.2*inch, 1.8*inch, 2*inch])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))
    story.append(score_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Key Findings Summary
    story.append(Paragraph("<b>Key Findings Summary</b>", heading_style))
    
    findings = []
    
    # Structural differences
    if score <= 25:
        findings.append("• Minimal structural differences detected - within normal variation range")
    elif score <= 60:
        findings.append("• Moderate structural differences observed - further examination recommended")
    else:
        findings.append("• Significant structural differences detected - professional consultation advised")
    
    # ML prediction findings
    if 'ml_prediction' in comparison_result and comparison_result['ml_prediction']:
        ml_pred = comparison_result['ml_prediction']
        findings.append(f"• AI Analysis: {ml_pred['recommendation']}")
    
    # Sector analysis findings
    if 'sector_analysis' in comparison_result.get('differences', {}):
        features = comparison_result.get('features', {})
        sector_data = features.get('sector_analysis', {})
        high_variation_sectors = [name for name, data in sector_data.items() if data.get('variation', 0) > 15]
        if high_variation_sectors:
            findings.append(f"• High color variation detected in: {', '.join(high_variation_sectors)}")
    
    # Symptom correlation
    if 'symptom_correlation' in comparison_result:
        correlations = comparison_result.get('symptom_correlation', [])
        if correlations:
            findings.append(f"• Symptom correlation: {correlations[0]}")
    
    for finding in findings:
        story.append(Paragraph(finding, normal_style))
    
    story.append(Spacer(1, 0.3*inch))
    
    # Feature Differences Table
    story.append(Paragraph("<b>Detailed Feature Differences</b>", heading_style))
    
    differences = comparison_result.get('differences', {})
    
    if differences:
        # Prepare table data
        table_data = [['Feature Category', 'Feature Name', 'Difference Value']]
        
        # Group features by category
        color_features = []
        texture_features = []
        contour_features = []
        spot_features = []
        
        for key, value in differences.items():
            if 'mean' in key.lower() or 'h_' in key or 's_' in key or 'v_' in key:
                color_features.append([key, f"{value:.4f}"])
            elif 'lbp' in key.lower() or 'contrast' in key.lower() or 'entropy' in key.lower() or 'homogeneity' in key.lower():
                texture_features.append([key, f"{value:.4f}"])
            elif 'edge' in key.lower() or 'circular' in key.lower():
                contour_features.append([key, f"{value:.4f}"])
            elif 'spot' in key.lower():
                spot_features.append([key, f"{value:.4f}"])
        
        # Add rows
        for feat in color_features:
            table_data.append(['Color', feat[0], feat[1]])
        for feat in texture_features:
            table_data.append(['Texture', feat[0], feat[1]])
        for feat in contour_features:
            table_data.append(['Contour', feat[0], feat[1]])
        for feat in spot_features:
            table_data.append(['Spots', feat[0], feat[1]])
        
        # Create table
        diff_table = Table(table_data, colWidths=[1.5*inch, 2.5*inch, 1.5*inch])
        diff_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        story.append(diff_table)
        story.append(Spacer(1, 0.3*inch))
    
    # Sector Analysis (XAI Feature)
    if 'sector_analysis' in comparison_result.get('differences', {}):
        story.append(Paragraph("<b>Explainable AI: Sector Analysis</b>", heading_style))
        story.append(Paragraph(
            "The iris has been divided into 8 radial sectors for detailed analysis. "
            "Each sector is analyzed for color variation and anomalies.",
            normal_style
        ))
        story.append(Spacer(1, 0.1*inch))
        
        # Get sector analysis from features
        features = comparison_result.get('features', {})
        sector_data = features.get('sector_analysis', {})
        
        if sector_data:
            sector_table_data = [['Sector', 'Angle Range', 'Variation %', 'Status']]
            
            for sector_name, data in sector_data.items():
                variation = data.get('variation', 0)
                angle_range = data.get('angle_range', 'N/A')
                
                if variation > 15:
                    status = "⚠️ High Variation"
                elif variation > 10:
                    status = "⚡ Moderate"
                else:
                    status = "✓ Normal"
                
                sector_table_data.append([
                    sector_name,
                    angle_range,
                    f"{variation:.1f}%",
                    status
                ])
            
            sector_table = Table(sector_table_data, colWidths=[1.2*inch, 1.5*inch, 1.2*inch, 1.6*inch])
            sector_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]))
            story.append(sector_table)
            story.append(Spacer(1, 0.3*inch))
    
    # Symptom Correlation (XAI Feature)
    if 'symptom_correlation' in comparison_result:
        story.append(Paragraph("<b>Symptom Correlation Analysis</b>", heading_style))
        
        symptoms = comparison_result.get('symptoms', {})
        if symptoms:
            story.append(Paragraph("<b>Reported Symptoms:</b>", normal_style))
            symptom_list = [
                f"• Pain Level: {symptoms.get('pain', 'N/A')}",
                f"• Redness: {symptoms.get('redness', 'N/A')}",
                f"• Vision Blur: {symptoms.get('vision_blur', 'N/A')}",
                f"• Light Sensitivity: {symptoms.get('light_sensitivity', 'N/A')}",
                f"• Duration: {symptoms.get('duration', 'N/A')}"
            ]
            for symptom in symptom_list:
                story.append(Paragraph(symptom, normal_style))
            
            story.append(Spacer(1, 0.2*inch))
        
        correlations = comparison_result.get('symptom_correlation', [])
        if correlations:
            story.append(Paragraph("<b>Correlation Findings:</b>", normal_style))
            for correlation in correlations:
                story.append(Paragraph(f"• {correlation}", normal_style))
            
            story.append(Spacer(1, 0.3*inch))
    
    # Summary
    story.append(Paragraph("<b>Summary</b>", heading_style))
    story.append(Paragraph(
        f"The comparison analysis shows a difference score of {score:.2f}/100, "
        f"categorized as '{category}'. This score represents pixel-level structural "
        "differences between the user iris and the reference good iris baseline. "
        "The sector analysis provides detailed regional information, and symptom correlation "
        "helps contextualize findings. No medical diagnosis or health prediction is made.",
        normal_style
    ))
    story.append(Spacer(1, 0.3*inch))
    
    # XAI Disclaimer
    story.append(Paragraph("<b>Explainable AI (XAI) Approach</b>", heading_style))
    story.append(Paragraph(
        "This report uses Explainable AI techniques to provide transparency: "
        "(1) Original vs. Processed images show the analysis pipeline, "
        "(2) Sector maps visualize regional variations, "
        "(3) Anomaly detection identifies specific areas of interest, "
        "(4) Symptom correlation contextualizes findings. "
        "All measurements are based on real pixel-level data, not AI predictions.",
        normal_style
    ))
    story.append(Spacer(1, 0.3*inch))
    
    # Doctor Submission Section
    story.append(Paragraph("<b>For Healthcare Professional Review</b>", heading_style))
    story.append(Paragraph(
        "This report can be shared with qualified healthcare professionals for further evaluation. "
        "Please note that this tool provides structural comparison data only and should not be "
        "used as a substitute for professional medical examination.",
        normal_style
    ))
    story.append(Spacer(1, 0.2*inch))
    
    # Doctor notes section (blank)
    doctor_table = Table([
        ['Healthcare Professional Notes:'],
        [''],
        [''],
        [''],
        ['Signature: ___________________  Date: ___________']
    ], colWidths=[6*inch])
    doctor_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (0, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))
    story.append(doctor_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Final disclaimer
    story.append(Paragraph(
        "<b>⚠️ CRITICAL DISCLAIMER:</b> This is a screening tool, not a final diagnosis. "
        "This tool provides structural comparison data only and should NOT be used as a substitute "
        "for professional medical examination. Please consult an Ophthalmologist for proper diagnosis "
        "and treatment. All findings are for informational purposes only.",
        disclaimer_style
    ))
    
    # Build PDF
    doc.build(story)
    
    return output_path
