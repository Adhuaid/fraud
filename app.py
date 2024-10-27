from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
import os  # Import os for generating a secret key

app = Flask(__name__)

# Set up your database configuration here
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'  # Example: using SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Set the secret key for session management
app.secret_key = os.urandom(24)  # Generate a random secret key

db = SQLAlchemy(app)  # Correctly initialize SQLAlchemy with the app

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# Contact Message model
class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    contact_number = db.Column(db.String(15), nullable=False)
    message = db.Column(db.Text, nullable=False)

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'  # your email
app.config['MAIL_PASSWORD'] = 'your_app_password'  # your app password
mail = Mail(app)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if authenticate(username, password):  # Use the defined function
            session['user_id'] = User.query.filter_by(username=username).first().id  # Store user ID in session
            return redirect(url_for('home'))  # Redirect to home
        else:
            flash('Invalid username or password!', 'danger')  # Flash a message for invalid login
            return redirect(url_for('login'))  # Redirect back to login

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Validate and save the new user to the database
        if username and password:  # Add more validation as needed
            hashed_password = generate_password_hash(password)  # Default method used
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('login'))

    return render_template('register.html')

def authenticate(username, password):
    # Find the user by username
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        # If user exists and password is correct
        return True
    return False

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])  # Update to accept POST requests
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        contact_number = request.form['contact']
        message = request.form['message']

        # Save the contact message to the database
        new_message = ContactMessage(name=name, email=email, contact_number=contact_number, message=message)
        db.session.add(new_message)
        db.session.commit()

        # Send an email with the message
        msg = Message("New Contact Message", recipients=[app.config['MAIL_USERNAME']])
        msg.body = f"Name: {name}\nEmail: {email}\nContact Number: {contact_number}\nMessage: {message}"
        mail.send(msg)

        flash("Your message has been sent successfully!", "success")
        return redirect(url_for('contact'))  # Redirect to contact page after submission

    return render_template('contact.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Please log in first", "warning")
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Logged out successfully!", "info")
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create the tables
    app.run(debug=True)
