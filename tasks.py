import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv
from datetime import datetime

from celery import Celery
from flask import Flask
from config import Config
from models import db, EmailReminder

# Load environment variables
load_dotenv()

# Setup minimal Flask app context for Celery
flask_app = Flask(__name__)
flask_app.config.from_object(Config)
db.init_app(flask_app)

# Setup Celery
celery = Celery(__name__, broker=Config.CELERY_BROKER_URL, backend=Config.CELERY_RESULT_BACKEND)

@celery.task
def send_email_task(reminder_id):
    with flask_app.app_context():
        reminder = EmailReminder.query.get(reminder_id)
        if reminder:
            try:
                # Load secrets from .env
                email_user = os.getenv("EMAIL_USER")
                email_pass = os.getenv("EMAIL_PASS")

                # Create email
                msg = EmailMessage()
                msg['Subject'] = "Your Scheduled Reminder"
                msg['From'] = email_user
                msg['To'] = reminder.email
                msg.set_content(reminder.message)

                # Send email
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    smtp.login(email_user, email_pass)
                    smtp.send_message(msg)

                # Update DB
                reminder.status = 'sent'
                reminder.sent_time = datetime.utcnow()
                db.session.commit()
                print("✅ Email sent!")

            except Exception as e:
                print("❌ Failed to send email:", e)
                reminder.status = 'failed'
                db.session.commit()
