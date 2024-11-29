import sqlite3

# Connect to the SQLite database (it will create the file if it doesn't exist)
conn = sqlite3.connect('app_database.db')

# Create a cursor object
cursor = conn.cursor()

# Create tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    city TEXT
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS professionals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    service_type TEXT NOT NULL,
    experience INTEGER,
    status TEXT DEFAULT 'pending',
    password TEXT, 
    city TEXT
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    time_required TEXT,
    description TEXT
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS service_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_id INTEGER,
    customer_id INTEGER,
    professional_id INTEGER,
    date_of_request DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_of_completion DATETIME,
    service_status TEXT DEFAULT 'requested',
    remarks TEXT,
    service_rating INTEGER DEFAULT 0,
    FOREIGN KEY (service_id) REFERENCES services (id),
    FOREIGN KEY (customer_id) REFERENCES customers (id),
    FOREIGN KEY (professional_id) REFERENCES professionals (id)
);
''')

# Commit the changes and close the connection
conn.commit()
conn.close()
