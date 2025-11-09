from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
# Initialize SQLAlchemy instance
db = SQLAlchemy()

# Example User model
class User(db.Model):
    __tablename__ = "users"   # table name in database
    
    id = db.Column(db.Integer, primary_key=True)  # primary key
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"<User {self.name}>"
    

    
class Prediction(db.Model):
    __tablename__ = 'predictions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    symbol = db.Column(db.String(10), nullable=False)
    mode = db.Column(db.String(10), nullable=False)
    value = db.Column(db.Integer, nullable=False)
    current_price = db.Column(db.Float, nullable=False)
    predicted_price = db.Column(db.Float, nullable=False)
    high = db.Column(db.Float, nullable=False)
    low = db.Column(db.Float, nullable=False)
    direction = db.Column(db.String(10), nullable=False)
    confidence = db.Column(db.Float, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)