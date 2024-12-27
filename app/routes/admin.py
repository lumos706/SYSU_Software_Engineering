import random

from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import current_user
from sqlalchemy import func
from werkzeug.security import generate_password_hash

from app import db
from app.models import User, Drone, Pilot, Admin, DeliveryTask, Package

bp = Blueprint('admin', __name__)


#-------------------------------------------------------------------------------------------------------------
# 管理员登录
@bp.route('/')
def dashboard():
    return render_template('admin.html', admin=current_user)


# -------------------------------------------------------------------------------------------------------------
# 管理员修改信息
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


# -------------------------------------------------------------------------------------------------------------
# 管理员获取信息
@bp.route('/manage_user')
def manage_user():
    users = User.query.all()
    return render_template('manage_user.html', users=users, admin=current_user, lineStyle=None)


@bp.route('/manage_task')
def manage_task():
    tasks = DeliveryTask.query.all()
    return render_template('manage_task.html', tasks=tasks, admin=current_user, lineStyle=None)


@bp.route('/manage_package')
def manage_package():
    packages = Package.query.all()
    return render_template('manage_package.html', packages=packages, admin=current_user, lineStyle=None)


@bp.route('/manage_pilot')
def manage_pilot():
    pilots = Pilot.query.all()
    return render_template('manage_pilot.html', pilots=pilots, admin=current_user, lineStyle=None)


@bp.route('/manage_drone')
def manage_drone():
    drones = Drone.query.all()
    return render_template('manage_drone.html', drones=drones, admin=current_user, lineStyle=None)


# -------------------------------------------------------------------------------------------------------------

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


@bp.route('/add_pilot', methods=['POST'])
def add_pilot():
    name = request.form['name']
    contact_info = request.form['contact_info']
    login_credentials = request.form['login_credentials']
    password = request.form['password']
    # 检查用户名是否已存在
    existing_pilot = Pilot.query.filter_by(login_credentials=login_credentials).first()
    if existing_pilot:
        return jsonify({'error': '用户名已存在，请选择其他用户名！'}), 400
    hashed_password = generate_password_hash(password)
    new_pilot = Pilot(name=name, contact_info=contact_info, login_credentials=login_credentials,
                      password=hashed_password)
    db.session.add(new_pilot)
    db.session.commit()
    return redirect(url_for('admin.manage_pilot'))


@bp.route('/add_drone', methods=['POST'])
def add_drone():
    model = request.form['model']
    status = request.form['status']
    max_load_capacity = request.form['max_load_capacity']
    location = request.form['location']
    battery_level = request.form['battery_level']
    manufacture_date = request.form['manufacture_date']
    pilot_id = request.form['pilot_id']
    new_drone = Drone(model=model, status=status, max_load_capacity=max_load_capacity, location=location,
                      battery_level=battery_level, manufacture_date=manufacture_date, pilot_id=pilot_id)
    db.session.add(new_drone)
    db.session.commit()
    return redirect(url_for('admin.manage_drone'))


@bp.route('/add_package', methods=['POST'])
def add_package():
    recipient_name = request.form['recipient_name']
    recipient_address = request.form['recipient_address']
    package_info = request.form['package_info']
    task_id = request.form['task_id']
    user_id = request.form['user_id']
    new_package = Package(recipient_name=recipient_name, recipient_address=recipient_address, package_info=package_info,
                          task_id=task_id, user_id=user_id)
    db.session.add(new_package)
    db.session.commit()
    return redirect(url_for('admin.manage_package'))


@bp.route('/add_task', methods=['POST'])
def add_task():
    drone_id = request.form['drone_id']
    start_time = request.form['start_time']
    completion_status = request.form['completion_status']
    new_task = DeliveryTask(drone_id=drone_id, start_time=start_time, completion_status=completion_status)
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('admin.manage_task'))


