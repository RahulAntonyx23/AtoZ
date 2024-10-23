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
            return redirect(url_for('dashboard', customer_id=customer['id']))
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
    customer_id = request.args.get('customer_id')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM customers WHERE id = ?', (customer_id))
    customer = cursor.fetchone()
    conn.close()

    return render_template('dashboard.html', customer=customer)

@app.route('/place_service_request', methods=['GET', 'POST'])
def place_service_request():
    if request.method == 'GET':
        customer_id = request.args.get('customer_id')
        print("CUSTOMER_ID is " + customer_id)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, name FROM services')
        services = cursor.fetchall()
        conn.close()

        return render_template('customer/place_service_request_order.html',customer_id=customer_id, services=services)

    if request.method == 'POST':
        customer_id = request.form['customer_id']
        service_id = request.form['service_id']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO service_requests (service_id, customer_id) VALUES (?,?)', (service_id, customer_id))
        conn.commit()
            # Get the last inserted ID
        id = cursor.lastrowid  # Assuming request_id is the primary key of the service_requests table
        conn.close()
    
        flash('Request Submitted Successfully!')
    
    # Redirect to a new page to show booking details
        return redirect(url_for('view_booking', request_id=id))
    
@app.route('/view_booking/<int:request_id>')
def view_booking(request_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch the booking details using request_id
    cursor.execute('SELECT sr.id, sr.service_id, sr.customer_id, s.name FROM service_requests sr JOIN services s ON sr.service_id = s.id WHERE sr.id = ?', (request_id,))
    booking_details = cursor.fetchone()
    
    conn.close()

    if booking_details:
        # Create a dictionary or similar structure for easier access
        booking_info = {
            'request_id': booking_details[0],
            'service_id': booking_details[1],
            'customer_id': booking_details[2],
            'service_name': booking_details[3]
        }
        return render_template('customer/booking_details.html', booking=booking_info)
    else:
        flash('Booking not found.')
        return redirect(url_for('dashboard'))  # Redirect to a safe page if not found


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
