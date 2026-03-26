-- DB
CREATE DATABASE IF NOT EXISTS bus_scheduler
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE bus_scheduler;

-- users & profile
CREATE TABLE IF NOT EXISTS users (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  username    VARCHAR(50) UNIQUE NOT NULL,
  password    VARCHAR(100) NOT NULL,
  name        VARCHAR(50) NOT NULL,
  created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_profiles (
  user_id   INT PRIMARY KEY,
  age       INT NULL,
  bio       VARCHAR(255) NULL,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- favorites
CREATE TABLE IF NOT EXISTS favorite_stops (
  id        INT AUTO_INCREMENT PRIMARY KEY,
  user_id   INT NOT NULL,
  stop_id   VARCHAR(50) NOT NULL,
  stop_name VARCHAR(100) NOT NULL,
  UNIQUE KEY uk_user_stop(user_id, stop_id),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS favorite_routes (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  user_id    INT NOT NULL,
  route_no   VARCHAR(20) NOT NULL,
  UNIQUE KEY uk_user_route(user_id, route_no),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- schedules (일정)
CREATE TABLE IF NOT EXISTS schedules (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  user_id      INT NOT NULL,
  title        VARCHAR(100) NOT NULL,
  description  TEXT,
  start_time   DATETIME NOT NULL,
  end_time     DATETIME NOT NULL,
  route_no     VARCHAR(20) NULL,     -- (선택) 연결할 버스 노선
  stop_id      VARCHAR(50) NULL,     -- (선택) 연결할 정류장
  recur_rule   VARCHAR(50) NULL,     -- ex) "WEEKLY:MON,WED,FRI@09:00"
  alert_min    INT DEFAULT 0,        -- 시작 전 알람 분
  created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- attachments (간단)
CREATE TABLE IF NOT EXISTS schedule_files (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  schedule_id INT NOT NULL,
  file_name   VARCHAR(200) NOT NULL,
  mime_type   VARCHAR(100) NOT NULL,
  bytes       LONGBLOB NOT NULL,
  FOREIGN KEY (schedule_id) REFERENCES schedules(id) ON DELETE CASCADE
);

-- 관리자/모니터링
CREATE TABLE IF NOT EXISTS app_events (
  id         BIGINT AUTO_INCREMENT PRIMARY KEY,
  level      ENUM('INFO','WARN','ERROR') DEFAULT 'INFO',
  message    VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
