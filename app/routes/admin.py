from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from app.models import User, Drone, Pilot, Admin, DeliveryTask, DroneHistory, Package
from app import db
from werkzeug.security import generate_password_hash
from flask_login import current_user

bp = Blueprint('admin', __name__)


@bp.route('/')
def dashboard():
    return render_template('admin.html', admin=current_user)

@bp.route('/admin_modify', methods=['POST', 'GET'])
def admin_modify():
    name = request.form['name']
    password = request.form['password']
    login_credentials = request.form['login_credentials']
    # 获取请求数据
    print(current_user.admin_id)
    admin_id = current_user.admin_id  # 替换为实际管理员 ID，例如通过 current_user 或表单获取
    admin = Admin.query.get(admin_id)
    try:
        if name:
            admin.name = name
        if login_credentials:
            admin.login_credentials = login_credentials
        if password:
            admin.password = password
        db.session.commit()
        return redirect(url_for('auth.login_admin'))
    except Exception as e:
        db.session.rollback()
        return redirect(url_for('admin.dashboard'))

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

@bp.route('/bulk_register', methods=['POST', 'GET'])
def bulk_register():
    try:
        users = []
        max_id = db.session.query(func.max(User.user_id)).scalar() or 0
        for i in range(max_id+1, max_id+11):  # 循环生成 1000 个用户
            username = f"user{i}"
            contact_info = f"user{i}@example.com"
            password = f"password{i}"
            hashed_password = generate_password_hash(password)

            # 创建用户对象并添加到列表
            user = User(username=username, password=hashed_password, contact_info=contact_info)
            users.append(user)

        # 使用 SQLAlchemy 批量插入
        db.session.bulk_save_objects(users)
        db.session.commit()

        return redirect(url_for('admin.manage_user'))
    except Exception as e:
        db.session.rollback()
        return redirect(url_for('admin.manage_user'))
    return redirect(url_for('admin.manage_user'))

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
                    "password": user.password,
                } for user in users
            ]
        }
    }
    return jsonify(users_data)

@bp.route('/delete_user/<int:user_id>', methods=['POST', 'GET'])
def delete_user(user_id):
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    entries = db.session.query(User).order_by(User.user_id).all()
    for new_id, entry in enumerate(entries, start=1):
        entry.id = new_id
    db.session.commit()  # 提交 ID 更新操作
    return redirect(url_for('admin.manage_user'))

@bp.route('/bulk_delete_user/<ids>', methods=['POST', 'GET'])
def bulk_delete_user(ids):
    # 将逗号分隔的 ID 字符串转换为整数列表
    id_list = list(map(int, ids.split(',')))

    # 删除指定 ID 的用户
    users_to_delete = User.query.filter(User.user_id.in_(id_list)).all()
    for user in users_to_delete:
        db.session.delete(user)
    db.session.commit()

    # 重新排序 ID
    entries = db.session.query(User).order_by(User.user_id).all()
    for new_id, entry in enumerate(entries, start=1):
        entry.user_id = new_id
    db.session.commit()  # 提交 ID 更新操作

    return redirect(url_for('admin.manage_user'))

@bp.route('/update_user', methods=['POST', 'GET'])
def update_user():
    try:
        # 从表单中获取提交的数据
        user_id = request.form.get('id')  # 用户主键 ID
        field = request.form.get('field')  # 被编辑的字段名
        value = request.form.get('value')  # 修改后的值
        # 校验参数完整性
        if not user_id or not field or value is None:
            return jsonify({"success": False, "message": "参数不完整"})
        # 根据 ID 获取用户记录
        user = User.query.get(user_id)
        if not user:
            return jsonify({"success": False, "message": "用户不存在"})
        # 动态设置字段值
        if field == 'username':
            user.username = value
        elif field == 'contact_info':
            user.contact_info = value
        elif field == 'password':
            user.password = generate_password_hash(value)  # 密码需要加密
        else:
            return jsonify({"success": False, "message": "无效的字段{"+field+"}"})
        # 提交更新到数据库
        db.session.commit()
        return jsonify({"success": True, "message": "用户信息更新成功"})
    except Exception as e:
        db.session.rollback()  # 回滚事务
        return jsonify({"success": False, "message": f"更新失败：{str(e)}"})



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

@bp.route('/manage_pilot')
def manage_pilot():
    pilots = Pilot.query.all()
    return render_template('manage_pilot.html', pilots=pilots, admin=current_user, lineStyle=None)

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

@bp.route('/manage_task')
def manage_task():
    tasks = DeliveryTask.query.all()
    return render_template('manage_task.html', tasks=tasks, admin=current_user, lineStyle=None)

@bp.route('/manage_package')
def manage_package():
    packages = Package.query.all()
    return render_template('manage_package.html', packages=packages, admin=current_user, lineStyle=None)