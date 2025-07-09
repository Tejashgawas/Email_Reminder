from flask import Flask, request, jsonify,render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from models import db, EmailReminder
from tasks import send_email_task
import config

app = Flask(__name__)
app.config.from_object(config.Config)
db.init_app(app)


with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/schedule-email', methods=['POST'])
def schedule_email():
    data = request.get_json()
    email = data.get('email')
    message = data.get('message')
    delay = int(data.get('delay', 30))  # default delay = 30s

    reminder = EmailReminder(
        email=email,
        message=message,
        status='scheduled',
        scheduled_time=datetime.utcnow() + timedelta(seconds=delay)
    )
    db.session.add(reminder)
    db.session.commit()

    send_email_task.apply_async(args=[reminder.id], countdown=delay)

    return jsonify({"message": "Email scheduled successfully", "id": reminder.id}), 200

@app.route('/emails', methods=['GET'])
def get_emails():
    reminders = EmailReminder.query.all()
    result = [
        {
            "id": r.id,
            "email": r.email,
            "message": r.message,
            "status": r.status,
            "scheduled_time": r.scheduled_time.strftime('%Y-%m-%d %H:%M:%S') if r.scheduled_time else None,
            "sent_time": r.sent_time.strftime('%Y-%m-%d %H:%M:%S') if r.sent_time else None
        } for r in reminders
    ]
    return jsonify(result), 200

@app.route('/delete/<int:id>', methods=['GET'])
def delete_email(id):
    reminder = EmailReminder.query.get(id)
    if not reminder:
        return jsonify({"message": "Reminder not found"}), 404

    db.session.delete(reminder)
    db.session.commit()
    return jsonify({"message": "Reminder deleted successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)
