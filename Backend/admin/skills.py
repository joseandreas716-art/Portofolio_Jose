import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from model import db, Skill
from Backend.admin.login import login_required, FormValidator, AuthenticationService

logger = logging.getLogger(__name__)

skills_bp = Blueprint('skills', __name__)

@skills_bp.route('/admin/skills', methods=['GET', 'POST'])
@login_required
def skills():
    if request.method == 'POST':
        action = request.form.get('action', 'add')
        
        if action == 'add':
            skill_name = FormValidator.sanitize_text(request.form.get('skill_name', ''))
            level = FormValidator.sanitize_text(request.form.get('level', ''))

            errors = []
            is_valid, error = FormValidator.validate_required(skill_name, 'Skill name')
            if not is_valid:
                errors.append(error)
                
            is_valid, error = FormValidator.validate_required(level, 'Level')
            if not is_valid:
                errors.append(error)

            if errors:
                for error in errors:
                    flash(error, 'danger')
                return redirect(url_for('skills.skills'))

            try:
                skill = Skill(skill_name=skill_name, level=level)
                db.session.add(skill)
                db.session.commit()
                flash('Skill berhasil ditambahkan.', 'success')
                AuthenticationService.log_action(session.get('admin_id'), 'CREATE_SKILL', skill_name)
            except Exception as e:
                db.session.rollback()
                flash(f'Error menambah skill: {str(e)}', 'danger')
                logger.error(f'Add skill error: {str(e)}')

    skills_list = Skill.query.order_by(Skill.id.asc()).all()
    return render_template('admin/skills.html', skills=skills_list)

@skills_bp.route('/admin/skills/<int:skill_id>/edit', methods=['POST'])
@login_required
def edit_skill(skill_id):
    skill = Skill.query.get_or_404(skill_id)
    
    skill_name = FormValidator.sanitize_text(request.form.get('skill_name', ''))
    level = FormValidator.sanitize_text(request.form.get('level', ''))

    errors = []
    is_valid, error = FormValidator.validate_required(skill_name, 'Skill name')
    if not is_valid:
        errors.append(error)
        
    is_valid, error = FormValidator.validate_required(level, 'Level')
    if not is_valid:
        errors.append(error)

    if errors:
        for error in errors:
            flash(error, 'danger')
        return redirect(url_for('skills.skills'))

    try:
        skill.skill_name = skill_name
        skill.level = level
        db.session.commit()
        flash('Skill berhasil diupdate.', 'success')
        AuthenticationService.log_action(session.get('admin_id'), 'UPDATE_SKILL', skill_name)
    except Exception as e:
        db.session.rollback()
        flash(f'Error mengupdate skill: {str(e)}', 'danger')
        logger.error(f'Edit skill error: {str(e)}')

    return redirect(url_for('skills.skills'))

@skills_bp.route('/admin/skills/<int:skill_id>/delete', methods=['POST'])
@login_required
def delete_skill(skill_id):
    skill = Skill.query.get_or_404(skill_id)
    skill_name = skill.skill_name

    try:
        db.session.delete(skill)
        db.session.commit()
        flash('Skill berhasil dihapus.', 'success')
        AuthenticationService.log_action(session.get('admin_id'), 'DELETE_SKILL', skill_name)
    except Exception as e:
        db.session.rollback()
        flash(f'Error menghapus skill: {str(e)}', 'danger')
        logger.error(f'Delete skill error: {str(e)}')

    return redirect(url_for('skills.skills'))
