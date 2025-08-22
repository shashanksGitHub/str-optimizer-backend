import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import socket
import requests
import json

def send_email_via_sendgrid(to_email, subject, body, pdf_path=None):
    """Send email via SendGrid API (HTTP-based, bypasses SMTP blocks)"""
    sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
    if not sendgrid_api_key:
        print("❌ SendGrid API key not configured")
        return False
    
    try:
        # Use a different sender to avoid spam reputation
        from_email = "yashkpa@gmail.com"  # Verified sender for SendGrid
        
        # SendGrid API endpoint
        url = "https://api.sendgrid.com/v3/mail/send"
        
        # Convert plain text to HTML with better formatting
        html_body = body.replace('\n', '<br>').replace('  ', '&nbsp;&nbsp;')
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{subject}</title>
        </head>
        <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; background-color: #f9f9f9; margin: 0; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #2c3e50; margin: 0;">STR Optimizer</h1>
                    <p style="color: #7f8c8d; margin: 5px 0 0 0;">Property Optimization Report</p>
                </div>
                <div style="line-height: 1.8;">
                    {html_body}
                </div>
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #7f8c8d; font-size: 12px;">
                    <p>STR Optimizer - Maximize Your Property's Potential</p>
                    <p>Visit us at <a href="https://str-optimizer.web.app" style="color: #3498db;">str-optimizer.web.app</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Email data with enhanced headers for deliverability
        data = {
            "personalizations": [{
                "to": [{"email": to_email}],
                "subject": subject
            }],
            "from": {"email": from_email, "name": "STR Optimizer"},
            "reply_to": {"email": from_email, "name": "STR Optimizer Support"},
            "content": [
                {"type": "text/plain", "value": body},
                {"type": "text/html", "value": html_body}
            ],
            "categories": ["property_optimization", "business_report"],
            "custom_args": {
                "service": "str_optimizer",
                "report_type": "property_analysis",
                "version": "2.0"
            },
            "headers": {
                "X-Priority": "3",
                "X-MSMail-Priority": "Normal",
                "Importance": "Normal"
            }
        }
        
        # Add PDF attachment with size check
        if pdf_path and os.path.exists(pdf_path):
            try:
                import base64
                file_size = os.path.getsize(pdf_path)
                print(f"📎 PDF file size: {file_size} bytes")
                
                # Limit attachment size to 10MB for better deliverability
                if file_size > 10 * 1024 * 1024:  # 10MB
                    print("⚠️ PDF too large for email attachment, skipping")
                else:
                    with open(pdf_path, "rb") as f:
                        pdf_data = base64.b64encode(f.read()).decode()
                    
                    data["attachments"] = [{
                        "content": pdf_data,
                        "filename": "Property_Optimization_Report.pdf",
                        "type": "application/pdf",
                        "disposition": "attachment",
                        "content_id": "property_report"
                    }]
                    print("✅ PDF attached to SendGrid email")
            except Exception as e:
                print(f"⚠️ Failed to attach PDF to SendGrid: {e}")
        
        headers = {
            "Authorization": f"Bearer {sendgrid_api_key}",
            "Content-Type": "application/json",
            "User-Agent": "STR-Optimizer/1.0"
        }
        
        print("📤 Sending email via SendGrid API...")
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 202:
            print(f"✅ Email sent successfully via SendGrid to {to_email}")
            return True
        else:
            print(f"❌ SendGrid API error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ SendGrid error: {e}")
        return False

