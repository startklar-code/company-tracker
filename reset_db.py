import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# حذف الجداول القديمة إذا كانت موجودة
cursor.executescript("""
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS work_logs;

-- إنشاء الجداول من جديد
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password BLOB NOT NULL,
    role TEXT NOT NULL
);

CREATE TABLE work_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    project TEXT,
    task_type TEXT,
    hours_worked REAL,
    hourly_rate REAL,
    leave_remaining REAL,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
""")

conn.commit()
conn.close()

print("✅ تم مسح البيانات القديمة وإنشاء قاعدة البيانات من جديد.")
