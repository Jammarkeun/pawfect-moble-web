"""
Email Service for Pawfect Finds
Uses Gmail SMTP for sending emails
"""
import smtplib
import logging
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app

logger = logging.getLogger(__name__)

class EmailService:
    """Email service using Gmail SMTP"""

    @staticmethod
    def send_application_status_email(recipient_email: str, account_type: str, status: str, admin_notes: str = None) -> bool:
        """Send approval/rejection status email for account applications."""
        try:
            if not recipient_email:
                logger.error("Missing recipient email for application status email")
                return False

            sender_email = current_app.config.get('MAIL_DEFAULT_SENDER') or current_app.config.get('MAIL_USERNAME')
            sender_password = current_app.config.get('MAIL_PASSWORD')
            mail_server = current_app.config.get('MAIL_SERVER', 'smtp.gmail.com')
            mail_port = int(current_app.config.get('MAIL_PORT', 587))
            mail_use_tls = bool(current_app.config.get('MAIL_USE_TLS', True))

            if not sender_email or not sender_password:
                logger.error("Email configuration missing for application status email")
                return False

            if isinstance(sender_email, tuple):
                sender_email = sender_email[1]

            account_label = (account_type or 'account').strip().title()
            is_approved = (status or '').strip().lower() == 'approved'
            is_buyer = (account_type or '').strip().lower() == 'user'
            base_url = (current_app.config.get('BASE_URL') or 'http://localhost:5000').rstrip('/')
            login_url = f"{base_url}/login"

            if is_approved and is_buyer:
                subject = 'Congratulations! Your Pawfect Finds account is approved'
            else:
                subject = f"{account_label} Application {'Approved' if is_approved else 'Update'} - Pawfect Finds"
            status_color = '#2E7D32' if is_approved else '#C62828'
            status_title = 'Approved' if is_approved else 'Rejected'

            note_html = ''
            if admin_notes:
                note_html = f"""
                <div style=\"background: #f5f5f5; border-left: 4px solid #6D4C41; padding: 12px; margin: 16px 0;\">
                    <strong>Admin Note:</strong><br>{admin_notes}
                </div>
                """

            if is_approved and is_buyer:
                body_intro = "Congratulations! Your account has been approved by the admin."
                body_details = "You can now log in to Pawfect Finds and start shopping."
                cta_html = f"""
                <p style=\"margin-top: 24px;\">
                    <a href=\"{login_url}\" style=\"background: #6D4C41; color: #ffffff; padding: 12px 20px; text-decoration: none; border-radius: 6px; display: inline-block;\">Log In Now</a>
                </p>
                """
            else:
                body_intro = f"Your {account_label.lower()} application has been <strong>{status_title.lower()}</strong>."
                body_details = ""
                cta_html = ""

            html = f"""
            <html>
                <body style=\"font-family: Arial, sans-serif; line-height: 1.6; color: #333;\">
                    <div style=\"max-width: 600px; margin: 0 auto; padding: 20px;\">
                        <h2 style=\"color: {status_color};\">{account_label} Application {status_title}</h2>
                        <p>Hello,</p>
                        <p>{body_intro}</p>
                        {f'<p>{body_details}</p>' if body_details else ''}
                        {note_html}
                        {cta_html}
                        <p style=\"margin-top: 20px;\">Thank you for using Pawfect Finds.</p>
                        <p style=\"color: #666; font-size: 12px; margin-top: 30px;\">- Pawfect Finds</p>
                    </div>
                </body>
            </html>
            """

            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = f'"Pawfect Finds" <{sender_email}>'
            message['To'] = recipient_email
            message.attach(MIMEText(html, 'html'))

            smtp_hosts = [mail_server]
            if mail_server == 'smtp.gmail.com':
                smtp_hosts.append('smtp.googlemail.com')

            last_error = None
            for smtp_host in smtp_hosts:
                try:
                    socket.getaddrinfo(smtp_host, mail_port)
                    with smtplib.SMTP(smtp_host, mail_port, timeout=20) as server:
                        if mail_use_tls:
                            server.starttls()
                        server.login(sender_email, sender_password)
                        server.send_message(message)

                    logger.info(
                        "Application status email sent to %s (%s/%s) via %s",
                        recipient_email, account_type, status, smtp_host
                    )
                    return True
                except socket.gaierror as dns_error:
                    last_error = dns_error
                    logger.error("DNS resolution failed for SMTP host %s: %s", smtp_host, dns_error)
                except Exception as smtp_error:
                    last_error = smtp_error
                    logger.error("SMTP send failed via %s: %s", smtp_host, smtp_error)

            logger.error(
                "Failed to send application status email after trying hosts %s. Last error: %s",
                smtp_hosts, last_error
            )
            return False
        except Exception as e:
            logger.error(f"Failed to send application status email: {e}")
            return False
    
    @staticmethod
    def send_otp_email(recipient_email: str, otp_code: str) -> bool:
        """
        Send OTP email using Gmail SMTP.
        Returns True if successful, False otherwise.
        """
        try:
            # Get email configuration
            sender_email = current_app.config.get('MAIL_DEFAULT_SENDER') or current_app.config.get('MAIL_USERNAME')
            sender_password = current_app.config.get('MAIL_PASSWORD')
            mail_server = current_app.config.get('MAIL_SERVER', 'smtp.gmail.com')
            mail_port = int(current_app.config.get('MAIL_PORT', 587))
            mail_use_tls = bool(current_app.config.get('MAIL_USE_TLS', True))
            
            # Debug logging
            logger.info(f"Attempting to send email to {recipient_email}")
            logger.info(f"Using sender email: {sender_email}")
            logger.info("SMTP target: %s:%s (TLS=%s)", mail_server, mail_port, mail_use_tls)
            
            if not sender_email or not sender_password:
                logger.error("=== Email Configuration Error ===")
                logger.error(f"MAIL_DEFAULT_SENDER: {current_app.config.get('MAIL_DEFAULT_SENDER')}")
                logger.error(f"MAIL_USERNAME: {current_app.config.get('MAIL_USERNAME')}")
                logger.error(f"MAIL_PASSWORD: {'[SET]' if current_app.config.get('MAIL_PASSWORD') else '[NOT SET]'}")
                logger.error("==============================")
                return False
                
            # Ensure email is in the correct format
            if isinstance(sender_email, tuple):
                sender_email = sender_email[1]  # Get email from (name, email) tuple
            
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = 'Your Pawfect Finds Verification Code'
            
            # Format the sender to show 'Pawfect Finds' in Gmail
            sender_name = 'Pawfect Finds'
            message['From'] = f'"{sender_name}" <{sender_email}>'
            message['To'] = recipient_email
            
            # Create HTML content
            html = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #6D4C41;">Verification Code</h2>
                        <p>Hello,</p>
                        <p>Your verification code is:</p>
                        <div style="background: #f5f5f5; padding: 20px; text-align: center; margin: 20px 0;">
                            <h1 style="color: #6D4C41; font-size: 32px; margin: 0; letter-spacing: 5px;">{otp_code}</h1>
                        </div>
                        <p>Enter this code in the app to complete your signup.</p>
                        <p>This code will expire in 10 minutes.</p>
                        <p style="color: #666; font-size: 12px; margin-top: 30px;">
                            If you didn't request this, you can safely ignore this email.<br>
                            — Pawfect Finds
                        </p>
                    </div>
                </body>
            </html>
            """
            
            # Attach HTML content
            message.attach(MIMEText(html, 'html'))
            
            # Try configured SMTP host first, then Gmail alias for DNS fallback.
            smtp_hosts = [mail_server]
            if mail_server == 'smtp.gmail.com':
                smtp_hosts.append('smtp.googlemail.com')

            last_error = None
            for smtp_host in smtp_hosts:
                try:
                    # Explicit DNS check gives clearer diagnostics than a generic SMTP error.
                    socket.getaddrinfo(smtp_host, mail_port)
                    with smtplib.SMTP(smtp_host, mail_port, timeout=20) as server:
                        if mail_use_tls:
                            server.starttls()
                        server.login(sender_email, sender_password)
                        server.send_message(message)

                    logger.info("OTP email sent to %s via %s", recipient_email, smtp_host)
                    return True
                except socket.gaierror as dns_error:
                    last_error = dns_error
                    logger.error("DNS resolution failed for SMTP host %s: %s", smtp_host, dns_error)
                except Exception as smtp_error:
                    last_error = smtp_error
                    logger.error("SMTP send failed via %s: %s", smtp_host, smtp_error)
                
            logger.error("Failed to send OTP email after trying hosts %s. Last error: %s", smtp_hosts, last_error)
            return False
            
        except Exception as e:
            logger.error(f"Failed to send OTP email: {e}")
            return False
    
    @staticmethod
    def send_low_stock_alert(recipient_email: str, product_name: str, current_stock: int, threshold: int, product_id: int) -> bool:
        """
        Send low stock alert email to seller.
        Returns True if successful, False otherwise.
        """
        try:
            sender_email = current_app.config.get('MAIL_DEFAULT_SENDER') or current_app.config.get('MAIL_USERNAME')
            sender_password = current_app.config.get('MAIL_PASSWORD')
            
            if not sender_email or not sender_password:
                logger.error("Email configuration missing for low stock alert")
                return False
            
            if isinstance(sender_email, tuple):
                sender_email = sender_email[1]
            
            message = MIMEMultipart('alternative')
            message['Subject'] = f'⚠️ Low Stock Alert: {product_name}'
            message['From'] = f'"Pawfect Finds" <{sender_email}>'
            message['To'] = recipient_email
            
            html = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #FF9800;">⚠️ Low Stock Alert</h2>
                        <p>Hello,</p>
                        <p>Your product <strong>{product_name}</strong> is running low on stock.</p>
                        <div style="background: #fff3e0; border-left: 4px solid #FF9800; padding: 15px; margin: 20px 0;">
                            <p style="margin: 5px 0;"><strong>Current Stock:</strong> {current_stock} units</p>
                            <p style="margin: 5px 0;"><strong>Alert Threshold:</strong> {threshold} units</p>
                        </div>
                        <p>Please consider restocking to avoid running out of inventory.</p>
                        <p><a href="{current_app.config.get('BASE_URL', 'http://localhost:5000')}/seller/inventory" 
                              style="background: #6D4C41; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 10px;">
                           Manage Inventory
                        </a></p>
                        <p style="color: #666; font-size: 12px; margin-top: 30px;">
                            — Pawfect Finds Inventory System
                        </p>
                    </div>
                </body>
            </html>
            """
            
            message.attach(MIMEText(html, 'html'))
            
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(message)
            
            logger.info(f"Low stock alert sent to {recipient_email} for product {product_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send low stock alert: {e}")
            return False
    
    @staticmethod
    def send_out_of_stock_alert(recipient_email: str, product_name: str, product_id: int) -> bool:
        """
        Send out of stock alert email to seller.
        Returns True if successful, False otherwise.
        """
        try:
            sender_email = current_app.config.get('MAIL_DEFAULT_SENDER') or current_app.config.get('MAIL_USERNAME')
            sender_password = current_app.config.get('MAIL_PASSWORD')
            
            if not sender_email or not sender_password:
                logger.error("Email configuration missing for out of stock alert")
                return False
            
            if isinstance(sender_email, tuple):
                sender_email = sender_email[1]
            
            message = MIMEMultipart('alternative')
            message['Subject'] = f'🚨 Out of Stock: {product_name}'
            message['From'] = f'"Pawfect Finds" <{sender_email}>'
            message['To'] = recipient_email
            
            html = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #f44336;">🚨 Out of Stock Alert</h2>
                        <p>Hello,</p>
                        <p>Your product <strong>{product_name}</strong> is now <strong style="color: #f44336;">OUT OF STOCK</strong>.</p>
                        <div style="background: #ffebee; border-left: 4px solid #f44336; padding: 15px; margin: 20px 0;">
                            <p style="margin: 5px 0;"><strong>Current Stock:</strong> 0 units</p>
                            <p style="margin: 5px 0;"><strong>Status:</strong> Product unavailable for purchase</p>
                        </div>
                        <p>Please restock immediately to resume sales and prevent lost revenue.</p>
                        <p><a href="{current_app.config.get('BASE_URL', 'http://localhost:5000')}/seller/inventory" 
                              style="background: #f44336; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 10px;">
                           Restock Now
                        </a></p>
                        <p style="color: #666; font-size: 12px; margin-top: 30px;">
                            — Pawfect Finds Inventory System
                        </p>
                    </div>
                </body>
            </html>
            """
            
            message.attach(MIMEText(html, 'html'))
            
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(message)
            
            logger.info(f"Out of stock alert sent to {recipient_email} for product {product_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send out of stock alert: {e}")
            return False
    
    @staticmethod
    def send_seller_approval_email(email: str, first_name: str, business_name: str) -> bool:
        """Send approval email to seller"""
        try:
            sender_email = current_app.config.get('MAIL_DEFAULT_SENDER') or current_app.config.get('MAIL_USERNAME')
            sender_password = current_app.config.get('MAIL_PASSWORD')
            
            if not sender_email or not sender_password:
                logger.error("Email configuration missing for seller approval")
                return False
            
            if isinstance(sender_email, tuple):
                sender_email = sender_email[1]
            
            base_url = (current_app.config.get('BASE_URL') or 'http://localhost:5000').rstrip('/')
            login_url = f"{base_url}/auth/login"
            
            message = MIMEMultipart('alternative')
            message['Subject'] = '🎉 Your Seller Application is Approved!'
            message['From'] = f'"Pawfect Finds" <{sender_email}>'
            message['To'] = email
            
            html = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #2E7D32;">🎉 Congratulations!</h2>
                        <p>Hello {first_name},</p>
                        <p>We're excited to inform you that your seller application for <strong>{business_name}</strong> has been <strong style="color: #2E7D32;">APPROVED</strong>!</p>
                        
                        <div style="background: #e8f5e9; border-left: 4px solid #2E7D32; padding: 15px; margin: 20px 0;">
                            <h4 style="margin-top: 0; color: #1b5e20;">What's Next?</h4>
                            <ul style="margin: 10px 0; padding-left: 20px;">
                                <li>Log in to your seller account</li>
                                <li>Complete your business profile</li>
                                <li>Start adding your pet products</li>
                                <li>Begin accepting orders from customers</li>
                            </ul>
                        </div>
                        
                        <p style="margin-top: 24px;">
                            <a href="{login_url}" style="background: #2E7D32; color: #ffffff; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold;">Log In Now</a>
                        </p>
                        
                        <p style="margin-top: 20px; color: #666;">If you have any questions, please contact our support team.</p>
                        <p style="color: #666; font-size: 12px; margin-top: 30px;">
                            — Pawfect Finds<br>
                            <em>Connecting Pet Lovers with Quality Products</em>
                        </p>
                    </div>
                </body>
            </html>
            """
            
            message.attach(MIMEText(html, 'html'))
            
            mail_server = current_app.config.get('MAIL_SERVER', 'smtp.gmail.com')
            mail_port = int(current_app.config.get('MAIL_PORT', 587))
            mail_use_tls = bool(current_app.config.get('MAIL_USE_TLS', True))
            
            with smtplib.SMTP(mail_server, mail_port) as server:
                if mail_use_tls:
                    server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(message)
            
            logger.info(f"Seller approval email sent to {email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send seller approval email: {e}")
            return False
    
    @staticmethod
    def send_seller_rejection_email(email: str, first_name: str, reason: str) -> bool:
        """Send rejection email to seller"""
        try:
            sender_email = current_app.config.get('MAIL_DEFAULT_SENDER') or current_app.config.get('MAIL_USERNAME')
            sender_password = current_app.config.get('MAIL_PASSWORD')
            
            if not sender_email or not sender_password:
                logger.error("Email configuration missing for seller rejection")
                return False
            
            if isinstance(sender_email, tuple):
                sender_email = sender_email[1]
            
            message = MIMEMultipart('alternative')
            message['Subject'] = 'Seller Application Status Update'
            message['From'] = f'"Pawfect Finds" <{sender_email}>'
            message['To'] = email
            
            html = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #d32f2f;">Seller Application Status</h2>
                        <p>Hello {first_name},</p>
                        <p>Thank you for your interest in becoming a seller on Pawfect Finds. After careful review of your application, we've decided to not approve it at this time.</p>
                        
                        <div style="background: #ffebee; border-left: 4px solid #d32f2f; padding: 15px; margin: 20px 0;">
                            <h4 style="margin-top: 0; color: #b71c1c;">Reason:</h4>
                            <p style="margin: 10px 0;">{reason}</p>
                        </div>
                        
                        <p>You may reapply in the future if you address the concerns noted above. We encourage you to review our seller guidelines and try again.</p>
                        
                        <p style="margin-top: 20px; color: #666;">If you have questions about this decision, please contact our support team.</p>
                        <p style="color: #666; font-size: 12px; margin-top: 30px;">
                            — Pawfect Finds Support Team<br>
                            <em>Connecting Pet Lovers with Quality Products</em>
                        </p>
                    </div>
                </body>
            </html>
            """
            
            message.attach(MIMEText(html, 'html'))
            
            mail_server = current_app.config.get('MAIL_SERVER', 'smtp.gmail.com')
            mail_port = int(current_app.config.get('MAIL_PORT', 587))
            mail_use_tls = bool(current_app.config.get('MAIL_USE_TLS', True))
            
            with smtplib.SMTP(mail_server, mail_port) as server:
                if mail_use_tls:
                    server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(message)
            
            logger.info(f"Seller rejection email sent to {email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send seller rejection email: {e}")
            return False
    
    @staticmethod
    def send_rider_approval_email(email: str, first_name: str, vehicle_type: str) -> bool:
        """Send approval email to rider"""
        try:
            sender_email = current_app.config.get('MAIL_DEFAULT_SENDER') or current_app.config.get('MAIL_USERNAME')
            sender_password = current_app.config.get('MAIL_PASSWORD')
            
            if not sender_email or not sender_password:
                logger.error("Email configuration missing for rider approval")
                return False
            
            if isinstance(sender_email, tuple):
                sender_email = sender_email[1]
            
            base_url = (current_app.config.get('BASE_URL') or 'http://localhost:5000').rstrip('/')
            login_url = f"{base_url}/auth/login"
            
            message = MIMEMultipart('alternative')
            message['Subject'] = '🚀 Your Rider Application is Approved!'
            message['From'] = f'"Pawfect Finds" <{sender_email}>'
            message['To'] = email
            
            html = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #2E7D32;">🚀 Welcome to Pawfect Finds Riders!</h2>
                        <p>Hello {first_name},</p>
                        <p>Congratulations! Your rider application has been <strong style="color: #2E7D32;">APPROVED</strong>!</p>
                        
                        <div style="background: #e8f5e9; border-left: 4px solid #2E7D32; padding: 15px; margin: 20px 0;">
                            <h4 style="margin-top: 0; color: #1b5e20;">Next Steps:</h4>
                            <ul style="margin: 10px 0; padding-left: 20px;">
                                <li>Log in to your rider account</li>
                                <li>Complete your rider profile</li>
                                <li>View available delivery orders</li>
                                <li>Start earning by accepting deliveries</li>
                            </ul>
                        </div>
                        
                        <div style="background: #f3e5f5; border-left: 4px solid #7b1fa2; padding: 15px; margin: 20px 0;">
                            <p style="margin: 5px 0;"><strong>Vehicle Type:</strong> {vehicle_type}</p>
                        </div>
                        
                        <p style="margin-top: 24px;">
                            <a href="{login_url}" style="background: #2E7D32; color: #ffffff; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold;">Log In Now</a>
                        </p>
                        
                        <p style="margin-top: 20px; color: #666;">If you have any questions, please contact our rider support team.</p>
                        <p style="color: #666; font-size: 12px; margin-top: 30px;">
                            — Pawfect Finds Rider Support<br>
                            <em>Join our delivery network</em>
                        </p>
                    </div>
                </body>
            </html>
            """
            
            message.attach(MIMEText(html, 'html'))
            
            mail_server = current_app.config.get('MAIL_SERVER', 'smtp.gmail.com')
            mail_port = int(current_app.config.get('MAIL_PORT', 587))
            mail_use_tls = bool(current_app.config.get('MAIL_USE_TLS', True))
            
            with smtplib.SMTP(mail_server, mail_port) as server:
                if mail_use_tls:
                    server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(message)
            
            logger.info(f"Rider approval email sent to {email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send rider approval email: {e}")
            return False
    
    @staticmethod
    def send_rider_rejection_email(email: str, first_name: str, reason: str) -> bool:
        """Send rejection email to rider"""
        try:
            sender_email = current_app.config.get('MAIL_DEFAULT_SENDER') or current_app.config.get('MAIL_USERNAME')
            sender_password = current_app.config.get('MAIL_PASSWORD')
            
            if not sender_email or not sender_password:
                logger.error("Email configuration missing for rider rejection")
                return False
            
            if isinstance(sender_email, tuple):
                sender_email = sender_email[1]
            
            message = MIMEMultipart('alternative')
            message['Subject'] = 'Rider Application Status Update'
            message['From'] = f'"Pawfect Finds" <{sender_email}>'
            message['To'] = email
            
            html = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #d32f2f;">Rider Application Status</h2>
                        <p>Hello {first_name},</p>
                        <p>Thank you for your interest in joining Pawfect Finds as a rider. After reviewing your application, we've decided to not approve it at this time.</p>
                        
                        <div style="background: #ffebee; border-left: 4px solid #d32f2f; padding: 15px; margin: 20px 0;">
                            <h4 style="margin-top: 0; color: #b71c1c;">Reason:</h4>
                            <p style="margin: 10px 0;">{reason}</p>
                        </div>
                        
                        <p>You may reapply in the future if you address the concerns noted above. We encourage you to review our rider guidelines and try again.</p>
                        
                        <p style="margin-top: 20px; color: #666;">If you have questions about this decision, please contact our rider support team.</p>
                        <p style="color: #666; font-size: 12px; margin-top: 30px;">
                            — Pawfect Finds Rider Support<br>
                            <em>Join our delivery network</em>
                        </p>
                    </div>
                </body>
            </html>
            """
            
            message.attach(MIMEText(html, 'html'))
            
            mail_server = current_app.config.get('MAIL_SERVER', 'smtp.gmail.com')
            mail_port = int(current_app.config.get('MAIL_PORT', 587))
            mail_use_tls = bool(current_app.config.get('MAIL_USE_TLS', True))
            
            with smtplib.SMTP(mail_server, mail_port) as server:
                if mail_use_tls:
                    server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(message)
            
            logger.info(f"Rider rejection email sent to {email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send rider rejection email: {e}")
            return False
            
            subject = "Your Pawfect Finds Verification Code"
            text_content = f"""Hello,

