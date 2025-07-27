DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS work_logs;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);

CREATE TABLE work_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    date TEXT NOT NULL,
    project TEXT NOT NULL,
    task_type TEXT NOT NULL,
    hours_worked REAL NOT NULL,
    hourly_rate REAL NOT NULL,
    leave_remaining REAL NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
