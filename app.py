import sqlite3

conn = sqlite3.connect('database.db')
conn.execute("PRAGMA foreign_keys = ON")
cursor = conn.cursor()


cursor.execute('''CREATE TABLE IF NOT EXISTS Clients (
        client_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT,
        phone TEXT)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Employees (
 employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
 name TEXT NOT NULL,
 speciality TEXT)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Services (
service_id INTEGER PRIMARY KEY AUTOINCREMENT,
service_name TEXT NOT NULL,
duration_minutes INTEGER NOT NULL,
price REAL NOT NULL)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Appointments (
    appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    employee_id INTEGER NOT NULL,
    service_id INTEGER NOT NULL,
    appointment_date TEXT NOT NULL,
    appointment_time TEXT NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY(client_id) REFERENCES Clients(client_id),
    FOREIGN KEY(employee_id) REFERENCES Employees(employee_id),
    FOREIGN KEY(service_id) REFERENCES Services(service_id))''')

cursor.execute('CREATE INDEX IF NOT EXISTS idx_appointments_date ON Appointments(appointment_date)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_appointments_employee ON Appointments(employee_id)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_appointments_service ON Appointments(service_id)')


client_count = cursor.execute('SELECT COUNT(*) FROM Clients').fetchone()[0]
employee_count = cursor.execute('SELECT COUNT(*) FROM Employees').fetchone()[0]
service_count = cursor.execute('SELECT COUNT(*) FROM Services').fetchone()[0]

if client_count == 0:
    cursor.execute("INSERT INTO Clients (name, email, phone) VALUES ('Alice Johnson', 'alice@example.com', '111-222-3333')")
    cursor.execute("INSERT INTO Clients (name, email,phone) VALUES ('Bob Smith','bob@example.com', '444-555-6666')")
    cursor.execute("INSERT INTO Clients (name, email,phone) VALUES ('Charlie Brown','charlie@example.com', '777-888-9999')")

if employee_count == 0:
    cursor.execute("INSERT INTO Employees (name, speciality) VALUES ('Emma Davis','Hair Stylist')")
    cursor.execute("INSERT INTO Employees (name, speciality) VALUES ('James Lee','Nail Technician')")
    cursor.execute("INSERT INTO Employees (name, speciality) VALUES ('Sophia Turner','Massage Therapist')")

if service_count == 0:
    cursor.execute("INSERT INTO Services (service_name, duration_minutes, price) VALUES ('Haircut', 30, 25.00)")
    cursor.execute("INSERT INTO Services (service_name, duration_minutes, price) VALUES ('Manicure', 45, 35.00)")
    cursor.execute("INSERT INTO Services (service_name, duration_minutes, price) VALUES ('Massage', 60, 60.00)")

conn.commit()
conn.close()

print("Database created successfully.")
