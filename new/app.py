from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flashing messages

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('your_database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Home route
@app.route('/')
def home():
    return render_template('base.html')

@app.route('/login-admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  # Keep it as plaintext
        
        print(f"Attempting to log in with Username: {username} and Password: {password}")  # Debugging

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM admins WHERE username = ? AND password = ?', (username, password))
        admin = cursor.fetchone()
        conn.close()

        if admin:
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials. Please try again.')

    return render_template('admin_login.html')


@app.route('/login-pro', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  # Keep it as plaintext
        
        print(f"Attempting to log in with Username: {username} and Password: {password}")  # Debugging

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM professionals WHERE username = ? AND password = ?', (username, password))
        admin = cursor.fetchone()
        conn.close()

        if admin:
            return redirect(url_for('pro_dashboard'))
        else:
            flash('Invalid credentials. Please try again.')

    return render_template('pro_login.html')





@app.route('/login-customer', methods=['GET', 'POST'])
def login_customer():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  # Keep it as plaintext
        
        print(f"Attempting to log in with Username: {username} and Password: {password}")  # Debugging

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM customers WHERE name = ? AND password = ?', (username, password))
        customer = cursor.fetchone()
        conn.close()

        if customer:
            # return render_template('login.html')
            return redirect(url_for('dashboard'))
            # return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials. Please try again.')
    return render_template('customer_login.html')


# Sign up route
@app.route('/signup-customer', methods=['GET', 'POST'])
def signup_customer():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO customers (name, email, password) VALUES (?, ?, ?)', (name, email, password))
            conn.commit()
            flash('Sign up successful! You can log in now.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already registered. Please use a different email.')
        finally:
            conn.close()

    return render_template('customer_signup.html')



# Admin dashboard route
@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin-dash.html')

# Admin dashboard route
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/test-db')
def test_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM sqlite_master WHERE type="table";')
    tables = cursor.fetchall()
    conn.close()
    return f'Tables in the database: {tables}'

if __name__ == '__main__':
    app.run(debug=True)
