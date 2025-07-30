import sqlite3

conn = sqlite3.connect('users.db')
c = conn.cursor()

username = 'admin'
password = 'admin123'  # لاحقًا سنضع تشفير
role = 'admin'

try:
    c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
    conn.commit()
    print("✅ تم إضافة المدير بنجاح.")
except sqlite3.IntegrityError:
    print("⚠️ اسم المستخدم موجود مسبقًا.")
finally:
    conn.close()
