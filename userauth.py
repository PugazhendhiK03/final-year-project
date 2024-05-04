from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask import flash

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

def register_user(username, password):
    # Check if the username already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        # Username already exists, handle accordingly (e.g., display error message)
        flash('Username already exists. Please choose a different username.', 'danger')
        return False

    # Hash the password before saving it to the database
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    # Create a new user record with the hashed password
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    flash('Registration successful! Please log in.', 'success')
    return True

def login_user(username, password):
    user = User.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password, password):
        return True
    else:
        return False