def send_email(to_email, desc, amenities, reviews, pdf_path):
    """Send email with optimization report"""
    from_email = os.getenv("EMAIL_USERNAME")
    password = os.getenv("EMAIL_PASSWORD")

    # Check if email credentials are configured
    if not from_email and not os.getenv("SENDGRID_API_KEY"):
        print("❌ No email service configured (Gmail or SendGrid). Skipping email send.")
        return False

    try:
        print(f"📧 Preparing email to {to_email}")
        
        subject = "Your Property Optimization Report is Ready"
        body = f"""Dear Property Owner,

Thank you for using STR Optimizer. Your property analysis has been completed and your optimization report is ready.

OPTIMIZED DESCRIPTION:
{desc[:500]}{"..." if len(desc) > 500 else ""}

RECOMMENDED AMENITIES:
{amenities[:300]}{"..." if len(amenities) > 300 else ""}

REVIEW INSIGHTS:
{reviews[:300] if reviews else "Review analysis not available for this property"}{"..." if reviews and len(reviews) > 300 else ""}

{('Your detailed PDF report is attached to this email.' if pdf_path else 'You can access your full report in your account dashboard.')}

We hope these recommendations help improve your property's performance and booking rates.

Best regards,
STR Optimizer Team

Support: support@stroptimizer.com
Website: https://str-optimizer.web.app

This is an automated message from STR Optimizer. Please do not reply to this email.
        """
        
        print("✅ Email body prepared")

        # Try SendGrid first (HTTP API - bypasses SMTP blocks)
        if os.getenv("SENDGRID_API_KEY"):
            print("🔄 Trying SendGrid API (bypasses SMTP blocks)...")
            if send_email_via_sendgrid(to_email, subject, body, pdf_path):
                return True
            else:
                print("⚠️ SendGrid failed, falling back to Gmail SMTP...")

        # Fall back to Gmail SMTP if SendGrid unavailable
        if not from_email or not password:
            print("❌ Gmail credentials not configured and SendGrid failed.")
            return False

        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Attach PDF if available - with size limit
        if pdf_path and os.path.exists(pdf_path):
            try:
                file_size = os.path.getsize(pdf_path)
                print(f"📎 PDF file size: {file_size} bytes")
                
                # Limit PDF attachment to 5MB to prevent memory issues
                if file_size > 5 * 1024 * 1024:  # 5MB
                    print("⚠️ PDF too large, skipping attachment")
                else:
                    with open(pdf_path, "rb") as f:
                        part = MIMEApplication(f.read(), Name=os.path.basename(pdf_path))
                        part['Content-Disposition'] = f'attachment; filename="str_optimization_report.pdf"'
                        msg.attach(part)
                        print("✅ PDF attached successfully")
            except Exception as attachment_error:
                print(f"⚠️ Failed to attach PDF: {attachment_error}")

        # Try multiple SMTP configurations for better compatibility
        smtp_configs = [
            # Gmail SSL
            {'server': 'smtp.gmail.com', 'port': 465, 'ssl': True, 'name': 'Gmail SSL'},
            # Gmail TLS (alternative port)
            {'server': 'smtp.gmail.com', 'port': 587, 'ssl': False, 'name': 'Gmail TLS'},
            # Gmail on port 25 (basic)
            {'server': 'smtp.gmail.com', 'port': 25, 'ssl': False, 'name': 'Gmail Port 25'},
        ]

        for config in smtp_configs:
            try:
                print(f"📤 Trying {config['name']} ({config['server']}:{config['port']})...")
                
                # Set socket timeout to prevent hanging
                socket.setdefaulttimeout(10)
                
                if config['ssl']:
                    # SSL connection
                    server = smtplib.SMTP_SSL(config['server'], config['port'], timeout=10)
                else:
                    # TLS connection
                    server = smtplib.SMTP(config['server'], config['port'], timeout=10)
                    if config['port'] == 587:
                        server.starttls()
                
                print("🔐 Logging into Gmail...")
                server.login(from_email, password)
                print("📨 Sending email...")
                server.send_message(msg)
                server.quit()
                print(f"✅ Email sent successfully via {config['name']} to {to_email}")
                return True
                
            except (socket.gaierror, socket.timeout, OSError) as network_error:
                print(f"❌ {config['name']} network error: {network_error}")
                continue
            except smtplib.SMTPAuthenticationError as auth_error:
                print(f"❌ {config['name']} authentication failed: {auth_error}")
                continue
            except smtplib.SMTPException as smtp_error:
                print(f"❌ {config['name']} SMTP error: {smtp_error}")
                continue
            except Exception as config_error:
                print(f"❌ {config['name']} unexpected error: {config_error}")
                continue

        # If all attempts failed
        print("❌ All email services failed.")
        print("💡 SMTP ports are blocked by your hosting provider (DigitalOcean).")
        print("💡 Solutions:")
        print("   1. Contact DigitalOcean support to unblock SMTP ports")
        print("   2. Add SENDGRID_API_KEY environment variable for HTTP-based email")
        print("   3. Use a different email service provider")
        return False
        
    except Exception as e:
        print(f"❌ Email preparation error: {e}")
        return False 