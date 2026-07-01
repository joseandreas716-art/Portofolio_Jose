import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from model import db, Experience
from Backend.admin.login import login_required, FormValidator, AuthenticationService

logger = logging.getLogger(__name__)

experience_bp = Blueprint('experience', __name__)

@experience_bp.route('/admin/experience', methods=['GET', 'POST'])
@login_required
def experience():
    if request.method == 'POST':
        action = request.form.get('action', 'add')
        
        if action == 'add':
            company_name = FormValidator.sanitize_text(request.form.get('company_name', ''))
            position = FormValidator.sanitize_text(request.form.get('position', ''))
            start_date = FormValidator.sanitize_text(request.form.get('start_date', ''))
            end_date = FormValidator.sanitize_text(request.form.get('end_date', ''))
            description = FormValidator.sanitize_text(request.form.get('description', ''))

            errors = []
            is_valid, error = FormValidator.validate_required(company_name, 'Company name')
            if not is_valid:
                errors.append(error)
                
            is_valid, error = FormValidator.validate_required(position, 'Position')
            if not is_valid:
                errors.append(error)
                
            is_valid, error = FormValidator.validate_required(start_date, 'Start date')
            if not is_valid:
                errors.append(error)
                
            is_valid, error = FormValidator.validate_required(description, 'Description')
            if not is_valid:
                errors.append(error)

            if errors:
                for error in errors:
                    flash(error, 'danger')
                return redirect(url_for('experience.experience'))

            try:
                exp = Experience(
                    company_name=company_name,
                    position=position,
                    start_date=start_date,
                    end_date=end_date,
                    description=description,
                )
                db.session.add(exp)
                db.session.commit()
                flash('Experience berhasil ditambahkan.', 'success')
                AuthenticationService.log_action(session.get('admin_id'), 'CREATE_EXPERIENCE', f'{position} at {company_name}')
            except Exception as e:
                db.session.rollback()
                flash(f'Error menambah experience: {str(e)}', 'danger')
                logger.error(f'Add experience error: {str(e)}')

    experiences = Experience.query.order_by(Experience.id.desc()).all()
    return render_template('admin/experience.html', experiences=experiences)

@experience_bp.route('/admin/experience/<int:experience_id>/edit', methods=['POST'])
@login_required
def edit_experience(experience_id):
    exp = Experience.query.get_or_404(experience_id)

    company_name = FormValidator.sanitize_text(request.form.get('company_name', ''))
    position = FormValidator.sanitize_text(request.form.get('position', ''))
    start_date = FormValidator.sanitize_text(request.form.get('start_date', ''))
    end_date = FormValidator.sanitize_text(request.form.get('end_date', ''))
    description = FormValidator.sanitize_text(request.form.get('description', ''))

    errors = []
    is_valid, error = FormValidator.validate_required(company_name, 'Company name')
    if not is_valid:
        errors.append(error)
        
    is_valid, error = FormValidator.validate_required(position, 'Position')
    if not is_valid:
        errors.append(error)
        
    is_valid, error = FormValidator.validate_required(start_date, 'Start date')
    if not is_valid:
        errors.append(error)
        
    is_valid, error = FormValidator.validate_required(description, 'Description')
    if not is_valid:
        errors.append(error)

    if errors:
        for error in errors:
            flash(error, 'danger')
        return redirect(url_for('experience.experience'))

    try:
        exp.company_name = company_name
        exp.position = position
        exp.start_date = start_date
        exp.end_date = end_date
        exp.description = description
        db.session.commit()
        flash('Experience berhasil diupdate.', 'success')
        AuthenticationService.log_action(session.get('admin_id'), 'UPDATE_EXPERIENCE', f'{position} at {company_name}')
    except Exception as e:
        db.session.rollback()
        flash(f'Error mengupdate experience: {str(e)}', 'danger')
        logger.error(f'Edit experience error: {str(e)}')

    return redirect(url_for('experience.experience'))

@experience_bp.route('/admin/experience/<int:experience_id>/delete', methods=['POST'])
@login_required
def delete_experience(experience_id):
    exp = Experience.query.get_or_404(experience_id)
    company_position = f'{exp.position} at {exp.company_name}'

    try:
        db.session.delete(exp)
        db.session.commit()
        flash('Experience berhasil dihapus.', 'success')
        AuthenticationService.log_action(session.get('admin_id'), 'DELETE_EXPERIENCE', company_position)
    except Exception as e:
        db.session.rollback()
        flash(f'Error menghapus experience: {str(e)}', 'danger')
        logger.error(f'Delete experience error: {str(e)}')

    return redirect(url_for('experience.experience'))
