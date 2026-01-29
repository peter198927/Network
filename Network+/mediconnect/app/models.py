from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    """Base User model with common attributes"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'doctor', 'hospital', 'admin'
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Polymorphic relationships
    doctor = db.relationship('Doctor', uselist=False, back_populates='user')
    hospital = db.relationship('Hospital', uselist=False, back_populates='user')
    
    __mapper_args__ = {
        'polymorphic_on': role,
        'polymorphic_identity': 'user'
    }
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)


class Doctor(db.Model):
    """Doctor profile extending User"""
    __tablename__ = 'doctors'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    full_name = db.Column(db.String(120), nullable=False)
    specialization = db.Column(db.String(120), nullable=False)
    experience_years = db.Column(db.Integer, default=0)
    phone = db.Column(db.String(20))
    location = db.Column(db.String(200))
    resume_url = db.Column(db.String(255))
    bio = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='doctor')
    applications = db.relationship('JobApplication', back_populates='doctor', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Doctor {self.full_name}>'


class Hospital(db.Model):
    """Hospital profile extending User"""
    __tablename__ = 'hospitals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    hospital_name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(300))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    website = db.Column(db.String(255))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='hospital')
    jobs = db.relationship('Job', back_populates='hospital', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Hospital {self.hospital_name}>'


class Job(db.Model):
    """Job posting by hospitals"""
    __tablename__ = 'jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    specialization = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200))
    salary_min = db.Column(db.Float)
    salary_max = db.Column(db.Float)
    experience_required = db.Column(db.Integer, default=0)
    job_type = db.Column(db.String(50))  # 'full-time', 'part-time', 'contract'
    status = db.Column(db.String(20), default='active')  # 'active', 'closed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    hospital = db.relationship('Hospital', back_populates='jobs')
    applications = db.relationship('JobApplication', back_populates='job', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Job {self.title} at {self.hospital.hospital_name}>'


class JobApplication(db.Model):
    """Job application by doctors"""
    __tablename__ = 'job_applications'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'reviewed', 'accepted', 'rejected'
    cover_letter = db.Column(db.Text)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime)
    
    # Relationships
    job = db.relationship('Job', back_populates='applications')
    doctor = db.relationship('Doctor', back_populates='applications')
    
    __table_args__ = (db.UniqueConstraint('job_id', 'doctor_id', name='unique_job_doctor_application'),)
    
    def __repr__(self):
        return f'<JobApplication Doctor:{self.doctor_id} Job:{self.job_id}>'