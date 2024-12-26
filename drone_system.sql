-- 创建Pilot表
CREATE TABLE Pilot (
    pilot_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    contact_info VARCHAR(255),
    login_credentials VARCHAR(255) UNIQUE,
    password VARCHAR(255) NOT NULL
);

-- 创建Drone表
CREATE TABLE Drone (
    drone_id INT AUTO_INCREMENT PRIMARY KEY,
    model VARCHAR(50),
    status VARCHAR(20),
    max_load_capacity DECIMAL(10, 2),
    location VARCHAR(255),
    battery_level DECIMAL(5, 2),
    manufacture_date VARCHAR(100),
    pilot_id INT,
    FOREIGN KEY (pilot_id) REFERENCES Pilot(pilot_id) ON UPDATE CASCADE
);

-- 创建DeliveryTask表
CREATE TABLE DeliveryTask (
    task_id INT AUTO_INCREMENT PRIMARY KEY,
    drone_id INT,
    start_time VARCHAR(100),
    completion_status VARCHAR(50),
    FOREIGN KEY (drone_id) REFERENCES Drone(drone_id) ON UPDATE CASCADE
);

-- 创建User表
CREATE TABLE User (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE,
    contact_info VARCHAR(255),
    password VARCHAR(255) NOT NULL
);

-- 创建Package表
CREATE TABLE Package (
    package_id INT AUTO_INCREMENT PRIMARY KEY,
    recipient_name VARCHAR(100),
    recipient_address VARCHAR(255),
    package_info TEXT,
    task_id INT,
    user_id INT,
    FOREIGN KEY (task_id) REFERENCES DeliveryTask(task_id) ON UPDATE CASCADE,
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON UPDATE CASCADE
);

-- 创建DroneHistory表
CREATE TABLE DroneHistory (
    history_id INT AUTO_INCREMENT PRIMARY KEY,
    drone_id INT,
    timestamp VARCHAR(100),
    location VARCHAR(255),
    FOREIGN KEY (drone_id) REFERENCES Drone(drone_id) ON UPDATE CASCADE
);

-- 创建Admin表
CREATE TABLE Admin (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    login_credentials VARCHAR(255) UNIQUE,
    password VARCHAR(255) NOT NULL
);

-- 创建索引
CREATE INDEX idx_recipient_address ON Package(recipient_address);
CREATE INDEX idx_task_id_user_id ON Package(task_id, user_id);
CREATE INDEX idx_status_max_load ON Drone(status, max_load_capacity);
CREATE INDEX idx_location_battery ON Drone(location, battery_level);
CREATE INDEX idx_drone_id ON DeliveryTask(drone_id);
CREATE INDEX idx_pilot_contact ON Pilot(contact_info);
CREATE INDEX idx_drone_history_timestamp ON DroneHistory(timestamp);
CREATE INDEX idx_user_username ON User(username);
CREATE INDEX idx_admin_credentials ON Admin(login_credentials);