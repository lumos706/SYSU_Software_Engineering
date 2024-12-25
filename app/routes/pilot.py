from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user

from app.models import DeliveryTask, DroneHistory
from app import db

bp = Blueprint('pilot', __name__)

@bp.route('/')
def dashboard():
    pilot_id = current_user.pilot_id
    tasks = DeliveryTask.query.filter_by(pilot_id=pilot_id).all()
    return render_template('pilot.html', tasks=tasks)

@bp.route('/update_task_status/<int:task_id>', methods=['POST'])
def update_task_status(task_id):
    task = DeliveryTask.query.get_or_404(task_id)
    task.status = request.form['status']
    db.session.commit()
    return redirect(url_for('pilot.dashboard'))

@bp.route('/log_maintenance', methods=['POST'])
def log_maintenance():
    drone_id = request.form['drone_id']
    location = request.form['location']
    new_record = DroneHistory(drone_id=drone_id, timestamp=datetime.now(), location=location)
    db.session.add(new_record)
    db.session.commit()
    return redirect(url_for('pilot.dashboard'))
