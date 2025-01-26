import json
import os
import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
import time

class LogistixEmailSender:
    def __init__(self):
        self.config = self.load_config()
        # Email credentials - you should set these as environment variables
        self.sender_email = os.getenv('LOGISTIX_EMAIL')
        self.sender_password = os.getenv('LOGISTIX_EMAIL_PASSWORD')
        
    def load_config(self):
        with open('config.json', 'r') as f:
            return json.load(f)
            
    def check_config(self):
        if 'email' not in self.config['contractor']:
            print("Error: No contractor email found in config.json")
            return False
        if not self.sender_email or not self.sender_password:
            print("Error: Email credentials not set in environment variables")
            print("Please set LOGISTIX_EMAIL and LOGISTIX_EMAIL_PASSWORD")
            return False
        return True
        
    def find_zip_files(self):
        contractor_key = self.config['contractor']['key']
        contracts_dir = Path('contracts') / contractor_key
        
        if not contracts_dir.exists():
            return []
            
        zip_files = []
        for contract_dir in contracts_dir.iterdir():
            if contract_dir.is_dir():
                for file in contract_dir.glob('*.zip'):
                    zip_files.append(file)
        return zip_files
        
    def send_email(self, zip_files):
        if not zip_files:
            print("No zip files found to send")
            return
            
        receiver_email = self.config['contractor']['email']
        
        # Create the email message
        message = MIMEMultipart()
        message["From"] = self.sender_email
        message["To"] = receiver_email
        message["Subject"] = "Logistix Package Delivery"
        
        # Add body to email
        body = f"Hello,\n\nAttached are {len(zip_files)} package(s) from your Logistix requests:\n\n"
        body += "\n".join([f"- {zip_file.name}" for zip_file in zip_files])
        body += "\n\nBest regards,\nLogistix System"
        
        message.attach(MIMEText(body, "plain"))
        
        # Attach zip files
        for zip_file in zip_files:
            with open(zip_file, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
                
            encoders.encode_base64(part)
            
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {zip_file.name}",
            )
            
            message.attach(part)
            
        # Create secure SSL/TLS connection and send email
        context = ssl.create_default_context()
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, receiver_email, message.as_string())
                print(f"Email sent successfully to {receiver_email}")
                
                # After successful sending, optionally move or delete zip files
                for zip_file in zip_files:
                    # Option 1: Delete the zip file
                    # zip_file.unlink()
                    # Option 2: Move to sent folder
                    sent_dir = zip_file.parent / 'sent'
                    sent_dir.mkdir(exist_ok=True)
                    zip_file.rename(sent_dir / zip_file.name)
                    
        except Exception as e:
            print(f"Error sending email: {e}")

    def run(self, interval=300):  # Default check every 5 minutes
        print("Starting Logistix Email Sender...")
        
        if not self.check_config():
            return
            
        while True:
            print("\nChecking for new zip files...")
            zip_files = self.find_zip_files()
            
            if zip_files:
                print(f"Found {len(zip_files)} zip file(s):")
                for zip_file in zip_files:
                    print(f"- {zip_file}")
                self.send_email(zip_files)
            else:
                print("No new zip files found")
                
            print(f"Waiting {interval} seconds before next check...")
            time.sleep(interval)

if __name__ == "__main__":
    email_sender = LogistixEmailSender()
    email_sender.run() 