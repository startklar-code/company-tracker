from flask import Flask, render_template, request, redirect, url_for, session, jsonify


import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# الصفحة الرئيسية — تسجيل دخول وتسجيل جديد
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        form_type = request.form.get('form_type')

        if form_type == 'login':
            username = request.form['username']
            password = request.form['password']
            role = request.form['role']

            conn = get_db_connection()
            user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ? AND role = ?', 
                                (username, password, role)).fetchone()
            conn.close()

            if user:
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']
                return redirect(url_for('worker_dashboard') if role == 'worker' else url_for('admin_dashboard'))
            else:
                return render_template('login.html', error="بيانات الدخول غير صحيحة")

        elif form_type == 'register':
            username = request.form['new_username']
            password = request.form['new_password']
            role = request.form['new_role']

            conn = get_db_connection()
            try:
                conn.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', 
                             (username, password, role))
                conn.commit()
                conn.close()
                return render_template('login.html', success="تم إنشاء الحساب بنجاح. يمكنك تسجيل الدخول الآن.")
            except sqlite3.IntegrityError:
                conn.close()
                return render_template('login.html', error="اسم المستخدم مستخدم بالفعل.")
    
    return render_template('login.html')

@app.route('/worker')
def worker_dashboard():
    if 'role' in session and session['role'] == 'worker':
        conn = get_db_connection()
        records = conn.execute('SELECT * FROM workers WHERE user_id = ?', (session['user_id'],)).fetchall()
        conn.close()
        return render_template('worker_dashboard.html', records=records, username=session['username'])
    return redirect(url_for('login'))


@app.route('/admin_dashboard')
def admin_dashboard():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    salaries = conn.execute('''
        SELECT s.id, u.username, w.project_name, s.month, s.year,
               s.total_hours, s.hourly_rate, s.remaining_vacation, s.salary
        FROM salaries s
        JOIN workers w ON s.worker_id = w.id
        JOIN users u ON w.user_id = u.id
        ORDER BY s.year DESC, s.month DESC
    ''').fetchall()
    conn.close()
    
    return render_template('admin_dashboard.html', salaries=salaries)


