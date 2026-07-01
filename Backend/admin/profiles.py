import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from model import db, Profile
from Backend.admin.login import login_required, FormValidator, FileSecurityService, AuthenticationService
from Backend.admin.upload import CloudinaryService

logger = logging.getLogger(__name__)

profiles_bp = Blueprint('profiles', __name__)

@profiles_bp.route('/admin/profile', methods=['GET', 'POST'])
@login_required
def profile():
    profile = Profile.query.order_by(Profile.id.desc()).first()

    if request.method == 'POST':
        full_name = FormValidator.sanitize_text(request.form.get('full_name', ''))
        profession = FormValidator.sanitize_text(request.form.get('profession', ''))
        about = FormValidator.sanitize_text(request.form.get('about', ''))
        email = FormValidator.sanitize_text(request.form.get('email', ''))
        phone = FormValidator.sanitize_text(request.form.get('phone', ''))
        linkedin = FormValidator.sanitize_text(request.form.get('linkedin', ''))
        github = FormValidator.sanitize_text(request.form.get('github', ''))
        instagram = FormValidator.sanitize_text(request.form.get('instagram', ''))
        location = FormValidator.sanitize_text(request.form.get('location', ''))
        university = FormValidator.sanitize_text(request.form.get('university', ''))
        favorite_language = FormValidator.sanitize_text(request.form.get('favorite_language', ''))
        photo_file = request.files.get('photo')

        # Validation
        errors = []
        is_valid, error = FormValidator.validate_required(full_name, 'Nama lengkap')
        if not is_valid:
            errors.append(error)
            
        is_valid, error = FormValidator.validate_required(profession, 'Profesi')
        if not is_valid:
            errors.append(error)
            
        is_valid, error = FormValidator.validate_required(about, 'About')
        if not is_valid:
            errors.append(error)
            
        is_valid, error = FormValidator.validate_email(email)
        if not is_valid:
            errors.append(error)

        if errors:
            for error in errors:
                flash(error, 'danger')
            return redirect(url_for('profiles.profile'))

        # Handle photo upload
        image_url = profile.photo_url if profile else None
        if photo_file and photo_file.filename:
            if not FileSecurityService.allowed_file(photo_file.filename):
                flash('Format gambar tidak didukung. Gunakan PNG, JPG, JPEG, GIF, atau WEBP.', 'danger')
                return redirect(url_for('profiles.profile'))

            is_valid, error = FileSecurityService.validate_file_size(photo_file.stream)
            if not is_valid:
                flash(f'Error upload: {error}', 'danger')
                return redirect(url_for('profiles.profile'))

            try:
                cloudinary_service = CloudinaryService()
                # Delete old photo if it exists to avoid orphans
                if profile and profile.photo_url:
                    cloudinary_service.delete_image(profile.photo_url)
                
                filename = secure_filename(photo_file.filename)
                image_url = cloudinary_service.upload_image(photo_file, filename, folder='portfolio/profile')
            except Exception as e:
                flash(f'Upload foto gagal: {str(e)}', 'danger')
                logger.error(f'Profile photo upload error: {str(e)}')
                return redirect(url_for('profiles.profile'))

        # Save to database
        try:
            if profile:
                profile.full_name = full_name
                profile.profession = profession
                profile.about = about
                profile.photo_url = image_url
                profile.email = email
                profile.phone = phone
                profile.linkedin = linkedin
                profile.github = github
                profile.instagram = instagram
                profile.location = location
                profile.university = university
                profile.favorite_language = favorite_language
            else:
                profile = Profile(
                    full_name=full_name,
                    profession=profession,
                    about=about,
                    photo_url=image_url,
                    email=email,
                    phone=phone,
                    linkedin=linkedin,
                    github=github,
                    instagram=instagram,
                    location=location,
                    university=university,
                    favorite_language=favorite_language,
                )
                db.session.add(profile)

            db.session.commit()
            flash('Profil berhasil disimpan.', 'success')
            AuthenticationService.log_action(session.get('admin_id'), 'UPDATE_PROFILE', full_name)
            return redirect(url_for('profiles.profile'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error menyimpan profil: {str(e)}', 'danger')
            logger.error(f'Profile save error: {str(e)}')

    return render_template('admin/profiles.html', profile=profile)
