@hospital_bp.route('/job/<int:job_id>/applicants')
@login_required
@role_required('hospital')
def view_applicants(job_id):
    job = JobListing.query.get_or_404(job_id)
    # Ensure this hospital owns the job
    if job.employer.user_id != current_user.id:
        abort(403)
        
    # Get applicants via relationship
    return render_template('hospital/applicants_list.html', job=job)

@hospital_bp.route('/application/<int:job_id>/<int:doc_id>/update', methods=['POST'])
@login_required
@role_required('hospital')
def update_status(job_id, doc_id):
    new_status = request.form.get('status')
    db.session.execute(
        applications.update().where(
            (applications.c.job_id == job_id) & (applications.c.doctor_id == doc_id)
        ).values(status=new_status)
    )
    db.session.commit()
    flash("Candidate status updated.", "success")
    return redirect(url_for('hospital.view_applicants', job_id=job_id))