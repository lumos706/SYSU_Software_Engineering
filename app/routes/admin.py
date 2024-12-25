from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from app.models import User, Drone, Pilot, Admin, DeliveryTask, DroneHistory, Package
from app import db
from werkzeug.security import generate_password_hash
from flask_login import current_user

bp = Blueprint('admin', __name__)


@bp.route('/')
def dashboard():
    return render_template('admin.html', admin=current_user)


@bp.route('/manage_user')
def manage_user():
    users = User.query.all()
    return render_template('manage_user.html', users=users, admin=current_user, lineStyle=None)


@bp.route('/add_user', methods=['POST'])
def add_user():
    username = request.form['username']
    password = request.form['password']
    contact_info = request.form['contact_info']
    # 检查用户名是否已存在
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'error': '用户名已存在，请选择其他用户名！'}), 400
    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password, contact_info=contact_info)
    db.session.add(new_user)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '用户注册失败，请稍后再试！'}), 500
    return redirect(url_for('admin.manage_user'))


@bp.route('/manage_drone')
def manage_drone():
    drones = Drone.query.all()
    return render_template('manage_drone.html', drones=drones, admin=current_user, lineStyle=None)


@bp.route('/add_drone', methods=['POST'])
def add_drone():
    model = request.form['model']
    status = request.form['status']
    max_load_capacity = request.form['max_load_capacity']
    location = request.form['location']
    battery_level = request.form['battery_level']
    new_drone = Drone(model=model, status=status, max_load_capacity=max_load_capacity, location=location,
                      battery_level=battery_level)
    db.session.add(new_drone)
    db.session.commit()
    return redirect(url_for('admin.dashboard'))


@bp.route('/manage_pilot')
def manage_pilot():
    pilots = Pilot.query.all()
    return render_template('manage_pilot.html', pilots=pilots, admin=current_user, lineStyle=None)


@bp.route('/api/users')
def api_users():
    users = User.query.all()
    users_data = {
        "status": 0,
        "message": "",
        "total": len(users),
        "data": {
            "item": [
                {
                    "id": user.user_id,
                    "username": user.username,
                    "contact_info": user.contact_info,
                } for user in users
            ]
        }
    }
    return jsonify(users_data)

@bp.route('/api/drones')
def api_drones():
    drones = Drone.query.all()
    drones_data = {
        "status": 0,
        "message": "",
        "total": len(drones),
        "data": {
            "item": [
                {
                    "id": drone.drone_id,
                    "model": drone.model,
                    "status": drone.status,
                    "max_load_capacity": drone.max_load_capacity,
                    "location": drone.location,
                    "battery_level": drone.battery_level,
                } for drone in drones
            ]
        }
    }
    return jsonify(drones_data)

@bp.route('/api/pilots')
def api_pilots():
    pilots = Pilot.query.all()
    pilots_data = {
        "status": 0,
        "message": "",
        "total": len(pilots),
        "data": {
            "item": [
                {
                    "id": pilot.pilot_id,
                    "name": pilot.name,
                    "contact_info": pilot.contact_info,
                } for pilot in pilots
            ]
        }
    }
    return jsonify(pilots_data)