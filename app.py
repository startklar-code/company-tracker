from flask import Flask, render_template, request, redirect, session
import sqlite3
import bcrypt

app = Flask(__name__)
app.secret_key = "your-secret-key"  # سر الجلسة

# الاتصال بقاعدة البيانات
def get_db_connection():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

# الصفحة الرئيسية (تسجيل الدخول)
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user["password"]):
            session["username"] = username
            return redirect("/dashboard")
        else:
            return "❌ اسم المستخدم أو كلمة المرور خاطئة."

    return render_template("login.html")

# صفحة التسجيل
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        existing = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

        if existing:
            conn.close()
            return "⚠️ هذا الاسم مستخدم بالفعل."

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
        conn.commit()
        conn.close()

        return "✅ تم التسجيل بنجاح! <a href='/'>تسجيل الدخول</a>"

    return render_template("register.html")

# لوحة المستخدم
@app.route("/dashboard")
def dashboard():
    if "username" in session:
        return render_template("dashboard.html")
    return redirect("/")


# عرض المستخدمين (للمشرف فقط)
@app.route("/users")
def show_users():
    if "username" not in session:
        return redirect("/")

    if session["username"] != "admin":
        return "🚫 الوصول مرفوض. هذه الصفحة للمشرف فقط."

    conn = get_db_connection()
    users = conn.execute("SELECT username FROM users").fetchall()
    conn.close()

    user_list = "<ul>"
    for u in users:
        user_list += f"<li>{u['username']}</li>"
    user_list += "</ul>"

    return f"<h2>📋 قائمة المستخدمين:</h2>{user_list}<br><a href='/dashboard'>⬅️ العودة</a>"

# تسجيل الخروج
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# تشغيل السيرفر
if __name__ == "__main__":
    app.run(debug=True)
