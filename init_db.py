import sqlite3

with open("schema.sql", "r", encoding="utf-8") as f:
    schema = f.read()

conn = sqlite3.connect("users.db")
conn.executescript(schema)
conn.commit()
conn.close()

print("✅ قاعدة البيانات جاهزة.")
