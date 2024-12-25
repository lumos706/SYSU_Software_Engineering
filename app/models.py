from app import db
from flask_login import UserMixin

class Admin(db.Model, UserMixin):
    admin_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    login_credentials = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<Admin {self.name}>"

    def get_id(self):
        return self.admin_id

class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    contact_info = db.Column(db.String(255))
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"

    def get_id(self):
        return self.user_id

class Pilot(db.Model, UserMixin):
    pilot_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_info = db.Column(db.String(255))
    login_credentials = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<Pilot {self.name}>"

    def get_id(self):
        return self.pilot_id

class Drone(db.Model):
    drone_id = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20))
    max_load_capacity = db.Column(db.Float)
    location = db.Column(db.String(255))
    battery_level = db.Column(db.Float)

class DeliveryTask(db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    drone_id = db.Column(db.Integer, db.ForeignKey('drone.id'))
    start_time = db.Column(db.DateTime)
    completion_status = db.Column(db.String(50))


class Package(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipient_name = db.Column(db.String(100), nullable=False)
    recipient_address = db.Column(db.String(255), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    delivery_task_id = db.Column(db.Integer, db.ForeignKey('delivery_task.id'))


class DroneHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    drone_id = db.Column(db.Integer, db.ForeignKey('drone.id'))
    timestamp = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(255))
