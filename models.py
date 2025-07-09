from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class EmailReminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='scheduled')
    scheduled_time = db.Column(db.DateTime, nullable=True)
    sent_time = db.Column(db.DateTime, nullable=True)
    