Your verification code is: {otp_code}

Enter this code in the app to complete your signup.

This code will expire in 10 minutes.

If you didn't request this, you can ignore this email.

— Pawfect Finds"""
            
            response = requests.post(
                url,
                auth=("api", api_key),
                data={
                    "from": f"{sender_name} <{sender_email}>",
                    "to": recipient_email,
                    "subject": subject,
                    "text": text_content
                },
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Mailgun: OTP email sent successfully to {recipient_email}")
                return True
            else:
                logger.error(f"Mailgun API error: {response.status_code} - {response.text}")
                return EmailService._send_via_fallback(recipient_email, otp_code)
                
        except Exception as e:
            logger.error(f"Mailgun error: {e}")
            return EmailService._send_via_fallback(recipient_email, otp_code)
    
    @staticmethod
    def _send_via_resend(recipient_email: str, otp_code: str) -> bool:
        """Send email via Resend API"""
        try:
            api_key = current_app.config.get('RESEND_API_KEY')
            sender_email = current_app.config.get('EMAIL_FROM', 'noreply@pawfectfinds.com')
            sender_name = current_app.config.get('EMAIL_FROM_NAME', 'Pawfect Finds')
            
            if not api_key:
                logger.warning("Resend API key not configured")
                return EmailService._send_via_fallback(recipient_email, otp_code)
            
            url = "https://api.resend.com/emails"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            subject = "Your Pawfect Finds Verification Code"
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #6D4C41;">Verification Code</h2>
                        <p>Hello,</p>
                        <p>Your verification code is:</p>
                        <div style="background: #f5f5f5; padding: 20px; text-align: center; margin: 20px 0;">
                            <h1 style="color: #6D4C41; font-size: 32px; margin: 0; letter-spacing: 5px;">{otp_code}</h1>
                        </div>
                        <p>Enter this code in the app to complete your signup.</p>
                        <p>This code will expire in 10 minutes.</p>
                        <p style="color: #666; font-size: 12px; margin-top: 30px;">
                            If you didn't request this, you can safely ignore this email.<br>
                            — Pawfect Finds
                        </p>
                    </div>
                </body>
            </html>
            """
            
            payload = {
                "from": f"{sender_name} <{sender_email}>",
                "to": [recipient_email],
                "subject": subject,
                "html": html_content
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"Resend: OTP email sent successfully to {recipient_email}")
                return True
            else:
                logger.error(f"Resend API error: {response.status_code} - {response.text}")
                return EmailService._send_via_fallback(recipient_email, otp_code)
                
        except Exception as e:
            logger.error(f"Resend error: {e}")
            return EmailService._send_via_fallback(recipient_email, otp_code)
    
    @staticmethod
    def _send_via_smtp(recipient_email: str, otp_code: str) -> bool:
        """Send email via SMTP (fallback method)"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            from email.utils import formataddr
            
            mail_server = current_app.config.get('MAIL_SERVER', 'smtp.gmail.com')
            mail_port = int(current_app.config.get('MAIL_PORT', 587))
            mail_use_tls = bool(current_app.config.get('MAIL_USE_TLS', True))
            mail_username = current_app.config.get('MAIL_USERNAME')
            mail_password = current_app.config.get('MAIL_PASSWORD')
            sender_name = current_app.config.get('EMAIL_FROM_NAME', 'Pawfect Finds')
            sender_email = current_app.config.get('EMAIL_FROM', mail_username)
            
            if not mail_username or not mail_password:
                return EmailService._send_via_fallback(recipient_email, otp_code)
            
            message = MIMEMultipart("alternative")
            message["Subject"] = "Your Pawfect Finds Verification Code"
            message["From"] = formataddr((sender_name, sender_email or mail_username))
            message["To"] = recipient_email
            
            text_content = f"""Hello,

