import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from model import db, Project
from Backend.admin.login import login_required, FormValidator, FileSecurityService, AuthenticationService
from Backend.admin.upload import CloudinaryService

logger = logging.getLogger(__name__)

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/admin/projects', methods=['GET', 'POST'])
@login_required
def projects():
    if request.method == 'POST':
        action = request.form.get('action', 'add')
        
        if action == 'add':
            title = FormValidator.sanitize_text(request.form.get('title', ''))
            description = FormValidator.sanitize_text(request.form.get('description', ''))
            github_link = FormValidator.sanitize_text(request.form.get('github_link', ''))
            live_demo_link = FormValidator.sanitize_text(request.form.get('live_demo_link', ''))
            image_file = request.files.get('image')

            errors = []
            is_valid, error = FormValidator.validate_required(title, 'Title')
            if not is_valid:
                errors.append(error)
                
            is_valid, error = FormValidator.validate_required(description, 'Description')
            if not is_valid:
                errors.append(error)

            if errors:
                for error in errors:
                    flash(error, 'danger')
                return redirect(url_for('projects.projects'))

            image_url = None
            if image_file and image_file.filename:
                if not FileSecurityService.allowed_file(image_file.filename):
                    flash('Format gambar tidak didukung. Gunakan PNG, JPG, JPEG, GIF, atau WEBP.', 'danger')
                    return redirect(url_for('projects.projects'))

                is_valid, error = FileSecurityService.validate_file_size(image_file.stream)
                if not is_valid:
                    flash(f'Error upload: {error}', 'danger')
                    return redirect(url_for('projects.projects'))

                try:
                    cloudinary_service = CloudinaryService()
                    filename = secure_filename(image_file.filename)
                    image_url = cloudinary_service.upload_image(image_file, filename, folder='portfolio/projects')
                except Exception as e:
                    flash(f'Upload gambar gagal: {str(e)}', 'danger')
                    logger.error(f'Project image upload error: {str(e)}')
                    return redirect(url_for('projects.projects'))

            try:
                project = Project(
                    title=title,
                    description=description,
                    image_url=image_url,
                    github_link=github_link,
                    live_demo_link=live_demo_link,
                )
                db.session.add(project)
                db.session.commit()
                flash('Project berhasil ditambahkan.', 'success')
                AuthenticationService.log_action(session.get('admin_id'), 'CREATE_PROJECT', title)
            except Exception as e:
                db.session.rollback()
                flash(f'Error menambah project: {str(e)}', 'danger')
                logger.error(f'Add project error: {str(e)}')

    projects_list = Project.query.order_by(Project.created_at.desc()).all()
    return render_template('admin/projects.html', projects=projects_list)

@projects_bp.route('/admin/projects/<int:project_id>/edit', methods=['POST'])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)

    title = FormValidator.sanitize_text(request.form.get('title', ''))
    description = FormValidator.sanitize_text(request.form.get('description', ''))
    github_link = FormValidator.sanitize_text(request.form.get('github_link', ''))
    live_demo_link = FormValidator.sanitize_text(request.form.get('live_demo_link', ''))
    image_file = request.files.get('image')

    errors = []
    is_valid, error = FormValidator.validate_required(title, 'Title')
    if not is_valid:
        errors.append(error)
        
    is_valid, error = FormValidator.validate_required(description, 'Description')
    if not is_valid:
        errors.append(error)

    if errors:
        for error in errors:
            flash(error, 'danger')
        return redirect(url_for('projects.projects'))

    image_url = project.image_url
    if image_file and image_file.filename:
        if not FileSecurityService.allowed_file(image_file.filename):
            flash('Format gambar tidak didukung. Gunakan PNG, JPG, JPEG, GIF, atau WEBP.', 'danger')
            return redirect(url_for('projects.projects'))

        is_valid, error = FileSecurityService.validate_file_size(image_file.stream)
        if not is_valid:
            flash(f'Error upload: {error}', 'danger')
            return redirect(url_for('projects.projects'))

        try:
            cloudinary_service = CloudinaryService()
            if project.image_url:
                cloudinary_service.delete_image(project.image_url)
                
            filename = secure_filename(image_file.filename)
            image_url = cloudinary_service.upload_image(image_file, filename, folder='portfolio/projects')
        except Exception as e:
            flash(f'Upload gambar gagal: {str(e)}', 'danger')
            logger.error(f'Project image upload error: {str(e)}')
            return redirect(url_for('projects.projects'))

    try:
        project.title = title
        project.description = description
        project.image_url = image_url
        project.github_link = github_link
        project.live_demo_link = live_demo_link
        db.session.commit()
        flash('Project berhasil diupdate.', 'success')
        AuthenticationService.log_action(session.get('admin_id'), 'UPDATE_PROJECT', title)
    except Exception as e:
        db.session.rollback()
        flash(f'Error mengupdate project: {str(e)}', 'danger')
        logger.error(f'Edit project error: {str(e)}')

    return redirect(url_for('projects.projects'))

@projects_bp.route('/admin/projects/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    project_title = project.title

    try:
        if project.image_url:
            cloudinary_service = CloudinaryService()
            cloudinary_service.delete_image(project.image_url)

        db.session.delete(project)
        db.session.commit()
        flash('Project berhasil dihapus.', 'success')
        AuthenticationService.log_action(session.get('admin_id'), 'DELETE_PROJECT', project_title)
    except Exception as e:
        db.session.rollback()
        flash(f'Error menghapus project: {str(e)}', 'danger')
        logger.error(f'Delete project error: {str(e)}')

    return redirect(url_for('projects.projects'))
