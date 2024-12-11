import os
from os import abort

from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

from models import Donation, ReceivedDonation

app = Flask(__name__)

# Configure the SQLite database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'e5b168685e6c6fd80555afe9bd8211caa047c074aa2de4fc'
UPLOAD_FOLDER = 'static/profile_pics'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize SQLAlchemy
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = 'login'

# Define User Loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Create User model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'



# Database Model for Donations
class Donation(db.Model):
    food_donation = 'donation'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    food_type = db.Column(db.String(100), nullable=True)  # Changed from nullable=False to nullable=True
    quantity = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def save_donation(self):
        db.session.add(self)
        db.session.commit()



# Route to Home Page
@app.route('/')
def home():
    return render_template('index.html')



# Route to Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()  # Look for user by username

        if user and check_password_hash(user.password, password):  # Check password hash
            login_user(user)  # Use flask-login to handle the user session
            return redirect(url_for('dashboard'))  # Redirect to dashboard after successful login
        else:
            flash('Wrong password! Please try again.', 'error')  # Flash error message for wrong password
            return redirect(url_for('login'))
    return render_template('login.html')



# Route to Register Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Hash the password for security using pbkdf2:sha256
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Check if the user already exists
        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            flash("Username already exists. Please choose another one.", 'danger')
            return redirect(url_for('register'))

        # Create new user and add to the database
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))  # Redirect to login page after successful registration

    return render_template('register.html')


@app.route('/ignore_donation/<int:donation_id>', methods=['POST'])
def ignore_donation(donation_id):
    # Find the donation by ID
    donation = Donation.query.get_or_404(donation_id)

    # Delete the donation
    db.session.delete(donation)
    db.session.commit()

    # Redirect to the donations view page after deletion
    return redirect(url_for('donor_dashboard'))


# Route to Dashboard (only accessible after login)
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')




# Route for admin dashboard
@app.route('/admin')
@login_required
def admin():
    donations = Donation.query.all()  # List all donations
    return render_template('admin.html', donations=donations)


@app.route('/donate', methods=['GET', 'POST'])
def donate():
    if request.method == 'POST':
        # Handle the form submission for donation
        contact = request.form['contact']
        donor_name = request.form['donor_name']
        food_type = request.form['food_type']
        quantity = request.form['quantity']
        manual_location = request.form.get('manual_location')  # Get the manual location if any

        # If a manual location is provided, use it instead
        if manual_location:
            location = manual_location

        # Save donation to the database
        new_donation = Donation(

            food_type=food_type,
            quantity=quantity,

        )
        db.session.add(new_donation)
        db.session.commit()

        flash('Donation successfully added!', 'success')
        return redirect(url_for('donor_dashboard'))

    total_donations = Donation.query.count()  # For example, count total donations
    goal = 1000  # Set the goal in kg
    suggested_items = ['Rice', 'Wheat', 'Vegetables']  # Example suggested items
    nearby_places = ['Community Center', 'Central Park', 'Food Bank', 'Church Hall', 'Library']  # Example nearby places

    return render_template(
        'donate.html',
        total_donations=total_donations,
        goal=goal,
        suggested_items=suggested_items,
        nearby_places=nearby_places
    )



@app.route('/view_donations')
@login_required
def view_donations():
    # Retrieve all donations from the database
    donations = Donation.query.all()  # Adjust as needed to filter donations by user or criteria
    return render_template('view_donations.html', donations=donations)



@app.route('/manage_users')
def manage_users():
    users = User.query.all()  # Fetch all users from the database
    return render_template('manage_users.html', users=users)

# Route to delete a user
@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully.', 'success')
    else:
        flash('User not found.', 'error')
    return redirect(url_for('manage_users'))


@app.route('/view_reports')
@login_required
def view_reports():
    # Fetch donation data
    donations = Donation.query.all()

    # Process donation data for reporting
    report_data = {}
    for donation in donations:
        food_type = donation.food_type
        if food_type in report_data:
            report_data[food_type] += donation.quantity
        else:
            report_data[food_type] = donation.quantity

    return render_template('view_reports.html', report_data=report_data)