# -------------------------------------------------------------------------------------------------------------
# 批量注册用户
@bp.route('/bulk_register_user', methods=['POST', 'GET'])
def bulk_register_user():
    try:
        users = []
        max_id = db.session.query(func.max(User.user_id)).scalar() or 0
        for i in range(max_id + 1, max_id + 11):  # 循环生成 1000 个用户
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


@bp.route('/bulk_register_pilot', methods=['POST', 'GET'])
def bulk_register_pilot():
    try:
        pilots = []
        max_id = db.session.query(func.max(Pilot.pilot_id)).scalar() or 0
        for i in range(max_id + 1, max_id + 11):  # 循环生成 1000 个用户
            name = f"pilot{i}"
            contact_info = f"pilot{i}@example.com"
            login_credentials = f"pilot{i}"
            password = f"password{i}"
            hashed_password = generate_password_hash(password)

            # 创建用户对象并添加到列表
            pilot = Pilot(name=name, contact_info=contact_info, login_credentials=login_credentials,
                          password=hashed_password)
            pilots.append(pilot)

        # 使用 SQLAlchemy 批量插入
        db.session.bulk_save_objects(pilots)
        db.session.commit()

        return redirect(url_for('admin.manage_pilot'))
    except Exception as e:
        db.session.rollback()
        return redirect(url_for('admin.manage_pilot'))


@bp.route('/bulk_register_drone', methods=['POST', 'GET'])
def bulk_register_drone():
    try:
        drones = []
        pilot_ids_list = db.session.query(Pilot.pilot_id).scalars().all()
        max_id = db.session.query(func.max(Drone.drone_id)).scalar() or 0
        for i in range(max_id + 1, max_id + 11):  # 循环生成 10 个用户
            model = f"drone{i}"
            status = "READY"
            max_load_capacity = 100
            location = f"location{i}"
            battery_level = 100
            manufacture_date = "2021-01-01"
            pilot_id = random.randint(pilot_ids_list[0], pilot_ids_list[-1])

            # 创建用户对象并添加到列表
            drone = Drone(model=model, status=status, max_load_capacity=max_load_capacity, location=location,
                          battery_level=battery_level, manufacture_date=manufacture_date, pilot_id=pilot_id)
            drones.append(drone)

        # 使用 SQLAlchemy 批量插入
        db.session.bulk_save_objects(drones)
        db.session.commit()

        return redirect(url_for('admin.manage_drone'))
    except Exception as e:
        db.session.rollback()
        return redirect(url_for('admin.manage_drone'))


@bp.route('/bulk_register_package', methods=['POST', 'GET'])
def bulk_register_package():
    try:
        packages = []
        task_ids_list = db.session.query(DeliveryTask.task_id).scalars().all()
        user_ids_list = db.session.query(User.user_id).scalars().all()
        max_id = db.session.query(func.max(Package.package_id)).scalar() or 0
        for i in range(max_id + 1, max_id + 11):  # 循环生成 10 个用户
            recipient_name = f"recipient{i}"
            recipient_address = f"address{i}"
            package_info = f"package{i}"
            task_id = random.randint(task_ids_list[0], task_ids_list[-1])
            user_id = random.randint(user_ids_list[0], user_ids_list[-1])

            # 创建用户对象并添加到列表
            package = Package(recipient_name=recipient_name, recipient_address=recipient_address,
                              package_info=package_info,
                              task_id=task_id, user_id=user_id)
            packages.append(package)

        # 使用 SQLAlchemy 批量插入
        db.session.bulk_save_objects(packages)
        db.session.commit()

        return redirect(url_for('admin.manage_package'))
    except Exception as e:
        db.session.rollback()
        return redirect(url_for('admin.manage_package'))


