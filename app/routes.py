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
            SELECT Name AS Name, FORMAT(Area, 'N1') AS Area FROM continent
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

# Delete a continent
@routes.route('/continent/delete/<name>', methods=['POST'])
def delete_continent(name):
    # Get a connection to the database
    conn = create_connection()
    
    # Check if the connection was successful
    if conn:
        cursor = conn.cursor()
        try:
            # Delete the continent from the database
            cursor.execute('DELETE FROM continent WHERE Name = ?', (name,))
            conn.commit()  # Commit the transaction
            
            # Redirect to the continent list with a success message
            flash('Continent deleted successfully!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
        finally:
            cursor.close()
            conn.close()  # Ensure the connection is closed
    else:
        flash('Error: Unable to connect to the database.', 'danger')
    
    return redirect(url_for('routes.continents'))

# Update a continent
@routes.route('/continent/update/<name>', methods=['GET', 'POST'])
def update_continent(name):
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # Decode the name if it's URL-encoded
            name = name.replace('%20', ' ')  # Handle spaces, if needed

            if request.method == 'POST':
                # Get updated data from the form
                new_name = request.form['name']
                area = request.form['area']

                # Update the continent in the database
                cursor.execute('UPDATE continent SET Name = ?, Area = ? WHERE Name = ?', (new_name, area, name))
                conn.commit()

                flash('Continent updated successfully!', 'success')
                return redirect(url_for('routes.continents'))

            # For GET request, fetch current data to pre-fill the form
            cursor.execute('SELECT Name, Area FROM continent WHERE Name = ?', (name,))
            continent = cursor.fetchone()
            if not continent:
                flash('Continent not found!', 'danger')
                return redirect(url_for('routes.continents'))

            # Pass the current data to the form
            return render_template('update_continent.html', continent={'name': continent[0], 'area': continent[1]})
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
        finally:
            cursor.close()
            conn.close()
    else:
        flash('Error: Unable to connect to the database.', 'danger')
        return redirect(url_for('routes.continents'))

