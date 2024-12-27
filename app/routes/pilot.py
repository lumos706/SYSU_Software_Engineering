from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import current_user, login_required
from app.models import DeliveryTask, DroneHistory, Package, Drone, Pilot
from app import db

bp = Blueprint('pilot', __name__)

# Dashboard
@bp.route('/')
@login_required
def dashboard():
    # 获取当前飞行员的 ID
    pilot_id = current_user.pilot_id

    # 查询归属于当前飞行员的无人机
    drones = Drone.query.filter_by(pilot_id=pilot_id).all()
    drone_ids = [drone.drone_id for drone in drones]
    print("in pilot1---------------------------------------------------")
    # 查询无人机关联的任务
    tasks = DeliveryTask.query.filter(DeliveryTask.drone_id.in_(drone_ids)).all() if drone_ids else []
    print("in pilot2----------------------------------------------------")
    # 渲染模板
    return render_template('pilot.html', tasks=tasks, pilot=Pilot.query.get(current_user.pilot_id))


# 查看飞行员信息
@bp.route('/profile', methods=['GET'])
@login_required
def profile():
    pilot = Pilot.query.get_or_404(current_user.pilot_id)
    return jsonify({
        "name": pilot.name,
        "contact_info": pilot.contact_info,
    })


# 更新飞行员信息
@bp.route('/update_info', methods=['POST'])
@login_required
def update_info():
    pilot = Pilot.query.get_or_404(current_user.pilot_id)
    pilot.contact_info = request.form.get('contact')
    db.session.commit()
    return redirect(url_for('pilot.dashboard'))


# 更新飞行员登录凭据
@bp.route('/update_credentials', methods=['POST'])
@login_required
def update_credentials():
    pilot = Pilot.query.get_or_404(current_user.pilot_id)
    new_password = request.form.get('password')
    pilot.password = new_password  # 假设已加密处理密码
    db.session.commit()
    return redirect(url_for('pilot.dashboard'))


# 获取未分配包裹
@bp.route('/unassigned_packages', methods=['GET'])
@login_required
def unassigned_packages():
    # 查询未分配包裹
    packages = Package.query.filter_by(task_id=None).all()
    # 查询当前飞行员的所有 Active 状态无人机
    drones = Drone.query.filter_by(pilot_id=current_user.pilot_id, status="Active").all()

    return jsonify({
        "packages": [
            {
                "package_id": pkg.package_id,
                "recipient_name": pkg.recipient_name,
                "recipient_address": pkg.recipient_address,
            }
            for pkg in packages
        ],
        "drones": [
            {
                "drone_id": drone.drone_id,
                "model": drone.model,
            }
            for drone in drones
        ],
    })



# 分配包裹
@bp.route('/assign_package/<int:package_id>', methods=['POST'])
@login_required
def assign_package(package_id):
    package = Package.query.get_or_404(package_id)

    # 确认包裹未被分配
    if package.task_id is not None:
        return jsonify({"message": "该包裹已被分配"}), 400

    # 获取前端传入的无人机 ID
    drone_id = request.json.get("drone_id")
    drone = Drone.query.filter_by(drone_id=drone_id, pilot_id=current_user.pilot_id, status="Active").first()
    if not drone:
        return jsonify({"message": "选择的无人机不可用"}), 400

    # 创建任务并分配给无人机
    new_task = DeliveryTask(
        drone_id=drone.drone_id,
        start_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        completion_status="In Progress"
    )
    db.session.add(new_task)
    db.session.commit()

    # 更新包裹的任务 ID
    package.task_id = new_task.task_id
    db.session.commit()

    return jsonify({"message": f"包裹分配成功，使用无人机 {drone.model} ({drone.drone_id})"}), 200


# 获取归属于当前飞行员的无人机
@bp.route('/my_drones', methods=['GET'])
@login_required
def my_drones():
    pilot_id = current_user.pilot_id
    drones = Drone.query.filter_by(pilot_id=pilot_id).all()

    return jsonify([
        {
            "drone_id": drone.drone_id,
            "model": drone.model,
            "status": drone.status,
            "battery_level": drone.battery_level,
            "location": drone.location,
        }
        for drone in drones
    ])

@bp.route('/drone_tasks/<int:drone_id>', methods=['GET'])
@login_required
def drone_tasks(drone_id):
    # 确保无人机属于当前飞行员
    drone = Drone.query.filter_by(drone_id=drone_id, pilot_id=current_user.pilot_id).first_or_404()

    # 获取无人机任务，按开始时间排序
    tasks = DeliveryTask.query.filter_by(drone_id=drone_id).order_by(DeliveryTask.start_time).all()

    # 包含包裹信息的任务详情
    tasks_data = []
    for task in tasks:
        package = Package.query.filter_by(task_id=task.task_id).first()
        tasks_data.append({
            "task_id": task.task_id,
            "start_time": task.start_time,
            "completion_status": task.completion_status,
            "recipient_name": package.recipient_name if package else "未指定",
            "recipient_address": package.recipient_address if package else "未指定",
        })

    return jsonify(tasks_data)
