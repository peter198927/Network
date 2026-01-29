from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.models import db, User, Doctor, Job, JobApplication
from app.decorators import role_required

doctor_bp = Blueprint('doctor', __name__, url_prefix='/doctor', template_folder='../templates/doctor')


@doctor_bp.route('/browse-jobs')
@role_required('doctor')
def browse_jobs():
    """Browse available job listings"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    specialization = request.args.get('specialization', '', type=str)
    location = request.args.get('location', '', type=str)
    
    query = Job.query.filter_by(status='active')
    
    if search:
        query = query.filter(Job.title.ilike(f'%{search}%'))
    
    if specialization:
        query = query.filter(Job.specialization.ilike(f'%{specialization}%'))
    
    if location:
        query = query.filter(Job.location.ilike(f'%{location}%'))
    
    jobs = query.paginate(page=page, per_page=10)
    
    return render_template('browse_jobs.html', jobs=jobs, search=search)


@doctor_bp.route('/apply-job/<int:job_id>', methods=['POST'])
@role_required('doctor')
def apply_job(job_id):
    """Apply for a job"""
    job = Job.query.get_or_404(job_id)
    doctor = Doctor.query.filter_by(user_id=session['user_id']).first()
    
    if not doctor:
        flash('Doctor profile not found', 'danger')
        return redirect(url_for('doctor.browse_jobs'))
    
    # Check if already applied
    existing_application = JobApplication.query.filter_by(
        job_id=job_id, 
        doctor_id=doctor.id
    ).first()
    
    if existing_application:
        flash('You have already applied for this job', 'warning')
        return redirect(url_for('doctor.browse_jobs'))
    
    cover_letter = request.form.get('cover_letter', '')
    
    try:
        application = JobApplication(
            job_id=job_id,
            doctor_id=doctor.id,
            cover_letter=cover_letter,
            status='pending'
        )
        db.session.add(application)
        db.session.commit()
        flash('Application submitted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error submitting application: {str(e)}', 'danger')
    
    return redirect(url_for('doctor.browse_jobs'))


@doctor_bp.route('/my-applications')
@role_required('doctor')
def my_applications():
    """View doctor's job applications"""
    doctor = Doctor.query.filter_by(user_id=session['user_id']).first()
    
    if not doctor:
        flash('Doctor profile not found', 'danger')
        return redirect(url_for('doctor.browse_jobs'))
    
    page = request.args.get('page', 1, type=int)
    applications = JobApplication.query.filter_by(
        doctor_id=doctor.id
    ).order_by(JobApplication.applied_at.desc()).paginate(page=page, per_page=10)
    
    return render_template('applied_jobs.html', applications=applications)


@doctor_bp.route('/profile', methods=['GET', 'POST'])
@role_required('doctor')
def profile():
    """View and edit doctor profile"""
    doctor = Doctor.query.filter_by(user_id=session['user_id']).first()
    
    if not doctor:
        flash('Doctor profile not found', 'danger')
        return redirect(url_for('doctor.browse_jobs'))
    
    if request.method == 'POST':
        try:
            doctor.full_name = request.form.get('full_name', doctor.full_name)
            doctor.specialization = request.form.get('specialization', doctor.specialization)
            doctor.experience_years = request.form.get('experience_years', doctor.experience_years, type=int)
            doctor.phone = request.form.get('phone', doctor.phone)
            doctor.location = request.form.get('location', doctor.location)
            doctor.bio = request.form.get('bio', doctor.bio)
            
            db.session.commit()
            flash('Profile updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {str(e)}', 'danger')
        
        return redirect(url_for('doctor.profile'))
    
    return render_template('profile.html', doctor=doctor)