@app.route('/about')
def about():
    return render_template('about.html')  # Ensure the 'about.html' template exists


@app.route('/active_donors')
def active_donors():
    # Query for all completed donations
    completed_donations = Donation.query.filter_by(status='Completed').all()
    return render_template('active_donors.html', donations=completed_donations)




@app.route('/check_user')
def check_user():
    if current_user.is_authenticated:
        return f"User ID: {current_user.id}, Username: {current_user.username}"
    else:
        return "No user is logged in."


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        # Update user settings
        current_user.username = request.form['username']
        current_user.email = request.form['email']

        # Update password if provided
        password = request.form['password']
        if password:  # Only update if a new password is provided
            current_user.password = generate_password_hash(password, method='pbkdf2:sha256')

        # Update notification settings (assuming you have a field for it)
        current_user.notification = request.form['notification']

        db.session.commit()  # Save changes to the database
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('settings'))

    return render_template('settings.html', user=current_user)

@app.route('/donation_detail/<int:donation_id>', methods=['GET'])
def donation_detail(donation_id):
    donation = Donation.query.get_or_404(donation_id)
    return render_template('donation_detail.html', donation=donation)



@app.route('/received_donations', methods=['GET'])
def received_donations():
    donations = Donation.query.all()  # Example, replace with your actual logic
    return render_template('received.html', donations=donations)
donations_data = [
    {
        'id': 1,
        'donor_name': 'Alice Smith',
        'food_type': 'Fruits',
        'quantity': '15 kg',
        'address': '456 Oak Lane',
        'date': datetime(2024, 12, 1)
    },
    {
        'id': 2,
        'donor_name': 'Bob Johnson',
        'food_type': 'Vegetables',
        'quantity': '20 kg',
        'address': '789 Pine Street',
        'date': datetime(2024, 12, 2)
    }
]

# Global list to store accepted donations
accepted_donations = []


@app.route('/accept_donation/<int:donation_id>', methods=['POST'])
def accept_donation(donation_id):
    # Find the donation by ID
    donation = Donation.query.get_or_404(donation_id)

    # Mark the donation as accepted (example)
    donation.status = 'accepted'

    # Commit changes to the database
    db.session.commit()

    # Redirect to the received donations page
    return redirect(url_for('received_donations'))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload_profile_picture/<int:user_id>', methods=['POST'])
def upload_profile_picture(user_id):
    user = User.query.get_or_404(user_id)

    # Check if the post request has the file part
    if 'profile_picture' not in request.files:
        return redirect(request.url)

    file = request.files['profile_picture']

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # Update user's profile picture in the database
        user.profile_picture = filename
        db.session.commit()

        # After saving, reload the users page to reflect the new profile picture
        return redirect(url_for('manage_users'))

    return "Invalid file type or no file selected", 400


@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user_by_id(user_id):  # Renamed function to avoid conflict
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully.', 'success')
    else:
        flash('User not found.', 'error')
    return redirect(url_for('manage_users'))


@app.route('/profile', methods=['GET', 'POST'])
@login_required  # Ensure the user is logged in
def profile():
    user = current_user  # Get the logged-in user

    if request.method == 'POST':
        # Handle file upload
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Update the user's profile picture in the database
            user.profile_picture = f'uploads/{filename}'
            db.session.commit()
            flash('Profile picture updated successfully!')
            return redirect(url_for('profile'))
        else:
            flash('Invalid file type')

    return render_template('profile.html', user=user)

@app.route('/donor_dashboard')
def donor_dashboard():
    donations = Donation.query.all()
    return render_template('donor_dashboard.html', donations=donations)

@app.route('/update_total_donations', methods=['POST'])
def update_total_donations():
    total_donations = request.form['total_donations']
    # Add logic to update the donation total in the database or session
    return redirect(url_for('dashboard'))  # Redirect to the dashboard after updating


@app.route('/logout')
@login_required
def logout():
    logout_user()  # Use flask-login to handle logout
    return redirect(url_for('login'))

# Create all database tables (you only need to do this once)
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
