from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from datetime import datetime
from flask_login import UserMixin
import sqlite3

from sqlalchemy.engine import cursor

conn = sqlite3.connect(r"C:\Users\bhoot\downloads\bhootharaju\mydatabase.db")

db = SQLAlchemy()
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    notification = db.Column(db.String(10), default='enabled')  # New field for notification settings

    def __repr__(self):
        return f'<User  {self.username}>'

class Donation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    food_type = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    donor_name = db.Column(db.String(200), nullable=False)
    contact = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    address = db.Column(db.String(200), nullable=False)  # Donor Address field
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default="Pending")
  # Ensure this line is correct

    def save_donation(self):
        db.session.add(self)
        db.session.commit()

class FoodDonation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    food_type = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), default='available')  # Track availability
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='food_donations', lazy=True)

    def __repr__(self):
        return f"FoodDonation('{self.food_type}', '{self.quantity}', '{self.status}')"

class ReceivedDonation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    food_type = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    donation_id = db.Column(db.Integer, db.ForeignKey('donation.id'), nullable=False)

    # Optional: Relationship to Donation
    donation = db.relationship('Donation', backref='received')
class DonationCount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    total_donations = db.Column(db.Integer, default=0)