Your verification code is: {otp_code}

Enter this code in the app to complete your signup.

This code will expire in 10 minutes.

If you didn't request this, you can ignore this email.

— Pawfect Finds"""
            
            part = MIMEText(text_content, "plain")
            message.attach(part)
            
            with smtplib.SMTP(mail_server, mail_port, timeout=15) as server:
                if mail_use_tls:
                    server.starttls()
                server.login(mail_username, mail_password)
                server.sendmail(sender_email or mail_username, [recipient_email], message.as_string())
            
            logger.info(f"SMTP: OTP email sent successfully to {recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"SMTP error: {e}")
            return EmailService._send_via_fallback(recipient_email, otp_code)
    
    @staticmethod
    def _send_via_fallback(recipient_email: str, otp_code: str) -> bool:
        """Fallback: Save OTP to file and console"""
        try:
            import os
            from datetime import datetime
            
            otp_file = os.path.join(current_app.root_path, 'otp_codes.txt')
            
            with open(otp_file, 'a', encoding='utf-8') as f:
                f.write(f"{recipient_email}: {otp_code} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            logger.info(f"OTP saved to file for {recipient_email}: {otp_code}")
            print(f"\n🔐 OTP for {recipient_email}: {otp_code}")
            print(f"📁 OTP also saved to: {otp_file}")
            return True
        except Exception as e:
            logger.error(f"Fallback OTP method failed: {e}")
            print(f"\n🔐 OTP for {recipient_email}: {otp_code}")
            return True

