from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.models import db, User, Doctor, Hospital
from werkzeug.security import generate_password_hash
from datetime import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/auth', template_folder='../templates/auth')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route"""
    if request.method == 'POST':
        data = request.form
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        role = data.get('role')  # 'doctor' or 'hospital'
        
        # Validation
        if not all([username, email, password, confirm_password, role]):
            flash('All fields are required', 'danger')
            return redirect(url_for('auth.register'))
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('auth.register'))
        
        try:
            # Create user
            user = User(username=username, email=email, role=role, is_verified=False)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            
            # Create role-specific profile
            if role == 'doctor':
                doctor = Doctor(user_id=user.id, full_name='', specialization='')
                db.session.add(doctor)
            elif role == 'hospital':
                hospital = Hospital(user_id=user.id, hospital_name='')
                db.session.add(hospital)
            
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error during registration: {str(e)}', 'danger')
            return redirect(url_for('auth.register'))
    
    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login route"""
    if request.method == 'POST':
        data = request.form
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            flash('Username and password required', 'danger')
            return redirect(url_for('auth.login'))
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            session['email'] = user.email
            session['is_verified'] = user.is_verified
            
            flash(f'Welcome back, {username}!', 'success')
            
            # Redirect based on role
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user.role == 'doctor':
                return redirect(url_for('doctor.browse_jobs'))
            else:  # hospital
                return redirect(url_for('hospital.dashboard'))
        else:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))
    
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    """User logout route"""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))
