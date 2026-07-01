import os
import re
import logging
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from email_validator import validate_email, EmailNotValidError
from model import db, Admin

logger = logging.getLogger(__name__)

login_bp = Blueprint('login', __name__)

# ==================== DECORATORS & SERVICES ====================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session or not session.get('admin_id'):
            flash('Anda harus login terlebih dahulu.', 'warning')
            return redirect(url_for('login.login'))
        return f(*args, **kwargs)
    return decorated_function

class AuthenticationService:
    @staticmethod
    def log_action(admin_id, action, details=None):
        try:
            logger.info(f"Admin {admin_id} performed action: {action}. Details: {details}")
        except Exception as e:
            logger.error(f"Failed to log action: {e}")

class FileSecurityService:
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

    @staticmethod
    def allowed_file(filename):
        if not filename or '.' not in filename:
            return False
        ext = filename.rsplit('.', 1)[1].lower()
        return ext in FileSecurityService.ALLOWED_EXTENSIONS

    @staticmethod
    def validate_file_size(file_stream, max_size=None):
        if max_size is None:
            max_size = FileSecurityService.MAX_FILE_SIZE
        
        file_stream.seek(0, os.SEEK_END)
        file_size = file_stream.tell()
        file_stream.seek(0)
        
        if file_size > max_size:
            return False, f"File terlalu besar. Maksimal {max_size / 1024 / 1024}MB"
        if file_size == 0:
            return False, "File kosong"
        
        return True, None

class FormValidator:
    @staticmethod
    def validate_email(email):
        try:
            validate_email(email, check_deliverability=False)
            return True, None
        except EmailNotValidError as e:
            return False, str(e)

    @staticmethod
    def validate_required(value, field_name):
        if not value or not str(value).strip():
            return False, f"{field_name} harus diisi"
        return True, None

    @staticmethod
    def sanitize_text(text):
        if not text:
            return ""
        return str(text).strip()

# ==================== ROUTES ====================

@login_bp.route('/admin/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Username dan password harus diisi.', 'danger')
            return redirect(url_for('login.login'))

        try:
            admin = Admin.query.filter_by(username=username).first()
            if admin and admin.check_password(password):
                session.permanent = True
                session['admin_id'] = admin.id
                session['admin_username'] = admin.username
                AuthenticationService.log_action(admin.id, 'LOGIN', None)
                flash(f'Selamat datang, {admin.username}!', 'success')
                return redirect(url_for('dashboard.dashboard'))
            else:
                flash('Username atau password salah.', 'danger')
                logger.warning(f'Failed login attempt for username: {username}')
        except Exception as e:
            flash(f'Terjadi kesalahan: {str(e)}', 'danger')
            logger.error(f'Login error: {str(e)}')

    return render_template('admin/login.html')

@login_bp.route('/admin/logout', methods=['GET', 'POST'])
@login_required
def logout():
    admin_id = session.get('admin_id')
    admin_username = session.get('admin_username', 'Unknown')
    
    AuthenticationService.log_action(admin_id, 'LOGOUT', None)
    session.clear()
    
    flash(f'Anda telah logout. Sampai jumpa, {admin_username}!', 'info')
    return redirect(url_for('login.login'))
