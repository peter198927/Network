"""
Application entry point for MediConnect
"""
import os
from app import create_app
from app.models import db, User, Doctor, Hospital, Job, JobApplication

# Create Flask app
app = create_app(config_name=os.environ.get('FLASK_ENV', 'development'))


@app.shell_context_processor
def make_shell_context():
    """Register shell context for Flask CLI"""
    return {
        'db': db,
        'User': User,
        'Doctor': Doctor,
        'Hospital': Hospital,
        'Job': Job,
        'JobApplication': JobApplication
    }


@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return '''
    <div style="text-align: center; padding: 50px; font-family: Arial;">
        <h1>404 - Page Not Found</h1>
        <p>The page you're looking for doesn't exist.</p>
        <a href="/">Back to Home</a>
    </div>
    ''', 404


@app.errorhandler(403)
def forbidden_error(error):
    """Handle 403 errors"""
    return '''
    <div style="text-align: center; padding: 50px; font-family: Arial;">
        <h1>403 - Access Forbidden</h1>
        <p>You don't have permission to access this resource.</p>
        <a href="/">Back to Home</a>
    </div>
    ''', 403


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    db.session.rollback()
    return '''
    <div style="text-align: center; padding: 50px; font-family: Arial;">
        <h1>500 - Internal Server Error</h1>
        <p>Something went wrong on our end. Please try again later.</p>
        <a href="/">Back to Home</a>
    </div>
    ''', 500


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=os.environ.get('FLASK_ENV') == 'development'
    )
