-- جدول المستخدمين (إدارة + عمال)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'worker'))
);

-- جدول سجلات العمال
CREATE TABLE IF NOT EXISTS work_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    worker_id INTEGER NOT NULL,
    work_date TEXT NOT NULL,
    work_hours REAL,
    wage REAL,
    notes TEXT,
    FOREIGN KEY (worker_id) REFERENCES users(id)
);

-- جدول الرواتب الظاهرة في صفحة الإدارة
CREATE TABLE IF NOT EXISTS salaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    worker_id INTEGER NOT NULL,
    total_hours REAL,
    total_wage REAL,
    period TEXT,
    FOREIGN KEY (worker_id) REFERENCES users(id)
);

-- جدول المشاريع
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
);
-- جدول المخازن الأساسي
CREATE TABLE IF NOT EXISTS stores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    unit TEXT NOT NULL,
    price REAL NOT NULL,
    current_stock INTEGER DEFAULT 0,
    last_updated TEXT DEFAULT CURRENT_TIMESTAMP
);

-- سجل العمليات في المخازن
CREATE TABLE IF NOT EXISTS store_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT NOT NULL,
    operation_type TEXT CHECK(operation_type IN ('in', 'out')) NOT NULL,
    quantity INTEGER NOT NULL,
    unit TEXT NOT NULL,
    price REAL NOT NULL,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    start_date TEXT,
    end_date TEXT
);




