import os
from dotenv import load_dotenv
load_dotenv()
from datetime import timedelta
from flask import Flask, render_template, session
from jinja2 import ChoiceLoader, FileSystemLoader
from config import Config
from model import db, Admin

def create_app():
    # Configure Flask app to use Frontend as static files folder
    app = Flask(
        __name__, 
        instance_relative_config=True,
        static_folder='Frontend',
        static_url_path='/Frontend'
    )
    app.config.from_object(Config)
    
    # Secret key for sessions
    app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    
    # Session configuration
    app.permanent_session_lifetime = timedelta(minutes=30)
    app.config['SESSION_REFRESH_EACH_REQUEST'] = True
    
    # Configure Jinja ChoiceLoader to load templates from both Frontend/ and root (for index.html)
    app.jinja_loader = ChoiceLoader([
        FileSystemLoader('Frontend'),
        FileSystemLoader('.')
    ])
    
    db.init_app(app)

    # Register blueprints from Backend packages
    from Backend.utama.utama import utama_bp
    from Backend.admin.login import login_bp
    from Backend.admin.dashboard import dashboard_bp
    from Backend.admin.profiles import profiles_bp
    from Backend.admin.skills import skills_bp
    from Backend.admin.experience import experience_bp
    from Backend.admin.projects import projects_bp

    app.register_blueprint(utama_bp)
    app.register_blueprint(login_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(profiles_bp)
    app.register_blueprint(skills_bp)
    app.register_blueprint(experience_bp)
    app.register_blueprint(projects_bp)

    @app.before_request
    def make_session_permanent():
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=30)

    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('500.html', error=error), 500

    return app


app = create_app()

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            print('Database tables verified/created successfully')
            
            # Seed default admin if table is empty
            admin_check = Admin.query.filter_by(username='admin').first()
            if not admin_check:
                # pyrefly: ignore [unexpected-keyword]
                default_admin = Admin(username='admin')
                default_admin.set_password('admin123')
                db.session.add(default_admin)
                db.session.commit()
                print('Default admin user (admin / admin123) successfully seeded!')
        except Exception as error:
            print(f'Warning: Could not configure database: {error}')
            print('App will continue running, but database features may not work')

    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=int(os.getenv('PORT', 5001)))


