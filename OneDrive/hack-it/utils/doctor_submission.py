"""
Doctor Submission Module
Handles report submission to doctors via email
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
import json


def send_report_to_doctor(report_path, doctor_email, patient_info, smtp_config=None):
    """
    Send iris analysis report to doctor via email.
    
    Args:
        report_path: Path to the PDF report
        doctor_email: Doctor's email address
        patient_info: Dictionary with patient information
        smtp_config: SMTP configuration (optional)
    
    Returns:
        dict: Status of email sending
    """
    
    if smtp_config is None:
        # Default SMTP configuration (can be customized)
        smtp_config = {
            'server': 'smtp.gmail.com',
            'port': 587,
            'username': '',  # To be configured by user
            'password': ''   # To be configured by user
        }
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = smtp_config.get('username', 'noreply@indianiris.com')
        msg['To'] = doctor_email
        msg['Subject'] = f"Iris Analysis Report - {patient_info.get('name', 'Patient')}"
        
        # Email body
        body = f"""
Dear Doctor,

Please find attached the comprehensive iris analysis report for the following patient:

Patient Name: {patient_info.get('name', 'N/A')}
Age: {patient_info.get('age', 'N/A')}
Gender: {patient_info.get('gender', 'N/A')}
Contact: {patient_info.get('contact', 'N/A')}
Date of Examination: {patient_info.get('date', 'N/A')}

Report Summary:
- Structural Difference Score: {patient_info.get('score', 'N/A')}/100
- Category: {patient_info.get('category', 'N/A')}
- AI Health Score: {patient_info.get('ai_score', 'N/A')}/100

The attached PDF report contains:
1. Detailed iris comparison (Patient vs. Reference Healthy Iris)
2. AI-powered health analysis
3. Sector-wise analysis with anomaly detection
4. Symptom correlation findings
5. High-resolution iris images

IMPORTANT DISCLAIMER:
This is a NON-DIAGNOSTIC screening tool. The report provides structural comparison data only 
and should not be used as a substitute for professional medical examination. Please conduct 
a thorough clinical evaluation before making any diagnostic or treatment decisions.

For any questions regarding this report, please contact the patient directly.

Best regards,
INDIAN IRIS - Iris Analysis System
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach PDF report
        if Path(report_path).exists():
            with open(report_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {Path(report_path).name}'
                )
                msg.attach(part)
        else:
            return {
                'success': False,
                'message': 'Report file not found'
            }
        
        # Send email
        if smtp_config.get('username') and smtp_config.get('password'):
            server = smtplib.SMTP(smtp_config['server'], smtp_config['port'])
            server.starttls()
            server.login(smtp_config['username'], smtp_config['password'])
            text = msg.as_string()
            server.sendmail(smtp_config['username'], doctor_email, text)
            server.quit()
            
            return {
                'success': True,
                'message': f'Report successfully sent to {doctor_email}'
            }
        else:
            return {
                'success': False,
                'message': 'SMTP configuration not set. Please configure email settings.'
            }
    
    except Exception as e:
        return {
            'success': False,
            'message': f'Error sending email: {str(e)}'
        }


def save_doctor_submission_record(report_path, doctor_email, patient_info, submission_log='reports/submissions.json'):
    """
    Save record of report submission to doctor.
    
    Args:
        report_path: Path to the PDF report
        doctor_email: Doctor's email address
        patient_info: Dictionary with patient information
        submission_log: Path to submission log file
    """
    from datetime import datetime
    
    # Load existing submissions
    submissions = []
    if Path(submission_log).exists():
        try:
            with open(submission_log, 'r') as f:
                submissions = json.load(f)
        except:
            submissions = []
    
    # Add new submission
    submission_record = {
        'timestamp': datetime.now().isoformat(),
        'patient_name': patient_info.get('name', 'N/A'),
        'patient_contact': patient_info.get('contact', 'N/A'),
        'doctor_email': doctor_email,
        'report_path': str(report_path),
        'score': patient_info.get('score', 'N/A'),
        'category': patient_info.get('category', 'N/A')
    }
    
    submissions.append(submission_record)
    
    # Save updated submissions
    with open(submission_log, 'w') as f:
        json.dump(submissions, f, indent=2)


def generate_doctor_submission_form():
    """
    Generate HTML form for doctor submission (for web interface).
    
    Returns:
        str: HTML form code
    """
    html_form = """
    <div class="doctor-submission-form">
        <h3>Submit Report to Doctor</h3>
        <form>
            <label for="doctor_name">Doctor's Name:</label>
            <input type="text" id="doctor_name" name="doctor_name" required>
            
            <label for="doctor_email">Doctor's Email:</label>
            <input type="email" id="doctor_email" name="doctor_email" required>
            
            <label for="doctor_specialty">Specialty:</label>
            <select id="doctor_specialty" name="doctor_specialty">
                <option value="ophthalmologist">Ophthalmologist</option>
                <option value="optometrist">Optometrist</option>
                <option value="general">General Practitioner</option>
                <option value="other">Other</option>
            </select>
            
            <label for="additional_notes">Additional Notes (Optional):</label>
            <textarea id="additional_notes" name="additional_notes" rows="4"></textarea>
            
            <button type="submit">Send Report to Doctor</button>
        </form>
    </div>
    """
    return html_form
