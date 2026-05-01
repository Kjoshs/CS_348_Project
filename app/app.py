from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app=Flask(__name__)


def  get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/appointments')
def appointments():
    conn = get_db_connection()
    appointments = conn.execute('''
        SELECT A.appointment_id,
                C.name AS client_name,
                E.name AS employee_name,
                S.service_name,
                A.appointment_date,
                A.appointment_time,
                A.status
        FROM Appointments A
        JOIN Clients C ON A.client_id = C.client_id
        JOIN Employees E ON A.employee_id = E.employee_id
        JOIN Services S ON A.service_id = S.service_id
        ORDER BY A.appointment_date, A.appointment_time
        ''').fetchall()
    conn.close()
    return render_template('appointments.html', appointments=appointments)

@app.route('/add_appointment', methods=['GET', 'POST'])
def add_appointment():
    conn = get_db_connection()

    clients = conn.execute('SELECT * FROM Clients ORDER BY name').fetchall()
    employees = conn.execute('SELECT * FROM Employees ORDER BY name').fetchall()
    services = conn.execute('SELECT * FROM Services ORDER BY service_name').fetchall()

    if request.method == 'POST':
        client_id = request.form['client_id']
        employee_id = request.form['employee_id']
        service_id = request.form['service_id']
        appointment_date = request.form['appointment_date']
        appointment_time = request.form['appointment_time']
        status = request.form['status']

        conn.execute('''
                INSERT INTO Appointments (client_id, employee_id, service_id, appointment_date, appointment_time, status)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (client_id, employee_id, service_id, appointment_date, appointment_time, status))

        conn.commit()
        conn.close()
        return redirect(url_for('appointments'))

    conn.close()
    return render_template(
        'add_appointment.html',
        clients=clients,
        employees=employees,
        services=services,
    )

@app.route('/edit_appointment/<int:id>', methods=['GET', 'POST'])
def edit_appointment(id):
    conn = get_db_connection()

    appointment = conn.execute(
      'SELECT * FROM Appointments WHERE appointment_id = ?', (id,)
    ).fetchone()

    if appointment is None:
        conn.close()
        return "Appointment not found."

    clients = conn.execute('SELECT * FROM Clients ORDER BY name').fetchall()
    employees = conn.execute('SELECT * FROM Employees ORDER BY name').fetchall()
    services = conn.execute('SELECT * FROM Services ORDER BY service_name').fetchall()

    if request.method == 'POST':
        client_id = request.form['client_id']
        employee_id = request.form['employee_id']
        service_id = request.form['service_id']
        appointment_date = request.form['appointment_date']
        appointment_time = request.form['appointment_time']
        status = request.form['status']

        conn.execute('''
        UPDATE Appointments
        SET client_id = ?, employee_id = ?, service_id = ?,
        appointment_date = ?, appointment_time = ?, status = ?
        WHERE appointment_id = ?
        ''', (client_id, employee_id, service_id, appointment_date, appointment_time, status, id))

        conn.commit()
        conn.close()
        return redirect(url_for('appointments'))

    conn.close()
    return render_template(
        'edit_appointment.html',
        appointment=appointment,
        clients=clients,
        employees=employees,
        services=services,
    )

@app.route('/delete_appointment/<int:id>', methods=['POST'])
def delete_appointment(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM Appointments WHERE appointment_id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('appointments'))

@app.route('/report', methods=['GET', 'POST'])
def report():
    conn = get_db_connection()

    employees = conn.execute('SELECT * FROM Employees ORDER BY name').fetchall()
    services = conn.execute('SELECT * FROM Services ORDER BY service_name').fetchall()

    results = []
    stats = None

    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        employee_id = request.form['employee_id']
        service_id = request.form['service_id']
        status = request.form['status']

        query = '''
            SELECT A.appointment_id,
            C.name AS client_name,
            E.name AS employee_name,
            S.service_name,
            S.duration_minutes,
            S.price,
            A.appointment_date,
            A.appointment_time,
            A.status
            FROM Appointments A
            JOIN Clients C ON A.client_id = C.client_id
            JOIN Employees E ON A.employee_id = E.employee_id
            JOIN Services S ON A.service_id = S.service_id
            WHERE A.appointment_date BETWEEN ? AND ?
            '''

        params = [start_date, end_date]

        if employee_id != '':
            query += ' AND A.employee_id = ?'
            params.append(employee_id)
        if service_id != '':
            query += ' AND A.service_id = ?'
            params.append(service_id)
        if status != '':
            query += ' AND A.status = ?'
            params.append(status)

        query += ' ORDER BY A.appointment_date, A.appointment_time'

        results = conn.execute(query, params).fetchall()

        stats_query = '''
            SELECT COUNT(*) AS total_appointments,
                    AVG(S.duration_minutes) AS avg_duration,
                    AVG(S.price) AS avg_price
            FROM Appointments A
            JOIN Services S ON A.service_id = S.service_id
            WHERE A.appointment_date BETWEEN ? AND ?
            '''

        stats_params = [start_date, end_date]

        if employee_id != '':
            stats_query += ' AND A.employee_id = ?'
            stats_params.append(employee_id)

        if service_id != '':
            stats_query += ' AND A.service_id = ?'
            stats_params.append(service_id)

        if status != '':
            stats_query += ' AND A.status = ?'
            stats_params.append(status)

        stats = conn.execute(stats_query, stats_params).fetchone()

    conn.close()
    return render_template(
        'report.html',
        employees=employees,
        services=services,
        results=results,
        stats=stats,
    )

if __name__ == '__main__':
    app.run(debug=True)
