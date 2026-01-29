from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import db, JobListing, DoctorProfile, applications
from app.decorators import role_required, verified_required

doctor_bp = Blueprint('doctor', __name__)

@doctor_bp.route('/jobs')
@login_required
@role_required('doctor')
def browse_jobs():
    # Only show active jobs from verified hospitals
    jobs = JobListing.query.filter_by(is_active=True).all()
    return render_template('doctor/browse_jobs.html', jobs=jobs)

@doctor_bp.route('/apply/<int:job_id>', methods=['POST'])
@login_required
@role_required('doctor')
@verified_required
def apply_to_job(job_id):
    doctor = DoctorProfile.query.filter_by(user_id=current_user.id).first()
    job = JobListing.query.get_or_404(job_id)
    
    # Check if already applied
    existing_app = db.session.query(applications).filter_by(
        doctor_id=doctor.id, job_id=job.id
    ).first()
    
    if existing_app:
        flash("You have already applied for this position.", "info")
    else:
        # Append to the relationship
        doctor.applied_jobs.append(job)
        db.session.commit()
        flash(f"Application submitted for {job.title}!", "success")
        
    return redirect(url_for('doctor.browse_jobs'))

@doctor_bp.route('/my-applications')
@login_required
@role_required('doctor')
def my_applications():
    doctor = DoctorProfile.query.filter_by(user_id=current_user.id).first()
    # Querying the association table to get statuses
    apps = db.session.query(JobListing.title, HospitalProfile.name, applications.c.status, applications.c.applied_at)\
        .join(applications, JobListing.id == applications.c.job_id)\
        .join(HospitalProfile, JobListing.hospital_id == HospitalProfile.id)\
        .filter(applications.c.doctor_id == doctor.id).all()
        
    return render_template('doctor/applied_jobs.html', applications=apps)