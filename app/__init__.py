from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import pymysql
from sqlalchemy import text

db = SQLAlchemy()
login_manager = LoginManager()

# noinspection SqlNoDataSourceInspection
def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    DB_URI = 'mysql+pymysql://root:123456@localhost:3306/drone_system'
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = '123456'

    db.app = app
    db.init_app(app)
    migrate = Migrate(app, db)
    # sql = text('SELECT * FROM user')
    # with app.app_context():  # 确保在应用上下文中执行
    #     result = db.session.execute(sql)
    # print(result.fetchall())
    # 初始化 LoginManager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.role_select'  # 设置登录视图

    # 用户加载回调函数
    @login_manager.user_loader
    def load_user(user_id):
        user_type = session.get('user_type')
        if user_type == 'user':
            return User.query.get(int(user_id))
        elif user_type == 'pilot':
            return Pilot.query.get(int(user_id))
        elif user_type == 'admin':
            return Admin.query.get(int(user_id))
        return None
    # 注册蓝图
    from app.routes import admin, user, pilot, auth
    from app.models import User, Pilot, Admin
    app.register_blueprint(auth.bp)  # 移除 url_prefix
    app.register_blueprint(admin.bp, url_prefix='/admin')
    app.register_blueprint(user.bp, url_prefix='/user')
    app.register_blueprint(pilot.bp, url_prefix='/pilot')
    return app


