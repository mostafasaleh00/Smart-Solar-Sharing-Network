import os
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from app.models import User, users

bp = Blueprint('auth', __name__, url_prefix='/auth')

UPLOAD_FOLDER = 'app/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        location = request.form.get('location')
        
        if email in [user.email for user in users.values()]:
            flash('Email already registered', 'danger')
            return redirect(url_for('auth.register'))
        
        user_id = str(len(users) + 1)
        user = User(id=user_id, name=name, email=email, role=role, location=location)
        user.set_password(password)
        users[user_id] = user
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = next((user for user in users.values() if user.email == email), None)
        
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash('Invalid email or password', 'danger')
            
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('auth.login'))

@bp.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html')

@bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    name = request.form.get('name')
    location = request.form.get('location')
    password = request.form.get('password')
    
    user = users[current_user.id]
    user.name = name
    user.location = location
    
    if password:
        user.set_password(password)
    
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('auth.profile'))

@bp.route('/profile/upload-picture', methods=['POST'])
@login_required
def upload_profile_picture():
    if 'profile_picture' not in request.files:
        flash('No file selected', 'danger')
        return redirect(url_for('auth.profile'))
        
    file = request.files['profile_picture']
    
    if file.filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('auth.profile'))
        
    if file and allowed_file(file.filename):
        # Create upload folder if it doesn't exist
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Remove old profile picture if it exists
        if current_user.profile_picture:
            old_picture_path = os.path.join(UPLOAD_FOLDER, current_user.profile_picture)
            if os.path.exists(old_picture_path):
                os.remove(old_picture_path)
        
        # Save new profile picture
        filename = secure_filename(f"profile_{current_user.id}_{file.filename}")
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        
        # Update user profile
        user = users[current_user.id]
        user.profile_picture = filename
        
        flash('Profile picture updated successfully!', 'success')
    else:
        flash('Invalid file type. Please use PNG, JPG, JPEG, or GIF.', 'danger')
        
    return redirect(url_for('auth.profile')) 