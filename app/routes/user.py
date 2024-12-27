import random

from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import current_user
from sqlalchemy import func
from werkzeug.security import generate_password_hash

from app import db
from app.models import User, Drone, Pilot, Admin, DeliveryTask, Package
bp = Blueprint('user', __name__)

@bp.route('/')
def dashboard():
    return render_template('user.html', user=current_user)

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
