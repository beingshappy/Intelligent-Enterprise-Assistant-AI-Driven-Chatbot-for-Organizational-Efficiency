import os
import random
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class OTPService:
    @staticmethod
    def generate_otp():
        return str(random.randint(100000, 999999))

    @staticmethod
    def send_otp(email: str, otp: str):
        # ALWAYS Save to file for easy demo access
        try:
            with open("demo_otp.txt", "w") as f:
                f.write(f"EMAIL: {email}\nOTP: {otp}\nTIME: {datetime.now().strftime('%H:%M:%S')}")
        except:
            pass

        # Configuration
        smtp_host = os.getenv("SMTP_HOST")
        smtp_port = int(os.getenv("SMTP_PORT", 587))
        smtp_user = os.getenv("SMTP_USER")
        smtp_password = os.getenv("SMTP_PASSWORD")
        email_from = os.getenv("EMAIL_FROM")

        if not all([smtp_host, smtp_user, smtp_password, email_from]):
            print("\n" + "="*50)
            print("[SERVER] DEMO MODE: OTP VERIFICATION CODE")
            print(f"EMAIL TO:  {email}")
            print(f"VERIFY CODE: {otp}")
            print("="*50 + "\n")
            return True

        try:
            msg = MIMEText(f"Your verification code for Enterprise Assistant is: {otp}")
            msg['Subject'] = f"{otp} is your verification code"
            msg['From'] = email_from
            msg['To'] = email

            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
            return True
        except Exception as e:
            # PURE TEXT FALLBACK
            print(f"\n[ERROR] FAILED TO SEND EMAIL: {e}")
            print("="*50)
            print("[SERVER] FALLBACK: OTP VERIFICATION CODE")
            print(f"EMAIL TO:  {email}")
            print(f"VERIFY CODE: {otp}")
            print("="*50 + "\n")
            return False

otp_service = OTPService()
