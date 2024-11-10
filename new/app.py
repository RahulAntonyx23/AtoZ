
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.secret_key = 'your_secret_key'
Bootstrap(app)
  

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
            return redirect(url_for('login_customer'))
        except sqlite3.IntegrityError:
            flash('Email already registered. Please use a different email.')
        finally:
            conn.close()

    return render_template('customer_signup.html')



# Admin dashboard route
@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin/admin-dash.html')

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

@app.route('/view_requests/<int:customer_id>')
def view_requests(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch all service requests for the given customer_id
    cursor.execute('''
        SELECT sr.id, sr.service_id, s.name as service_name, sr.customer_id, sr.service_status as status, sr.service_rating as rating, p.name as professional_name
        FROM service_requests sr
        JOIN services s ON sr.service_id = s.id
        LEFT JOIN professionals p ON sr.professional_id = p.id
        WHERE sr.customer_id = ?
    ''', (customer_id,))
    requests = cursor.fetchall()
    
    print("DEBUG: Requests fetched -", requests)  # Debugging line
    
    requests_list = [dict(request) for request in requests]
    print("DEBUG: Requests fetched -", requests_list)  # Debugging line
    
    conn.close()
    return render_template('customer/view_requests.html', requests=requests)

@app.route('/review/<int:request_id>', methods=['GET'])
def review(request_id):
    print(f"Review ID: {request_id}")
    conn = get_db_connection()
    cursor = conn.cursor()
    print(f"Executing query: SELECT * FROM service_requests WHERE id = {request_id}")
    cursor.execute('SELECT * FROM service_requests WHERE id = ?', (request_id,))
    request_data = cursor.fetchone()
    
    # Convert to dictionary for easier readability?
    request_data_dict = dict(request_data) if request_data else None
    print(f"Request Data: {request_data_dict}")  # Debugging line
    
    conn.close()

    if request_data is None:
        return "Request not found", 404

    return render_template('review.html', title="Review", request=request_data_dict)


@app.route('/submit_review/<int:request_id>', methods=['POST'])
def submit_review(request_id):
    rating = int(request.form.get('new_rating'))
    review_text = request.form.get('review_text')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT customer_id FROM service_requests where id =?', (request_id,))
    customer_id = cursor.fetchone()[0]
    cursor.execute('''UPDATE service_requests 
                   SET service_rating = ?, remarks = ?
                   WHERE id = ?''', (rating, review_text, request_id))
    conn.commit()
    conn.close()
    return redirect(url_for('view_requests', customer_id=customer_id))



@app.route('/view_request_pro/<string:service_type>/<int:pro_id>')
def view_request_pro(service_type, pro_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch all service requests for the given service type
    cursor.execute('''
        SELECT sr.id, sr.service_id, s.name as service_name, sr.service_status 
        FROM service_requests sr 
        JOIN services s ON sr.service_id = s.id 
        WHERE s.name = ?
    ''', (service_type,))
    requests = cursor.fetchall()
    
    conn.close()

    return render_template('professional/view_request_pro.html', requests=requests, pro_id=pro_id)



@app.route('/take_request/<int:request_id>/<int:pro_id>', methods=['POST'])
def take_request(request_id, pro_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Update the service request with the professional's ID and change status
    cursor.execute('UPDATE service_requests SET professional_id = ?, service_status = "In Progress" WHERE id = ?', (pro_id, request_id))
    cursor.execute('SELECT s.name as service_type FROM service_requests sr JOIN services s ON sr.service_id = s.id WHERE sr.id = ?', (request_id,))
    service_type = cursor.fetchone()['service_type']
    conn.commit()
    conn.close()
    
    # Redirect back to the view requests page
    return redirect(url_for('view_request_pro', service_type=service_type, pro_id=pro_id))  # Replace with actual service type



@app.route('/complete_request/<int:request_id>/<int:pro_id>', methods=['POST'])
def complete_request(request_id, pro_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Update the service request status to "Completed"
    cursor.execute('UPDATE service_requests SET service_status = "Completed" WHERE id = ?', (request_id,))
    
    # Fetch the service type for the request
    cursor.execute('SELECT s.name as service_type FROM service_requests sr JOIN services s ON sr.service_id = s.id WHERE sr.id = ?', (request_id,))
    service_type = cursor.fetchone()['service_type']
    
    conn.commit()
    conn.close()
    
    # Redirect back to the view requests page with service type and professional ID
    return redirect(url_for('view_request_pro', service_type=service_type, pro_id=pro_id))



@app.route('/pro_dashboard')
def pro_dashboard():
    professional_id = request.args.get('professional_id')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch professional details
    cursor.execute('SELECT * FROM professionals WHERE id = ?', (professional_id,))
    professional = cursor.fetchone()
    
    # Fetch service details based on the professional's service type
    cursor.execute('SELECT * FROM services WHERE name = ?', (professional['service_type'],))
    service = cursor.fetchone()
    
    conn.close()
    
    return render_template('professional/pro_dashboard.html', professional=professional, service=service)




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
        return redirect(url_for('admin/add_service'))

    return render_template('admin/add_service.html')

@app.route('/professionals', methods=['GET', 'POST'])
def view_professionals():
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        professional_id = request.form['professional_id']
        cursor.execute('UPDATE professionals SET status = "approved" WHERE id = ?', (professional_id,))
        conn.commit()
    
    cursor.execute('SELECT * FROM professionals')
    professionals = cursor.fetchall()
    conn.close()
    return render_template('admin/view_professionals.html', professionals=professionals)

@app.route('/view-people', methods=['GET', 'POST'])
def view_people():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        person_type = request.form['person_type']
        person_id = request.form['person_id']
        if person_type == 'customer':
            cursor.execute('DELETE FROM customers WHERE id = ?', (person_id,))
        elif person_type == 'professional':
            cursor.execute('DELETE FROM professionals WHERE id = ?', (person_id,))
        conn.commit()
    
    cursor.execute('SELECT * FROM customers')
    customers = cursor.fetchall()
    cursor.execute('SELECT * FROM professionals')
    professionals = cursor.fetchall()
    conn.close()
    return render_template('admin/view_people.html', customers=customers, professionals=professionals)



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
