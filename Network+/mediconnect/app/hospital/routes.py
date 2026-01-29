from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.models import db, User, Hospital, Job, JobApplication, Doctor
from app.decorators import role_required

hospital_bp = Blueprint('hospital', __name__, url_prefix='/hospital', template_folder='../templates/hospital')


@hospital_bp.route('/dashboard')
@role_required('hospital')
def dashboard():
    """Hospital dashboard"""
    hospital = Hospital.query.filter_by(user_id=session['user_id']).first()
    
    if not hospital:
        flash('Hospital profile not found', 'danger')
        return redirect(url_for('auth.login'))
    
    stats = {
        'total_jobs': Job.query.filter_by(hospital_id=hospital.id).count(),
        'active_jobs': Job.query.filter_by(hospital_id=hospital.id, status='active').count(),
        'total_applications': db.session.query(JobApplication).join(Job).filter(
            Job.hospital_id == hospital.id
        ).count(),
        'pending_applications': db.session.query(JobApplication).join(Job).filter(
            Job.hospital_id == hospital.id,
            JobApplication.status == 'pending'
        ).count()
    }
    
    return render_template('dashboard.html', hospital=hospital, stats=stats)


@hospital_bp.route('/post-job', methods=['GET', 'POST'])
@role_required('hospital')
def post_job():
    """Post a new job"""
    hospital = Hospital.query.filter_by(user_id=session['user_id']).first()
    
    if not hospital:
        flash('Hospital profile not found', 'danger')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        try:
            job = Job(
                hospital_id=hospital.id,
                title=request.form.get('title'),
                specialization=request.form.get('specialization'),
                description=request.form.get('description'),
                location=request.form.get('location'),
                salary_min=request.form.get('salary_min', type=float),
                salary_max=request.form.get('salary_max', type=float),
                experience_required=request.form.get('experience_required', 0, type=int),
                job_type=request.form.get('job_type'),
                status='active'
            )
            db.session.add(job)
            db.session.commit()
            flash('Job posted successfully!', 'success')
            return redirect(url_for('hospital.my_jobs'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error posting job: {str(e)}', 'danger')
            return redirect(url_for('hospital.post_job'))
    
    return render_template('post_job.html')


@hospital_bp.route('/my-jobs')
@role_required('hospital')
def my_jobs():
    """View hospital's job postings"""
    hospital = Hospital.query.filter_by(user_id=session['user_id']).first()
    
    if not hospital:
        flash('Hospital profile not found', 'danger')
        return redirect(url_for('auth.login'))
    
    page = request.args.get('page', 1, type=int)
    jobs = Job.query.filter_by(hospital_id=hospital.id).order_by(
        Job.created_at.desc()
    ).paginate(page=page, per_page=10)
    
    return render_template('my_jobs.html', jobs=jobs)


@hospital_bp.route('/job/<int:job_id>/applicants')
@role_required('hospital')
def applicants(job_id):
    """View applicants for a job"""
    job = Job.query.get_or_404(job_id)
    
    # Verify hospital owns this job
    if job.hospital_id != Hospital.query.filter_by(user_id=session['user_id']).first().id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('hospital.my_jobs'))
    
    page = request.args.get('page', 1, type=int)
    applications = JobApplication.query.filter_by(job_id=job_id).order_by(
        JobApplication.applied_at.desc()
    ).paginate(page=page, per_page=10)
    
    return render_template('applicants.html', job=job, applications=applications)


@hospital_bp.route('/application/<int:app_id>/review', methods=['POST'])
@role_required('hospital')
def review_application(app_id):
    """Review job application"""
    application = JobApplication.query.get_or_404(app_id)
    status = request.form.get('status')  # 'reviewed', 'accepted', 'rejected'
    
    # Verify hospital owns the job
    if application.job.hospital_id != Hospital.query.filter_by(user_id=session['user_id']).first().id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('hospital.my_jobs'))
    
    if status not in ['reviewed', 'accepted', 'rejected']:
        flash('Invalid status', 'danger')
        return redirect(url_for('hospital.applicants', job_id=application.job_id))
    
    try:
        application.status = status
        application.reviewed_at = db.func.now()
        db.session.commit()
        flash(f'Application marked as {status}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating application: {str(e)}', 'danger')
    
    return redirect(url_for('hospital.applicants', job_id=application.job_id))


@hospital_bp.route('/profile', methods=['GET', 'POST'])
@role_required('hospital')
def profile():
    """View and edit hospital profile"""
    hospital = Hospital.query.filter_by(user_id=session['user_id']).first()
    
    if not hospital:
        flash('Hospital profile not found', 'danger')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        try:
            hospital.hospital_name = request.form.get('hospital_name', hospital.hospital_name)
            hospital.phone = request.form.get('phone', hospital.phone)
            hospital.address = request.form.get('address', hospital.address)
            hospital.city = request.form.get('city', hospital.city)
            hospital.state = request.form.get('state', hospital.state)
            hospital.website = request.form.get('website', hospital.website)
            hospital.description = request.form.get('description', hospital.description)
            
            db.session.commit()
            flash('Profile updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {str(e)}', 'danger')
        
        return redirect(url_for('hospital.profile'))
    
    return render_template('profile.html', hospital=hospital)
