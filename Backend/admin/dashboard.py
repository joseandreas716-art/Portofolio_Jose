import logging
from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from model import db, Profile, Skill, Experience, Project, Contact
from Backend.admin.login import login_required, AuthenticationService

logger = logging.getLogger(__name__)

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/admin', methods=['GET'])
@dashboard_bp.route('/admin/dashboard', methods=['GET'])
@login_required
def dashboard():
    try:
        profile_count = Profile.query.count()
        skill_count = Skill.query.count()
        experience_count = Experience.query.count()
        project_count = Project.query.count()
        contact_count = Contact.query.count()
        
        # Recent contacts
        recent_contacts = Contact.query.order_by(Contact.created_at.desc()).limit(10).all()
        
        return render_template(
            'admin/dashboard.html',
            profile_count=profile_count,
            skill_count=skill_count,
            experience_count=experience_count,
            project_count=project_count,
            contact_count=contact_count,
            recent_contacts=recent_contacts,
        )
    except Exception as e:
        flash(f'Gagal memuat dashboard: {str(e)}', 'danger')
        logger.error(f'Dashboard error: {str(e)}')
        return redirect(url_for('login.login'))

@dashboard_bp.route('/admin/contacts/<int:contact_id>/delete', methods=['POST'])
@login_required
def delete_contact(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    sender_info = f'{contact.sender_name} ({contact.sender_email})'

    try:
        db.session.delete(contact)
        db.session.commit()
        flash('Pesan berhasil dihapus.', 'success')
        AuthenticationService.log_action(session.get('admin_id'), 'DELETE_CONTACT', sender_info)
    except Exception as e:
        db.session.rollback()
        flash(f'Error menghapus pesan: {str(e)}', 'danger')
        logger.error(f'Delete contact error: {str(e)}')

    return redirect(url_for('dashboard.dashboard'))
