# MediConnect - Medical Job Portal

A comprehensive Flask-based job portal connecting healthcare professionals (doctors) with medical institutions (hospitals).

## Features

### For Doctors
- Browse available medical job positions
- Filter jobs by specialization, location, and keywords
- Apply for jobs with cover letters
- Track application status
- Manage professional profile

### For Hospitals
- Post job openings
- Manage job postings (activate/deactivate)
- Review doctor applications
- Track applicant status (pending, reviewed, accepted, rejected)
- Manage hospital profile

### For Administrators
- User management and verification
- Job posting oversight
- Application tracking and reporting
- System statistics and analytics
- User account deactivation

## Project Structure

```
mediconnect/
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── models.py             # Database models
│   ├── decorators.py         # RBAC decorators
│   ├── auth/
│   │   └── routes.py         # Authentication routes
│   ├── doctor/
│   │   └── routes.py         # Doctor-specific routes
│   ├── hospital/
│   │   └── routes.py         # Hospital-specific routes
│   ├── admin/
│   │   └── routes.py         # Admin routes
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   └── uploads/          # Resume uploads directory
│   └── templates/
│       ├── base.html
│       ├── auth/
│       ├── doctor/
│       ├── hospital/
│       └── admin/
├── config.py                 # Configuration management
├── requirements.txt          # Python dependencies
├── render.yaml              # Deployment configuration
└── run.py                   # Application entry point
```

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Initialize the database:
   ```bash
   python run.py
   ```

## Running the Application

```bash
python run.py
```

The application will start at `http://localhost:5000`

## Default Credentials

Create an admin account through the registration page with:
- Role: Admin
- Verify through the admin panel

## Database Models

### User
- Base user model with authentication
- Roles: doctor, hospital, admin

### Doctor
- Doctor profile with specialization
- Links to job applications
- Resume management

### Hospital
- Hospital profile with details
- Links to posted jobs
- Applicant management

### Job
- Job posting details
- Links to hospital and applications
- Status tracking (active/closed)

### JobApplication
- Tracks doctor applications to jobs
- Status: pending, reviewed, accepted, rejected
- Includes cover letter

## Environment Variables

For production deployment:
- `FLASK_ENV`: Set to 'production'
- `SECRET_KEY`: Flask secret key
- `DATABASE_URL`: Database connection string
- `PORT`: Server port (default: 5000)

## Deployment

The application is configured for Render deployment using `render.yaml`. 
It includes automatic database setup and environment variable management.

## Technologies Used

- **Framework**: Flask
- **Database**: SQLAlchemy (supports SQLite, PostgreSQL)
- **Authentication**: Werkzeug (password hashing)
- **Deployment**: Render.com

## Security Features

- Password hashing with Werkzeug
- Session-based authentication
- Role-based access control (RBAC)
- CSRF protection ready
- Secure cookie settings
- Input validation

## Future Enhancements

- Email notifications
- Resume file uploads
- Interview scheduling
- Advanced search and filtering
- Job recommendations
- Performance analytics
- Two-factor authentication
- API endpoints
