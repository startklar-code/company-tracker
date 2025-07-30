import sqlite3

conn = sqlite3.connect('users.db')
c = conn.cursor()

# حذف الجداول إذا موجودة
c.execute('DROP TABLE IF EXISTS users')
c.execute('DROP TABLE IF EXISTS workers')
c.execute('DROP TABLE IF EXISTS projects')
c.execute('DROP TABLE IF EXISTS salaries')
c.execute('DROP TABLE IF EXISTS stores')
c.execute('DROP TABLE IF EXISTS store_logs')

# إنشاء الجداول من جديد
c.execute('''
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'worker'))
)
''')

c.execute('''
CREATE TABLE workers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    project_name TEXT,
    work_date TEXT,
    hours_worked REAL,
    hourly_rate REAL,
    vacation_days INTEGER,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
''')

c.execute('''
CREATE TABLE salaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    worker_id INTEGER,
    month INTEGER,
    year INTEGER,
    total_hours REAL,
    hourly_rate REAL,
    remaining_vacation INTEGER,
    salary REAL,
    FOREIGN KEY(worker_id) REFERENCES workers(id)
)
''')



c.execute('''
    CREATE TABLE IF NOT EXISTS stores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        unit TEXT,
        price REAL,
        last_updated TEXT
    )
    ''')

c.execute('''
    CREATE TABLE IF NOT EXISTS store_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_name TEXT NOT NULL,
        operation_type TEXT CHECK(operation_type IN ('in', 'out')) NOT NULL,
        quantity INTEGER NOT NULL,
        unit TEXT NOT NULL,
        price REAL NOT NULL,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')

c.execute('''
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    original_price REAL,
    raw_material_cost REAL,
    start_date TEXT,
    end_date TEXT,
    VorbreitGrundputz REAL,
    Grundputz REAL,
    vorbreitWeissputz REAL,
    WeissputzDecke REAL,
    WeeissputzWand REAL,
    GipserAbrieb REAL,
    Constration REAL,
    Peplanken REAL,
    Nitz REAL,
    FassadaAbrieb REAL,
    Abtiecken REAL,
    Strichen REAL
)
''')


conn.commit()
conn.close()
print("✅ تم إنشاء قاعدة البيانات بنجاح.")
