from flask import Blueprint, render_template, redirect, url_for, request, flash
from connect import create_connection

# Create a blueprint for modular routing
routes = Blueprint('routes', __name__)

# Redirect the root URL to the home page
@routes.route('/')
def index():
    return redirect(url_for('routes.home'))

# Display the home page
@routes.route('/home')
def home():
    return render_template('home.html')

# Display the list of top 10 countries 
# @routes.route('/country')
# def country():
#     # Get a connection to the database
#     conn = create_connection()
    
#     # Check if the connection was successful
#     if conn:
#         # Create a cursor from the connection
#         cursor = conn.cursor()
        
#         # Execute a query
#         cursor.execute('SELECT TOP 10 Code, Name, Capital, FORMAT(Population, \'N0\') AS Population, FORMAT(Area, \'N0\') AS Area FROM Country')
        
#         # Fetch the results
#         countries = cursor.fetchall()
        
#         # Close the cursor and connection
#         cursor.close()
#         conn.close()
        
#         # Pass the results to the template
#         return render_template('country.html', countries=countries)
#     else:
#         return render_template('country.html', countries=None)

# Display the list of countries with pagination
@routes.route('/country')
def country():
    # Get the current page number from the query string (default to page 1)
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of items per page
    
    # Calculate the starting row for the query (offset)
    offset = (page - 1) * per_page
    
    # Get a connection to the database
    conn = create_connection()
    
    if conn:
        # Create a cursor from the connection
        cursor = conn.cursor()
        
        # Execute a query with pagination using OFFSET and FETCH NEXT
        cursor.execute('''
            SELECT Code, Name, Capital, FORMAT(Population, 'N0') AS Population, FORMAT(Area, 'N0') AS Area
            FROM Country
            ORDER BY Name  -- or any other column for sorting
            OFFSET ? ROWS
            FETCH NEXT ? ROWS ONLY
        ''', (offset, per_page))
        
        # Fetch the results
        countries = cursor.fetchall()
        
        # Get the total count of rows to calculate the number of pages
        cursor.execute('SELECT COUNT(*) FROM Country')
        total_count = cursor.fetchone()[0]
        
        # Close the cursor and connection
        cursor.close()
        conn.close()
        
        # Calculate total number of pages
        total_pages = (total_count + per_page - 1) // per_page
        
        # Pass the results, total pages, and current page to the template
        return render_template('country.html', countries=countries, total_pages=total_pages, current_page=page)
    else:
        return render_template('country.html', countries=None)

# Display the list of continents
@routes.route('/continent')
def continents():
    # Get a connection to the database
    conn = create_connection()
    
    # Check if the connection was successful
    if conn:
        # Create a cursor from the connection
        cursor = conn.cursor()
        
        # Execute a query
        cursor.execute('''
            SELECT Name AS Continent, FORMAT(Area, 'N1') AS Area FROM continent
        ''')
        
        # Fetch the results
        continents = cursor.fetchall()
        
        # Close the cursor and connection
        cursor.close()
        conn.close()
        
        # Pass the results to the template
        return render_template('continent.html', continents=continents)
    else:
        return render_template('continent.html', continents=None)

# Display the form to create a new continent
@routes.route('/continent/create', methods=['GET', 'POST'])
def create_continent():
    # Handle the form submission when the method is POST
    if request.method == 'POST':
        continent_name = request.form['name']
        continent_area = request.form['area']
        
        # Get a connection to the database
        conn = create_connection()
        
        # Check if the connection was successful
        if conn:
            cursor = conn.cursor()
            try:
                # Insert the new continent into the database
                cursor.execute('INSERT INTO continent (Name, Area) VALUES (?, ?)', (continent_name, continent_area))
                conn.commit()  # Commit the transaction
                
                # Redirect to the continent list with a success message
                flash('Continent added successfully!', 'success')
                return redirect(url_for('routes.continents'))
            except Exception as e:
                flash(f'Error: {str(e)}', 'danger')  # Flash error message
            finally:
                cursor.close()
                conn.close()
        
        flash('Failed to connect to the database', 'danger')  # Error if connection failed

    # Render the form for GET request
    return render_template('create_continent.html')

