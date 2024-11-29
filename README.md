# Author 


# Technologies Used
- Flask
- Jinja Templates
- SQLite

# Features
- Login / Signup functionality for customers and professional service providers
- Admin can view manager all users
- Customer can post a service request for a specific service request
- Service Professional can view open service request tickets and take them up
- On service completion, user can leave review of service 

# Architecture
- app.py - contains the backend flask code that makes all api's available to use
- requirements.txt - contains a list of necessary packages for this code to work 
- db.txt - contains inital schema of the databse
- setup_database.py - can be used to create a new copy of the database with all blank tables if db doesnt already exist

- templates folder - contains rendering html code for all user & admin pages
    following folders contain that user type specific rendering pages
  - admin 
  - customer
  - professional 
    common / reused files & logic like login / signup pages are present in the root of this folder

# Created API to perform the following functions
- Create a new user supporting different types
- Login user 
- Display dashboards for each type of user with varying pages
- Create a service by the admin
- Raise service request by user and view requests
- Take service request + Complete / Cancel Service Requests
- View booking status
- Leave review 
- Admin API functions can view users and delete them

# Table ERD Diagram
![ERD Diagram](new\erd.png)

# Running this project
Create a new virtual env and activate the same (Optional)
0. Navigate into the `code` folder
1. Install all dependencies from 'requirements.txt' -> run `pip install -r requirements.txt`
2. Run the setup_database.py file to create a database if it doesnt exist (app_database.db) ->  python `setup_database.py`
3. run `app.py`-> python `app.py`
4. Visit `http://127.0.0.1:5000` to see the code live