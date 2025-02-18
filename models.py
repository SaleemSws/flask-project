from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    due_date = db.Column(db.DateTime, nullable=True)  # วันที่กำหนดส่ง
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # วันที่สร้าง
    completed_at = db.Column(db.DateTime, nullable=True)  # วันที่งานเสร็จ

    def mark_complete(self):
        self.completed = True
        self.completed_at = datetime.utcnow()
