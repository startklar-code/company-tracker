import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# جدول المستخدمين
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password BLOB NOT NULL
)
""")

# جدول سجلات العمل
cursor.execute("""
CREATE TABLE IF NOT EXISTS work_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT NOT NULL,
    date TEXT NOT NULL,
    project TEXT NOT NULL,
    work_type TEXT NOT NULL,
    hours REAL NOT NULL,
    hourly_rate REAL NOT NULL,
    FOREIGN KEY(user) REFERENCES users(username)
)
""")

# جدول رصيد الإجازة
cursor.execute("""
CREATE TABLE IF NOT EXISTS vacation_balance (
    user TEXT PRIMARY KEY,
    total_days INTEGER NOT NULL DEFAULT 30,
    used_days INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY(user) REFERENCES users(username)
)
""")

# إضافة مدير افتراضي (كلمة المرور لاحقًا مشفرة)
cursor.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", ("admin", b"1234"))

# رصيد الإجازات للمدير (اختياري)
cursor.execute("INSERT OR IGNORE INTO vacation_balance (user) VALUES (?)", ("admin",))

conn.commit()
conn.close()

print("✅ قاعدة البيانات جاهزة.")
