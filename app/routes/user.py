from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import current_user, login_required
from app.models import Package, DeliveryTask, Drone, DroneHistory
from app import db

bp = Blueprint('user', __name__)


@bp.route('/')
@login_required  # 确保用户已登录
def dashboard():
    user_id = current_user.user_id
    packages = Package.query.filter_by(user_id=user_id).all()  # 查询用户包裹
    return render_template('user.html', user=current_user, packages=packages)


@bp.route('/package/add', methods=['POST'])
@login_required
def add_package():
    # 从表单中获取数据
    recipient_name = request.form.get('recipient_name')
    recipient_address = request.form.get('recipient_address')
    package_info = request.form.get('package_info')

    # 验证输入是否有效
    if not recipient_name or not recipient_address:
        return "收件人姓名和地址不能为空", 400

    # 创建新的包裹记录
    new_package = Package(
        recipient_name=recipient_name,
        recipient_address=recipient_address,
        package_info=package_info,
        user_id=current_user.user_id,
        task_id=None  # 新建时未分配任务
    )
    db.session.add(new_package)
    db.session.commit()

    return redirect(url_for('user.dashboard'))


@bp.route('/package/status/<int:package_id>')
@login_required
def package_status(package_id):
    # 查询包裹信息
    package = Package.query.get_or_404(package_id)

    # 如果包裹未分配任务
    if not package.task_id:
        return jsonify({
            'package_status': '未分配任务',
            'package_id': package.package_id,
            'recipient_name': package.recipient_name,
            'recipient_address': package.recipient_address,
            'package_info': package.package_info
        })

    # 查询任务信息
    task = DeliveryTask.query.filter_by(task_id=package.task_id).first()

    # 如果任务不存在
    if not task:
        return jsonify({
            'package_status': '任务不存在',
            'package_id': package.package_id,
            'recipient_name': package.recipient_name,
            'recipient_address': package.recipient_address,
            'package_info': package.package_info
        })

    # 设置包裹状态，基于任务状态
    if task.completion_status == "Completed":
        package_status = "已完成"
    elif task.completion_status == "In Progress":
        package_status = "配送中"
    else:
        package_status = "待处理"

    # 返回状态信息
    return jsonify({
        'package_status': package_status,
        'package_id': package.package_id,
        'recipient_name': package.recipient_name,
        'recipient_address': package.recipient_address,
        'package_info': package.package_info
    })


@bp.route('/cancel_package/<int:package_id>')
@login_required
def cancel_package(package_id):
    package = Package.query.get_or_404(package_id)
    if package.status == 'Pending':  # 确保只有待处理状态的包裹可以被取消
        db.session.delete(package)
        db.session.commit()
    return redirect(url_for('user.dashboard'))


@bp.route('/update_info', methods=['POST'])
@login_required
def update_info():
    try:
        # 获取表单数据
        contact_info = request.form.get('contact')
        address = request.form.get('address')

        # 更新用户信息
        if contact_info:
            current_user.contact_info = contact_info
        db.session.commit()

        return redirect(url_for('user.dashboard'))
    except Exception as e:
        print(f"Error updating user info: {e}")
        return "修改失败，请稍后重试", 500


@bp.route('/update_credentials', methods=['POST'])
@login_required
def update_credentials():
    try:
        # 获取表单数据
        new_password = request.form.get('password')
        if not new_password:
            return "密码不能为空", 400

        # 更新密码（假设有 `set_password` 方法来加密密码）
        current_user.password = new_password
        db.session.commit()

        return redirect(url_for('user.dashboard'))
    except Exception as e:
        print(f"Error updating credentials: {e}")
        return "修改失败，请稍后重试", 500


@bp.route('/profile', methods=['GET'])
@login_required
def profile():
    try:
        # 构造返回的数据
        profile_data = {
            "username": current_user.username,
            "contact_info": current_user.contact_info,
            # 出于安全考虑，不返回明文密码
            "password": "******"
        }
        return jsonify(profile_data)
    except Exception as e:
        print(f"Error fetching user profile: {e}")
        return jsonify({"error": "无法加载用户信息"}), 500
