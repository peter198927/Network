from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.models import db, User, Doctor, Hospital, Job, JobApplication
from app.decorators import role_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin', template_folder='../templates/admin')


@admin_bp.route('/dashboard')
@role_required('admin')
def dashboard():
    """Admin dashboard with system statistics"""
    stats = {
        'total_users': User.query.count(),
        'verified_users': User.query.filter_by(is_verified=True).count(),
        'unverified_users': User.query.filter_by(is_verified=False).count(),
        'doctors': User.query.filter_by(role='doctor').count(),
        'hospitals': User.query.filter_by(role='hospital').count(),
        'total_jobs': Job.query.count(),
        'active_jobs': Job.query.filter_by(status='active').count(),
        'total_applications': JobApplication.query.count()
    }
    
    return render_template('dashboard.html', stats=stats)


@admin_bp.route('/users')
@role_required('admin')
def users():
    """Manage all users"""
    page = request.args.get('page', 1, type=int)
    role_filter = request.args.get('role', '', type=str)
    
    query = User.query
    
    if role_filter:
        query = query.filter_by(role=role_filter)
    
    users_list = query.order_by(User.created_at.desc()).paginate(page=page, per_page=10)
    
    return render_template('users.html', users=users_list, role_filter=role_filter)


@admin_bp.route('/user/<int:user_id>/verify', methods=['POST'])
@role_required('admin')
def verify_user(user_id):
    """Verify a user account"""
    user = User.query.get_or_404(user_id)
    
    try:
        user.is_verified = True
        db.session.commit()
        flash(f'User {user.username} verified successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error verifying user: {str(e)}', 'danger')
    
    return redirect(url_for('admin.users'))


@admin_bp.route('/user/<int:user_id>/deactivate', methods=['POST'])
@role_required('admin')
def deactivate_user(user_id):
    """Deactivate a user account"""
    user = User.query.get_or_404(user_id)
    
    # Prevent self-deactivation
    if user.id == session.get('user_id'):
        flash('Cannot deactivate your own account', 'danger')
        return redirect(url_for('admin.users'))
    
    try:
        db.session.delete(user)
        db.session.commit()
        flash(f'User {user.username} deactivated', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deactivating user: {str(e)}', 'danger')
    
    return redirect(url_for('admin.users'))


@admin_bp.route('/jobs')
@role_required('admin')
def jobs():
    """Manage all job postings"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '', type=str)
    
    query = Job.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    jobs_list = query.order_by(Job.created_at.desc()).paginate(page=page, per_page=10)
    
    return render_template('jobs.html', jobs=jobs_list, status_filter=status_filter)


@admin_bp.route('/job/<int:job_id>/close', methods=['POST'])
@role_required('admin')
def close_job(job_id):
    """Close a job posting"""
    job = Job.query.get_or_404(job_id)
    
    try:
        job.status = 'closed'
        db.session.commit()
        flash(f'Job "{job.title}" closed', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error closing job: {str(e)}', 'danger')
    
    return redirect(url_for('admin.jobs'))


@admin_bp.route('/applications')
@role_required('admin')
def applications():
    """View all job applications"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '', type=str)
    
    query = JobApplication.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    applications_list = query.order_by(JobApplication.applied_at.desc()).paginate(page=page, per_page=10)
    
    return render_template('applications.html', applications=applications_list, status_filter=status_filter)


@admin_bp.route('/reports')
@role_required('admin')
def reports():
    """View system reports"""
    # Job statistics
    job_stats = {
        'by_status': db.session.query(Job.status, db.func.count(Job.id)).group_by(Job.status).all(),
        'by_specialization': db.session.query(Job.specialization, db.func.count(Job.id)).group_by(Job.specialization).all()
    }
    
    # Application statistics
    app_stats = {
        'by_status': db.session.query(JobApplication.status, db.func.count(JobApplication.id)).group_by(JobApplication.status).all()
    }
    
    # User statistics
    user_stats = {
        'by_role': db.session.query(User.role, db.func.count(User.id)).group_by(User.role).all(),
        'by_verification': db.session.query(User.is_verified, db.func.count(User.id)).group_by(User.is_verified).all()
    }
    
    return render_template('reports.html', job_stats=job_stats, app_stats=app_stats, user_stats=user_stats)
