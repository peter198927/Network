from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from app.models import db


def create_app(config_name='development'):
    """Application factory function"""
    app = Flask(__name__, template_folder='templates', static_folder='static')
    
    # Load configuration
    if config_name == 'production':
        from config import ProductionConfig
        app.config.from_object(ProductionConfig)
    else:
        from config import DevelopmentConfig
        app.config.from_object(DevelopmentConfig)
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # Create tables within app context
    with app.app_context():
        db.create_all()
    
    # Register blueprints
    from app.auth.routes import auth_bp
    from app.doctor.routes import doctor_bp
    from app.hospital.routes import hospital_bp
    from app.admin.routes import admin_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(hospital_bp)
    app.register_blueprint(admin_bp)
    
    # Home route
    @app.route('/')
    def index():
        return '''
        <h1>Welcome to MediConnect</h1>
        <p>A platform connecting doctors with healthcare opportunities</p>
        <ul>
            <li><a href="/auth/register">Register</a></li>
            <li><a href="/auth/login">Login</a></li>
        </ul>
        '''
    
    return app