@app.route('/add_work', methods=['POST'])
def add_work():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    project_name = request.form['project_name']
    work_date = request.form['work_date']
    hours_worked = float(request.form['hours_worked'])
    hourly_rate = float(request.form['hourly_rate'])
    vacation_days = int(request.form['vacation_days'])

    conn = get_db_connection()
    c = conn.cursor()

    # إضافة بيانات العمل
    c.execute('''
        INSERT INTO workers (user_id, project_name, work_date, hours_worked, hourly_rate, vacation_days)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, project_name, work_date, hours_worked, hourly_rate, vacation_days))

    # حساب الراتب
    month = datetime.strptime(work_date, "%Y-%m-%d").month
    year = datetime.strptime(work_date, "%Y-%m-%d").year
    salary = hours_worked * hourly_rate

    c.execute('''
        INSERT INTO salaries (worker_id, month, year, total_hours, hourly_rate, remaining_vacation, salary)
        VALUES ((SELECT id FROM workers WHERE user_id=? ORDER BY id DESC LIMIT 1),
                ?, ?, ?, ?, ?, ?)
    ''', (user_id, month, year, hours_worked, hourly_rate, vacation_days, salary))

    conn.commit()
    conn.close()

    return redirect(url_for('worker_dashboard'))
@app.route('/edit_work/<int:work_id>', methods=['GET', 'POST'])
def edit_work(work_id):
    if 'role' not in session or session['role'] != 'worker':
        return redirect(url_for('login'))

    conn = get_db_connection()
    if request.method == 'POST':
        conn.execute('''
            UPDATE workers
            SET project_name = ?, work_date = ?, hours_worked = ?, hourly_rate = ?, vacation_days = ?
            WHERE id = ? AND user_id = ?
        ''', (
            request.form['project_name'],
            request.form['work_date'],
            float(request.form['hours_worked']),
            float(request.form['hourly_rate']),
            int(request.form['vacation_days']),
            work_id,
            session['user_id']
        ))
        conn.commit()
        conn.close()
        return redirect(url_for('worker_dashboard'))

    work = conn.execute('SELECT * FROM workers WHERE id = ? AND user_id = ?', (work_id, session['user_id'])).fetchone()
    conn.close()
    if work is None:
        return "السجل غير موجود", 404

    return render_template('edit_work.html', work=work)

@app.route('/delete_work/<int:work_id>')
def delete_work(work_id):
    if 'role' not in session or session['role'] != 'worker':
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM workers WHERE id = ? AND user_id = ?', (work_id, session['user_id']))
    conn.commit()
    conn.close()
    return redirect(url_for('worker_dashboard'))

from datetime import datetime

# صفحة عرض المخزون
@app.route('/stores', methods=['GET', 'POST'])
def stores():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    if request.method == 'POST':
        item_name = request.form['item_name']
        quantity = int(request.form['quantity'])
        unit = request.form['unit']
        price = float(request.form['price'])
        operation_type = request.form['operation_type']
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if operation_type == 'in':
            # إذا كان موجود من قبل، زود الكمية
            c.execute("SELECT * FROM stores WHERE item_name = ?", (item_name,))
            row = c.fetchone()
            if row:
                new_qty = row['quantity'] + quantity
                c.execute("UPDATE stores SET quantity = ?, unit = ?, price = ?, last_updated = ? WHERE item_name = ?",
                          (new_qty, unit, price, now, item_name))
            else:
                c.execute("INSERT INTO stores (item_name, quantity, unit, price, last_updated) VALUES (?, ?, ?, ?, ?)",
                          (item_name, quantity, unit, price, now))
        elif operation_type == 'out':
            # خصم الكمية
            c.execute("SELECT * FROM stores WHERE item_name = ?", (item_name,))
            row = c.fetchone()
            if row and row['quantity'] >= quantity:
                new_qty = row['quantity'] - quantity
                c.execute("UPDATE stores SET quantity = ?, last_updated = ? WHERE item_name = ?",
                          (new_qty, now, item_name))
            else:
                conn.close()
                return "❌ كمية غير كافية أو المادة غير موجودة"

        # حفظ في سجل العمليات
        c.execute("""
            INSERT INTO store_logs (item_name, operation_type, quantity, unit, price, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (item_name, operation_type, quantity, unit, price, now))



        conn.commit()

    # استرجاع البيانات لعرضها
    c.execute("SELECT * FROM stores")
    stock = c.fetchall()

    c.execute("SELECT * FROM store_logs ORDER BY timestamp DESC")
    logs = c.fetchall()

    conn.close()
    return render_template('stores.html', stock=stock, logs=logs)


# تقليل المخزون
@app.route('/use_store/<int:item_id>', methods=['POST'])
def use_store(item_id):
    quantity = int(request.form['quantity'])
    now = datetime.now().strftime('%Y-%m-%d')

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # تحديث الكمية إن كانت كافية
    c.execute('SELECT quantity FROM stores WHERE id = ?', (item_id,))
    item = c.fetchone()
    if item and item[0] >= quantity:
        c.execute('UPDATE stores SET quantity = quantity - ?, last_updated = ? WHERE id = ?', (quantity, now, item_id))
        conn.commit()

    conn.close()
    return redirect(url_for('stores'))

@app.route('/projects', methods=['GET', 'POST'])
def projects():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        c.execute('''
            INSERT INTO projects (name, description, start_date, end_date)
            VALUES (?, ?, ?, ?)
        ''', (name, description, start_date, end_date))

        conn.commit()

    c.execute('SELECT * FROM projects ORDER BY start_date DESC')
    all_projects = c.fetchall()
    conn.close()
    return render_template('projects.html', projects=all_projects)

@app.route('/api/projects')
def get_projects():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM projects')
    rows = c.fetchall()
    conn.close()

    projects = []
    for row in rows:
        duration = f"{row['start_date']} → {row['end_date']}"
        
        total_hours = sum([
            row['VorbreitGrundputz'] or 0,
            row['Grundputz'] or 0,
            row['vorbreitWeissputz'] or 0,
            row['WeissputzDecke'] or 0,
            row['WeeissputzWand'] or 0,
            row['GipserAbrieb'] or 0,
            row['Constration'] or 0,
            row['Peplanken'] or 0,
            row['Nitz'] or 0,
            row['FassadaAbrieb'] or 0,
            row['Abtiecken'] or 0,
            row['Strichen'] or 0
        ])

        original_price = row['original_price'] or 0
        raw_material = row['raw_material_cost'] or 0
        hourly_rate = 50  # ← يمكنك تغييره لاحقاً أو إدخاله من المستخدم
        
        work_cost = total_hours * hourly_rate
        total_cost = work_cost + raw_material
        profit = original_price - total_cost

        projects.append({
            'id': row['id'],
            'name': row['name'],
            'original_price': original_price,
            'raw_material_cost': raw_material,
            'start_date': row['start_date'],
            'end_date': row['end_date'],
            'VorbreitGrundputz': row['VorbreitGrundputz'] or 0,
            'Grundputz': row['Grundputz'] or 0,
            'vorbreitWeissputz': row['vorbreitWeissputz'] or 0,
            'WeissputzDecke': row['WeissputzDecke'] or 0,
            'WeeissputzWand': row['WeeissputzWand'] or 0,
            'GipserAbrieb': row['GipserAbrieb'] or 0,
            'Constration': row['Constration'] or 0,
            'Peplanken': row['Peplanken'] or 0,
            'Nitz': row['Nitz'] or 0,
            'FassadaAbrieb': row['FassadaAbrieb'] or 0,
            'Abtiecken': row['Abtiecken'] or 0,
            'Strichen': row['Strichen'] or 0,
            'total_worker_hours': total_hours,
            'hourly_rate': hourly_rate,
            'work_cost': work_cost,
            'total_cost': total_cost,
            'profit': profit,
            'duration': duration
        })

    return jsonify(projects)

@app.route('/api/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('DELETE FROM projects WHERE id = ?', (project_id,))
    conn.commit()
    conn.close()
    return '', 204


@app.route('/api/projects', methods=['POST'])
def api_add_project():
    data = request.get_json()

    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO projects (
            name, original_price, raw_material_cost, start_date, end_date,
            VorbreitGrundputz, Grundputz, vorbreitWeissputz, WeissputzDecke,
            WeeissputzWand, GipserAbrieb, Constration, Peplanken,
            Nitz, FassadaAbrieb, Abtiecken, Strichen
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('name'),
        data.get('originalPrice'),
        data.get('rawMaterialCost'),
        data.get('startDate'),
        data.get('endDate'),
        data.get('VorbreitGrundputz'),
        data.get('Grundputz'),
        data.get('vorbreitWeissputz'),
        data.get('WeissputzDecke'),
        data.get('WeeissputzWand'),
        data.get('GipserAbrieb'),
        data.get('Constration'),
        data.get('Peplanken'),
        data.get('Nitz'),
        data.get('FassadaAbrieb'),
        data.get('Abtiecken'),
        data.get('Strichen')
    ))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'}), 201

@app.route('/api/projects/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    data = request.get_json()

    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        UPDATE projects SET
            name = ?, original_price = ?, raw_material_cost = ?, 
            start_date = ?, end_date = ?, VorbreitGrundputz = ?, 
            Grundputz = ?, vorbreitWeissputz = ?, WeissputzDecke = ?, 
            WeeissputzWand = ?, GipserAbrieb = ?, Constration = ?, 
            Peplanken = ?, Nitz = ?, FassadaAbrieb = ?, Abtiecken = ?, 
            Strichen = ?
        WHERE id = ?
    ''', (
        data.get('name'),
        data.get('originalPrice'),
        data.get('rawMaterialCost'),
        data.get('startDate'),
        data.get('endDate'),
        data.get('VorbreitGrundputz'),
        data.get('Grundputz'),
        data.get('vorbreitWeissputz'),
        data.get('WeissputzDecke'),
        data.get('WeeissputzWand'),
        data.get('GipserAbrieb'),
        data.get('Constration'),
        data.get('Peplanken'),
        data.get('Nitz'),
        data.get('FassadaAbrieb'),
        data.get('Abtiecken'),
        data.get('Strichen'),
        project_id
    ))
    conn.commit()
    conn.close()
    return jsonify({'status': 'updated'})






if __name__ == '__main__':
    app.run(debug=True)
