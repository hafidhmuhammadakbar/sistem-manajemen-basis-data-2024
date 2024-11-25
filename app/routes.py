from flask import Blueprint, render_template, redirect, url_for
from connect import create_connection

# Create a blueprint for modular routing
routes = Blueprint('routes', __name__)

@routes.route('/')
def index():
    return redirect(url_for('routes.home'))

@routes.route('/home')
def home():
    return render_template('home.html')

@routes.route('/country')
def country():
    # Get a connection to the database
    conn = create_connection()
    
    # Check if the connection was successful
    if conn:
        # Create a cursor from the connection
        cursor = conn.cursor()
        
        # Execute a query
        cursor.execute('SELECT TOP 10 Code, Name, Capital, FORMAT(Population, \'N0\') AS Population, FORMAT(Area, \'N0\') AS Area FROM Country')
        
        # Fetch the results
        countries = cursor.fetchall()
        
        # Close the cursor and connection
        cursor.close()
        conn.close()
        
        # Pass the results to the template
        return render_template('country.html', countries=countries)
    else:
        return render_template('country.html', countries=None)
    
@routes.route('/continent')
def continents():
    # Get a connection to the database
    conn = create_connection()
    
    # Check if the connection was successful
    if conn:
        # Create a cursor from the connection
        cursor = conn.cursor()
        
        # Execute a query
        cursor.execute('SELECT C.Name AS Continent, COUNT(DISTINCT E.Country) AS CountryCount FROM continent C JOIN encompasses E ON C.Name = e.Continent GROUP BY C.Name')
        
        # Fetch the results
        continents = cursor.fetchall()
        
        # Close the cursor and connection
        cursor.close()
        conn.close()
        
        # Pass the results to the template
        return render_template('continent.html', continents=continents)
    else:
        return render_template('continent.html', continents=None)