@bp.route('/bulk_register_task', methods=['POST', 'GET'])
def bulk_register_task():
    try:
        tasks = []
        drone_ids_list = db.session.query(Drone.drone_id).scalars().all()
        max_id = db.session.query(func.max(DeliveryTask.task_id)).scalar() or 0
        for i in range(max_id + 1, max_id + 11):  # 循环生成 10 个用户
            drone_id = random.randint(drone_ids_list[0], drone_ids_list[-1])
            start_time = "2021-01-01 09:00:00"
            completion_status = "DONE"

            # 创建用户对象并添加到列表
            task = DeliveryTask(drone_id=drone_id, start_time=start_time, completion_status=completion_status)
            tasks.append(task)

        # 使用 SQLAlchemy 批量插入
        db.session.bulk_save_objects(tasks)
        db.session.commit()

        return redirect(url_for('admin.manage_task'))
    except Exception as e:
        db.session.rollback()
        return redirect(url_for('admin.manage_task'))


# -------------------------------------------------------------------------------------------------------------
# API 接口(返回 JSON 格式数据)
@bp.route('/api/users')
def api_users():
    # 获取筛选条件
    id = request.args.get('id')  # 获取 ID 参数
    username = request.args.get('username')  # 获取 username 参数
    contact_info = request.args.get('contact_info')  # 获取 contact_info 参数

    # 构造查询
    query = User.query
    if id:  # 如果 ID 存在，添加筛选条件
        query = query.filter(User.user_id == id)
    if username:  # 如果 username 存在，添加筛选条件
        query = query.filter(User.username == username)
    if contact_info:  # 如果 contact_info 存在，添加筛选条件
        query.filter(User.contact_info == contact_info)

    users = query.all()
    cnt = len(users)
    users_data = {
        "status": 0,
        "message": "共有{}条记录".format(cnt),
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


@bp.route('/api/pilots')
def api_pilots():
    # 获取筛选条件
    id = request.args.get('id')  # 获取 ID 参数
    name = request.args.get('name')
    contact_info = request.args.get('contact_info')

    # 构造查询
    query = Pilot.query
    if id:
        query = query.filter(Pilot.pilot_id == id)
    if name:
        query = query.filter(Pilot.name == name)
    if contact_info:
        query.filter(Pilot.contact_info == contact_info)

    pilots = query.all()
    cnt = len(pilots)
    pilots_data = {
        "status": 0,
        "message": "共有{}条记录".format(cnt),
        "total": len(pilots),
        "data": {
            "item": [
                {
                    "id": pilot.pilot_id,
                    "name": pilot.name,
                    "contact_info": pilot.contact_info,
                    "login_credentials": pilot.login_credentials,
                    "password": pilot.password,
                } for pilot in pilots
            ]
        }
    }
    return jsonify(pilots_data)


@bp.route('/api/drones')
def api_drones():
    # 获取筛选条件
    id = request.args.get('id')  # 获取 ID 参数
    model = request.args.get('model')
    status = request.args.get('status')
    manufacture_date = request.args.get('manufacture_date')
    location = request.args.get('location')
    pilot_id = request.args.get('pilot_id')

    # 构造查询
    query = Drone.query
    if id:
        query = query.filter(Drone.drone_id == id)
    if model:
        query = query.filter(Drone.model == model)
    if status:
        query = query.filter(Drone.status == status)
    if manufacture_date:
        query = query.filter(Drone.manufacture_date == manufacture_date)
    if location:
        query = query.filter(Drone.location.like(f"%{location}%"))
    if pilot_id:
        query = query.filter(Drone.pilot_id == pilot_id)

    drones = query.all()
    cnt = len(drones)
    drones_data = {
        "status": 0,
        "message": "共有{}条记录".format(cnt),
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
                    "manufacture_date": drone.manufacture_date,
                    "pilot_id": drone.pilot_id,
                } for drone in drones
            ]
        }
    }
    return jsonify(drones_data)


