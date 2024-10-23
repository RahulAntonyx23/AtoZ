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
def login_professional():
    if request.method == 'POST':
        name = request.form['username']
        password = request.form['password']  # Keep it as plaintext

        print(f"Attempting to log in with Username: {name} and Password: {password}")  # Debugging
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM professionals WHERE name = ? AND password = ?', (name, password))
        professional = cursor.fetchone()
        conn.close()

        if professional:
            return redirect(url_for('pro_dashboard', professional_id=professional['id']))
        else:
            flash('Invalid credentials. Please try again.')

    return render_template('pro_login.html')

@app.route('/signup-pro', methods=['GET', 'POST'])
def signup_professional():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM services')
    services = cursor.fetchall()
    conn.close()

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        service_type = request.form['service_type']
        experience = request.form['experience']
        password = request.form['password']  # Collecting the password

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO professionals (name, description, service_type, experience, password) 
                          VALUES (?, ?, ?, ?, ?)''',
                       (name, description, service_type, experience, password))
        conn.commit()
        conn.close()

        flash('Professional added successfully!')
        return redirect(url_for('login_professional'))

    return render_template('pro_signin.html', services=services)



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

@app.route('/pro_dashboard')
def pro_dashboard():
    professional_id = request.args.get('professional_id')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM professionals WHERE id = ?', (professional_id,))
    professional = cursor.fetchone()
    cursor.execute('SELECT * FROM services WHERE name = ?', (professional['service_type'],))
    service = cursor.fetchone()
    conn.close()
    
    return render_template('pro_dashboard.html', professional=professional, service=service)



#serivces admin
@app.route('/add-service', methods=['GET', 'POST'])
def add_service():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        time_required = request.form['time_required']
        description = request.form['description']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO services (name, price, time_required, description) VALUES (?, ?, ?, ?)',
                       (name, price, time_required, description))
        conn.commit()
        conn.close()

        flash('Service added successfully!')
        return redirect(url_for('add_service'))

    return render_template('add_service.html')

@app.route('/services')
def view_services():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM services')
    services = cursor.fetchall()
    conn.close()
    return render_template('view_services.html', services=services)



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
