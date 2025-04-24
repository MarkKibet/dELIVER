from flask import current_app, render_template_string, request
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os

def send_email(to_email, subject, html_content):
    """Send email using SendGrid"""
    sg_api_key = current_app.config.get('SENDGRID_API_KEY')
    from_email = current_app.config.get('EMAIL_SENDER')
    
    if not sg_api_key:
        current_app.logger.warning("SendGrid API key not configured. Email not sent.")
        return False
    
    message = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject=subject,
        html_content=html_content
    )
    
    try:
        sg = SendGridAPIClient(sg_api_key)
        response = sg.send(message)
        current_app.logger.info(f"Email sent to {to_email}, status code: {response.status_code}")
        return True
    except Exception as e:
        current_app.logger.error(f"Error sending email: {str(e)}")
        return False

def send_verification_email(to_email, token):
    """Send email verification link"""
    subject = "Verify Your Deliveroo Account"
    verification_url = f"{request.host_url.rstrip('/')}/verify-email?token={token}"
    
    html_content = render_template_string("""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #333;">Welcome to Deliveroo!</h2>
        <p>Thank you for signing up. Please verify your email address by clicking the link below:</p>
        <p><a href="{{ verification_url }}" style="display: inline-block; padding: 10px 20px; background-color: #00CCBC; color: white; text-decoration: none; border-radius: 5px;">Verify Email Address</a></p>
        <p>If the button doesn't work, copy and paste this URL into your browser:</p>
        <p>{{ verification_url }}</p>
        <p>This link will expire in 24 hours.</p>
        <p>Best regards,<br>The Deliveroo Team</p>
    </div>
    """, verification_url=verification_url)
    
    return send_email(to_email, subject, html_content)

def send_password_reset_email(to_email, token):
    """Send password reset link"""
    subject = "Reset Your Deliveroo Password"
    reset_url = f"{request.host_url.rstrip('/')}/reset-password?token={token}"
    
    html_content = render_template_string("""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #333;">Password Reset Request</h2>
        <p>We received a request to reset your password. Click the link below to set a new password:</p>
        <p><a href="{{ reset_url }}" style="display: inline-block; padding: 10px 20px; background-color: #00CCBC; color: white; text-decoration: none; border-radius: 5px;">Reset Password</a></p>
        <p>If the button doesn't work, copy and paste this URL into your browser:</p>
        <p>{{ reset_url }}</p>
        <p>This link will expire in 1 hour.</p>
        <p>If you didn't request a password reset, you can ignore this email.</p>
        <p>Best regards,<br>The Deliveroo Team</p>
    </div>
    """, reset_url=reset_url)
    
    return send_email(to_email, subject, html_content)