@bp.route('/api/packages')
def api_packages():
    # 获取筛选条件
    id = request.args.get('id')  # 获取 ID 参数
    recipient_name = request.args.get('recipient_name')
    task_id = request.args.get('task_id')
    user_id = request.args.get('user_id')

    # 构造查询
    query = Package.query
    if id:
        query = query.filter(Package.package_id == id)
    if recipient_name:
        query = query.filter(Package.recipient_name == recipient_name)
    if task_id:
        query = query.filter(Package.task_id == task_id)
    if user_id:
        query = query.filter(Package.user_id == user_id)

    packages = query.all()
    cnt = len(packages)
    packages_data = {
        "status": 0,
        "message": "共有{}条记录".format(cnt),
        "total": len(packages),
        "data": {
            "item": [
                {
                    "id": package.package_id,
                    "recipient_name": package.recipient_name,
                    "recipient_address": package.recipient_address,
                    "package_info": package.package_info,
                    "task_id": package.task_id,
                    "user_id": package.user_id,
                } for package in packages
            ]
        }
    }
    return jsonify(packages_data)


@bp.route('/api/tasks')
def api_tasks():
    # 获取筛选条件
    id = request.args.get('id')  # 获取 ID 参数
    drone_id = request.args.get('drone_id')
    start_time = request.args.get('start_time')
    completion_status = request.args.get('completion_status')

    # 构造查询
    query = DeliveryTask.query
    if id:
        query = query.filter(DeliveryTask.task_id == id)
    if drone_id:
        query = query.filter(DeliveryTask.drone_id == drone_id)
    if start_time:
        query = query.filter(DeliveryTask.start_time.like(f"%{start_time}%"))
    if completion_status:
        query = query.filter(DeliveryTask.completion_status.like(f"%{completion_status}%"))

    tasks = query.all()
    cnt = len(tasks)
    tasks_data = {
        "status": 0,
        "message": "共有{}条记录".format(cnt),
        "total": len(tasks),
        "data": {
            "item": [
                {
                    "id": task.task_id,
                    "drone_id": task.drone_id,
                    "start_time": task.start_time,
                    "completion_status": task.completion_status,
                } for task in tasks
            ]
        }
    }
    return jsonify(tasks_data)


# -------------------------------------------------------------------------------------------------------------
# 删除用户(单个)
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


@bp.route('/delete_pilot/<int:pilot_id>', methods=['POST', 'GET'])
def delete_pilot(pilot_id):
    pilot = Pilot.query.get(pilot_id)
    db.session.delete(pilot)
    db.session.commit()
    entries = db.session.query(Pilot).order_by(Pilot.pilot_id).all()
    for new_id, entry in enumerate(entries, start=1):
        entry.id = new_id
    db.session.commit()
    return redirect(url_for('admin.manage_pilot'))


@bp.route('/delete_drone/<int:drone_id>', methods=['POST', 'GET'])
def delete_drone(drone_id):
    drone = Drone.query.get(drone_id)
    db.session.delete(drone)
    db.session.commit()
    entries = db.session.query(Drone).order_by(Drone.drone_id).all()
    for new_id, entry in enumerate(entries, start=1):
        entry.id = new_id
    db.session.commit()
    return redirect(url_for('admin.manage_drone'))


@bp.route('/delete_package/<int:package_id>', methods=['POST', 'GET'])
def delete_package(package_id):
    package = Package.query.get(package_id)
    db.session.delete(package)
    db.session.commit()
    entries = db.session.query(Package).order_by(Package.package_id).all()
    for new_id, entry in enumerate(entries, start=1):
        entry.id = new_id
    db.session.commit()
    return redirect(url_for('admin.manage_package'))


@bp.route('/delete_task/<int:task_id>', methods=['POST', 'GET'])
def delete_task(task_id):
    task = DeliveryTask.query.get(task_id)
    db.session.delete(task)
    db.session.commit()
    entries = db.session.query(DeliveryTask).order_by(DeliveryTask.task_id).all()
    for new_id, entry in enumerate(entries, start=1):
        entry.id = new_id
    db.session.commit()
    return redirect(url_for('admin.manage_task'))


# -------------------------------------------------------------------------------------------------------------
# 删除用户(批量)
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


