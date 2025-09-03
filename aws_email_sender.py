#!/usr/bin/env python3
"""
AWS SES Email Sender
Sends emails using AWS Simple Email Service (SES) via boto3
"""

import boto3
from botocore.exceptions import ClientError
import os
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

class AWSEmailSender:
    def __init__(self, region_name='us-east-1'):
        """
        Initialize AWS SES client
        
        Args:
            region_name (str): AWS region name (default: us-east-1)
        """
        self.region_name = region_name
        self.ses_client = boto3.client('ses', region_name=region_name)
        
    def send_email(self, sender_email, recipient_emails, subject, html_content, text_content=None, cc_emails=None, bcc_emails=None):
        """
        Send email using AWS SES
        
        Args:
            sender_email (str): Verified sender email address
            recipient_emails (list): List of recipient email addresses
            subject (str): Email subject
            html_content (str): HTML content of the email
            text_content (str, optional): Plain text content of the email
            cc_emails (list, optional): List of CC email addresses
            bcc_emails (list, optional): List of BCC email addresses
            
        Returns:
            dict: Response from AWS SES
        """
        try:
            # Prepare destination
            destination = {
                'ToAddresses': recipient_emails
            }
            
            if cc_emails:
                destination['CcAddresses'] = cc_emails
            if bcc_emails:
                destination['BccAddresses'] = bcc_emails
            
            # Prepare message
            message = {
                'Subject': {
                    'Data': subject,
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Html': {
                        'Data': html_content,
                        'Charset': 'UTF-8'
                    }
                }
            }
            
            # Add text content if provided
            if text_content:
                message['Body']['Text'] = {
                    'Data': text_content,
                    'Charset': 'UTF-8'
                }
            
            # Send email
            response = self.ses_client.send_email(
                Source=sender_email,
                Destination=destination,
                Message=message
            )
            
            return response
            
        except ClientError as e:
            print(f"Error sending email: {e}")
            return None
    
    def send_raw_email(self, sender_email, recipient_emails, subject, html_content, text_content=None):
        """
        Send raw email using AWS SES (useful for complex HTML emails)
        
        Args:
            sender_email (str): Verified sender email address
            recipient_emails (list): List of recipient email addresses
            subject (str): Email subject
            html_content (str): HTML content of the email
            text_content (str, optional): Plain text content of the email
            
        Returns:
            dict: Response from AWS SES
        """
        try:
            # Create MIME message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = sender_email
            msg['To'] = ', '.join(recipient_emails)
            
            # Add text content if provided
            if text_content:
                text_part = MIMEText(text_content, 'plain', 'utf-8')
                msg.attach(text_part)
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Send raw email
            response = self.ses_client.send_raw_email(
                Source=sender_email,
                Destinations=recipient_emails,
                RawMessage={'Data': msg.as_string()}
            )
            
            return response
            
        except ClientError as e:
            print(f"Error sending raw email: {e}")
            return None
    
    def verify_email_address(self, email_address):
        """
        Verify an email address with AWS SES
        
        Args:
            email_address (str): Email address to verify
            
        Returns:
            bool: True if verification request was sent successfully
        """
        try:
            response = self.ses_client.verify_email_identity(
                EmailAddress=email_address
            )
            print(f"Verification email sent to {email_address}")
            return True
        except ClientError as e:
            print(f"Error verifying email address: {e}")
            return False
    
    def get_send_quota(self):
        """
        Get current sending quota and rate from AWS SES
        
        Returns:
            dict: Quota information
        """
        try:
            response = self.ses_client.get_send_quota()
            return response
        except ClientError as e:
            print(f"Error getting send quota: {e}")
            return None

def load_html_template(template_path):
    """
    Load HTML template from file
    
    Args:
        template_path (str): Path to HTML template file
        
    Returns:
        str: HTML content
    """
    try:
        with open(template_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Template file not found: {template_path}")
        return None
    except Exception as e:
        print(f"Error reading template file: {e}")
        return None

def main():
    """
    Main function to send email using AWS SES
    """
    # Configuration
    AWS_REGION = 'us-east-1'  # Change to your preferred region
    SENDER_EMAIL = 'your-verified-email@example.com'  # Must be verified in AWS SES
    RECIPIENT_EMAILS = [
        'olgamikhalenka97@gmail.com',
        'volha.mikhalenka@blackrock.com'
    ]
    EMAIL_SUBJECT = 'Preqin Updates - AWS SES Test'
    TEMPLATE_PATH = 'template.html'
    
    # Initialize email sender
    email_sender = AWSEmailSender(region_name=AWS_REGION)
    
    # Load HTML template
    print("Loading HTML template...")
    html_content = load_html_template(TEMPLATE_PATH)
    
    if not html_content:
        print("Failed to load template. Exiting.")
        return
    
    print("Template loaded successfully!")
    
    # Create plain text version (optional)
    text_content = """
    Preqin Updates
    
    This is a test email sent using AWS SES.
    
    Please view this email in HTML format for the full experience.
    
    Best regards,
    Preqin Team
    """
    
    # Send email
    print("Sending email via AWS SES...")
    response = email_sender.send_raw_email(
        sender_email=SENDER_EMAIL,
        recipient_emails=RECIPIENT_EMAILS,
        subject=EMAIL_SUBJECT,
        html_content=html_content,
        text_content=text_content
    )
    
    if response:
        print("✅ Email sent successfully!")
        print(f"Message ID: {response['MessageId']}")
        
        # Print quota information
        quota_info = email_sender.get_send_quota()
        if quota_info:
            print(f"\nSending Quota Information:")
            print(f"Max 24 Hour Send: {quota_info['Max24HourSend']}")
            print(f"Max Send Rate: {quota_info['MaxSendRate']} emails/second")
            print(f"Sent Last 24 Hours: {quota_info['SentLast24Hours']}")
    else:
        print("❌ Failed to send email")

if __name__ == "__main__":
    # Check if AWS credentials are configured
    try:
        # Test AWS credentials
        sts_client = boto3.client('sts')
        identity = sts_client.get_caller_identity()
        print(f"AWS Account: {identity['Account']}")
        print(f"AWS User/Role: {identity['Arn']}")
        print(f"AWS Region: {identity['Account']}")
        
        # Run main function
        main()
        
    except Exception as e:
        print(f"AWS credentials not configured or invalid: {e}")
        print("\nTo configure AWS credentials:")
        print("1. Install AWS CLI: pip install awscli")
        print("2. Configure credentials: aws configure")
        print("3. Or set environment variables:")
        print("   export AWS_ACCESS_KEY_ID=your_access_key")
        print("   export AWS_SECRET_ACCESS_KEY=your_secret_key")
        print("   export AWS_DEFAULT_REGION=us-east-1")
        print("\nMake sure your sender email is verified in AWS SES console.")
