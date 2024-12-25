from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user

from app.models import Package
from app import db
bp = Blueprint('user', __name__)

@bp.route('/')
def dashboard():
    user_id = current_user.user_id
    # packages = Package.query.filter_by(user_id=user_id).all()
    return render_template('user.html')

@bp.route('/cancel_package/<int:package_id>')
def cancel_package(package_id):
    package = Package.query.get_or_404(package_id)
    if package.status == 'Pending':
        db.session.delete(package)
        db.session.commit()
    return redirect(url_for('user.dashboard'))

@bp.route('/update_info', methods=['POST'])
def update_info():
    current_user.contact_info = request.form['contact_info']
    db.session.commit()
    return redirect(url_for('user.dashboard'))