@bp.route('/bulk_delete_pilot/<ids>', methods=['POST', 'GET'])
def bulk_delete_pilot(ids):
    # 将逗号分隔的 ID 字符串转换为整数列表
    id_list = list(map(int, ids.split(',')))

    # 删除指定 ID 的用户
    pilots_to_delete = Pilot.query.filter(Pilot.pilot_id.in_(id_list)).all()
    for pilot in pilots_to_delete:
        db.session.delete(pilot)
    db.session.commit()

    # 重新排序 ID
    entries = db.session.query(Pilot).order_by(Pilot.pilot_id).all()
    for new_id, entry in enumerate(entries, start=1):
        entry.pilot_id = new_id
    db.session.commit()  # 提交 ID 更新操作

    return redirect(url_for('admin.manage_pilot'))


@bp.route('/bulk_delete_drone/<ids>', methods=['POST', 'GET'])
def bulk_delete_drone(ids):
    # 将逗号分隔的 ID 字符串转换为整数列表
    id_list = list(map(int, ids.split(',')))

    # 删除指定 ID 的用户
    drones_to_delete = Drone.query.filter(Drone.drone_id.in_(id_list)).all()
    for drone in drones_to_delete:
        db.session.delete(drone)
    db.session.commit()

    # 重新排序 ID
    entries = db.session.query(Drone).order_by(Drone.drone_id).all()
    for new_id, entry in enumerate(entries, start=1):
        entry.drone_id = new_id
    db.session.commit()

    return redirect(url_for('admin.manage_drone'))


@bp.route('/bulk_delete_package/<ids>', methods=['POST', 'GET'])
def bulk_delete_package(ids):
    # 将逗号分隔的 ID 字符串转换为整数列表
    id_list = list(map(int, ids.split(',')))

    # 删除指定 ID 的用户
    packages_to_delete = Package.query.filter(Package.package_id.in_(id_list)).all()
    for package in packages_to_delete:
        db.session.delete(package)
    db.session.commit()

    # 重新排序 ID
    entries = db.session.query(Package).order_by(Package.package_id).all()
    for new_id, entry in enumerate(entries, start=1):
        entry.package_id = new_id
    db.session.commit()

    return redirect(url_for('admin.manage_package'))


@bp.route('/bulk_delete_task/<ids>', methods=['POST', 'GET'])
def bulk_delete_task(ids):
    # 将逗号分隔的 ID 字符串转换为整数列表
    id_list = list(map(int, ids.split(',')))

    # 删除指定 ID 的用户
    tasks_to_delete = DeliveryTask.query.filter(DeliveryTask.task_id.in_(id_list)).all()
    for task in tasks_to_delete:
        db.session.delete(task)
    db.session.commit()

    # 重新排序 ID
    entries = db.session.query(DeliveryTask).order_by(DeliveryTask.task_id).all()
    for new_id, entry in enumerate(entries, start=1):
        entry.task_id = new_id
    db.session.commit()

    return redirect(url_for('admin.manage_task'))


# -------------------------------------------------------------------------------------------------------------
# 更新信息
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
            return jsonify({"success": False, "message": "无效的字段{" + field + "}"})
        # 提交更新到数据库
        db.session.commit()
        return jsonify({"success": True, "message": "用户信息更新成功"})
    except Exception as e:
        db.session.rollback()  # 回滚事务
        return jsonify({"success": False, "message": f"更新失败：{str(e)}"})


@bp.route('/update_pilot', methods=['POST', 'GET'])
def update_pilot():
    try:
        # 从表单中获取提交的数据
        pilot_id = request.form.get('id')  # 用户主键 ID
        field = request.form.get('field')  # 被编辑的字段名
        value = request.form.get('value')  # 修改后的值
        # 校验参数完整性
        if not pilot_id or not field or value is None:
            return jsonify({"success": False, "message": "参数不完整"})
        # 根据 ID 获取用户记录
        pilot = Pilot.query.get(pilot_id)
        if not pilot:
            return jsonify({"success": False, "message": "用户不存在"})
        # 动态设置字段值
        if field == 'name':
            pilot.name = value
        elif field == 'contact_info':
            pilot.contact_info = value
        elif field == 'login_credentials':
            pilot.login_credentials = value
        elif field == 'password':
            pilot.password = generate_password_hash(value)  # 密码需要加密
        else:
            return jsonify({"success": False, "message": "无效的字段{" + field + "}"})
        # 提交更新到数据库
        db.session.commit()
        return jsonify({"success": True, "message": "用户信息更新成功"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"更新失败：{str(e)}"})


