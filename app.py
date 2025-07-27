from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import bcrypt

app = Flask(__name__)
app.secret_key = "your-secret-key"

def get_db_connection():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

# صفحة البداية (تسجيل الدخول)
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user and bcrypt.checkpw(password.encode(), user["password"]):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect("/dashboard")
        else:
            return "❌ اسم المستخدم أو كلمة المرور غير صحيحة"

    return render_template("login.html")

# تسجيل مستخدم جديد
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
            conn.commit()
        except sqlite3.IntegrityError:
            return "❌ اسم المستخدم مستخدم بالفعل"
        finally:
            conn.close()

        return redirect("/")
    return render_template("register.html")

# لوحة تحكم العامل
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user_id" not in session:
        return redirect("/")

    conn = get_db_connection()

    if request.method == "POST":
        date = request.form["date"]
        project = request.form["project"]
        task_type = request.form["task_type"]
        hours_worked = float(request.form["hours_worked"])
        hourly_rate = float(request.form["hourly_rate"])
        leave_remaining = float(request.form["leave_remaining"])

        conn.execute("""
            INSERT INTO work_logs 
            (user_id, date, project, task_type, hours_worked, hourly_rate, leave_remaining)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            session["user_id"], date, project, task_type,
            hours_worked, hourly_rate, leave_remaining
        ))
        conn.commit()

    logs = conn.execute("""
        SELECT * FROM work_logs WHERE user_id = ?
        ORDER BY date DESC
    """, (session["user_id"],)).fetchall()

    conn.close()
    return render_template("worker_dashboard.html", logs=logs)

# تسجيل الخروج
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
