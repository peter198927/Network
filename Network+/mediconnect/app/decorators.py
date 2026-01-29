from flask import session, redirect, url_for, abort
from functools import wraps


def role_required(*roles):
    """
    Decorator to enforce role-based access control.
    
    Usage:
        @app.route('/admin')
        @role_required('admin')
        def admin_dashboard():
            pass
        
        @app.route('/jobs')
        @role_required('doctor', 'hospital')
        def view_jobs():
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if user is logged in
            if 'user_id' not in session:
                return redirect(url_for('auth.login'))
            
            # Check if user has required role
            user_role = session.get('role')
            if user_role not in roles:
                abort(403)  # Forbidden
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function