@bp.route('/update_drone', methods=['POST', 'GET'])
def update_drone():
    try:
        # 从表单中获取提交的数据
        drone_id = request.form.get('id')  # 用户主键 ID
        field = request.form.get('field')  # 被编辑的字段名
        value = request.form.get('value')  # 修改后的值
        # 校验参数完整性
        if not drone_id or not field or value is None:
            return jsonify({"success": False, "message": "参数不完整"})
        # 根据 ID 获取用户记录
        drone = Drone.query.get(drone_id)
        if not drone:
            return jsonify({"success": False, "message": "用户不存在"})
        # 动态设置字段值
        if field == 'model':
            drone.model = value
        elif field == 'status':
            drone.status = value
        elif field == 'max_load_capacity':
            drone.max_load_capacity = value
        elif field == 'location':
            drone.location = value
        elif field == 'battery_level':
            drone.battery_level = value
        elif field == 'manufacture_date':
            drone.manufacture_date = value
        elif field == 'pilot_id':
            drone.pilot_id = value
        else:
            return jsonify({"success": False, "message": "无效的字段{" + field + "}"})
        # 提交更新到数据库
        db.session.commit()
        return jsonify({"success": True, "message": "用户信息更新成功"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"更新失败：{str(e)}"})


@bp.route('/update_package', methods=['POST', 'GET'])
def update_package():
    try:
        # 从表单中获取提交的数据
        package_id = request.form.get('id')  # 用户主键 ID
        field = request.form.get('field')  # 被编辑的字段名
        value = request.form.get('value')  # 修改后的值
        # 校验参数完整性
        if not package_id or not field or value is None:
            return jsonify({"success": False, "message": "参数不完整"})
        # 根据 ID 获取用户记录
        package = Package.query.get(package_id)
        if not package:
            return jsonify({"success": False, "message": "用户不存在"})
        # 动态设置字段值
        if field == 'recipient_name':
            package.recipient_name = value
        elif field == 'recipient_address':
            package.recipient_address = value
        elif field == 'package_info':
            package.package_info = value
        elif field == 'task_id':
            package.task_id = value
        elif field == 'user_id':
            package.user_id = value
        else:
            return jsonify({"success": False, "message": "无效的字段{" + field + "}"})
        # 提交更新到数据库
        db.session.commit()
        return jsonify({"success": True, "message": "用户信息更新成功"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"更新失败：{str(e)}"})


@bp.route('/update_task', methods=['POST', 'GET'])
def update_task():
    try:
        # 从表单中获取提交的数据
        task_id = request.form.get('id')  # 用户主键 ID
        field = request.form.get('field')  # 被编辑的字段名
        value = request.form.get('value')  # 修改后的值
        # 校验参数完整性
        if not task_id or not field or value is None:
            return jsonify({"success": False, "message": "参数不完整"})
        # 根据 ID 获取用户记录
        task = DeliveryTask.query.get(task_id)
        if not task:
            return jsonify({"success": False, "message": "用户不存在"})
        # 动态设置字段值
        if field == 'drone_id':
            task.drone_id = value
        elif field == 'start_time':
            task.start_time = value
        elif field == 'completion_status':
            task.completion_status = value
        else:
            return jsonify({"success": False, "message": "无效的字段{" + field + "}"})
        # 提交更新到数据库
        db.session.commit()
        return jsonify({"success": True, "message": "用户信息更新成功"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"更新失败：{str(e)}"})
# -------------------------------------------------------------------------------------------------------------
