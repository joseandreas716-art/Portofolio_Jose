import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    
    # CSRF & Session Protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'false').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes
    
    # Database Configuration (TiDB with SSL or local SQLite fallback)
    use_tidb = os.getenv('USE_TIDB', 'false').lower() == 'true'
    
    db_user = os.getenv('TIDB_USER')
    db_password = os.getenv('TIDB_PASSWORD')
    db_host = os.getenv('TIDB_HOST')
    db_port = os.getenv('TIDB_PORT', '4000')
    db_database = os.getenv('TIDB_DATABASE')
    
    ca_path = os.getenv('CA_PATH')
    if not ca_path or not os.path.exists(ca_path):
        local_ca = os.path.join(BASE_DIR, 'Ca.pem')
        if os.path.exists(local_ca):
            ca_path = local_ca
    
    if use_tidb and db_user and db_password and db_host:
        if ca_path and os.path.exists(ca_path):
            # Using raw path to handle Windows backslashes in SQLAlchemy connection URL query parameters
            # pymysql supports ssl_ca parameter via query arguments
            SQLALCHEMY_DATABASE_URI = (
                f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_database}"
                f"?ssl_verify_cert=true&ssl_verify_identity=true&ssl_ca={ca_path}"
            )
        else:
            SQLALCHEMY_DATABASE_URI = (
                f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_database}"
            )
    else:
        db_path = os.path.join(BASE_DIR, 'instance', 'portfolio.db')
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Cloudinary configuration
    CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')
    
    # Resend configuration
    RESEND_API_KEY = os.getenv('RESEND_API_KEY')
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')
