import os
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash
import resend
from model import db, Profile, Skill, Experience, Project, Contact

logger = logging.getLogger(__name__)

utama_bp = Blueprint('utama', __name__)

@utama_bp.route('/')
def home():
    profile = Profile.query.order_by(Profile.id.desc()).first()
    skills = Skill.query.order_by(Skill.id.asc()).all()
    experiences = Experience.query.order_by(Experience.id.desc()).all()
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template(
        'index.html',
        profile=profile,
        skills=skills,
        experiences=experiences,
        projects=projects,
    )

@utama_bp.route('/contact', methods=['POST'])
def contact():
    sender_name = request.form.get('name', '').strip()
    sender_email = request.form.get('email', '').strip()
    subject = request.form.get('subject', '').strip() or 'Pesan Kontak Portofolio'
    message = request.form.get('message', '').strip()

    if not sender_name or not sender_email or not message:
        flash('Semua field harus diisi.', 'danger')
        return redirect(url_for('utama.home'))

    if '@' not in sender_email or '.' not in sender_email:
        flash('Format email tidak valid.', 'danger')
        return redirect(url_for('utama.home'))

    try:
        contact_entry = Contact(
            sender_name=sender_name,
            sender_email=sender_email,
            subject=subject,
            message=message,
        )
        db.session.add(contact_entry)
        db.session.commit()

        # Resend Email Integration
        resend_api_key = os.getenv('RESEND_API_KEY')
        admin_email = os.getenv('ADMIN_EMAIL')

        if resend_api_key and admin_email:
            try:
                resend.api_key = resend_api_key
                
                email_body = (
                    f"<h1>Pesan Baru dari Portofolio</h1>"
                    f"<p><strong>Nama:</strong> {sender_name}</p>"
                    f"<p><strong>Email:</strong> {sender_email}</p>"
                    f"<p><strong>Subjek:</strong> {subject}</p>"
                    f"<p><strong>Pesan:</strong><br>{message}</p>"
                )
                
                # Send email using Resend
                # Using 'onboarding@resend.dev' for sandbox accounts
                resend.Emails.send({
                    "from": "onboarding@resend.dev",
                    "to": admin_email,
                    "subject": f"Kontak Portofolio: {subject}",
                    "html": email_body
                })
                logger.info(f"Email notification successfully sent via Resend to {admin_email}")
            except Exception as email_err:
                # Catch email error so it doesn't break the form submission if API key is invalid
                logger.error(f"Resend email failed: {email_err}")
                print(f"Resend email notification failed: {email_err}")

        flash('Pesan Anda berhasil dikirim. Terima kasih!', 'success')
    except Exception as error:
        db.session.rollback()
        flash(f'Gagal mengirim pesan: {error}', 'danger')
        logger.error(f'Contact submit error: {error}')

    return redirect(url_for('utama.home'))
