from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt
import hashlib
import pandas as pd
import sqlite3
import os


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session management

# Get the base directory of the current script
basedir = os.path.abspath(os.path.dirname(__file__))

# Construct the database path dynamically
db_path = os.path.join(basedir, 'db', 'titanic.sqlite')

@app.route('/ai')
def index():
    return render_template('index.html')

@app.route('/submit_code', methods=['POST'])
def submit_code():
    code = request.form.get('code')  # Get the submitted code
    result = execute_code(code)  # Run the code and get the result
    # Prepare the response
    response = {"student_code": code, "result": result}
    return render_template('index.html', code=code, response=response)


def execute_code(code):
    try:
        exec_globals = {}
        exec(code, exec_globals)  # Execute the user's code
        return exec_globals.get('result', 'Code executed successfully!')
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    app.run(debug=True)


@app.route('/second')
def hello_world():
    return render_template('index.html')

@app.route('/form', methods=['GET', 'POST'])
def render_form():
    message = ''

    if request.method == 'POST':
        text = request.form.get('text')
        if request.form['submit_button'] == 'Lowercase':
            message = text.lower()
        elif request.form['submit_button'] == 'Capital':
            message = text.upper()
        elif request.form['submit_button'] == 'Byamba':
            message = "Hi Byamba"
    return render_template('form.html', message=message)

@app.route('/')
def about():

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Fetch all posts from the database
    cursor.execute("SELECT * FROM me")
    me = cursor.fetchall()
    conn.close()

    # Format posts for rendering
    myInfo = [{"id": row[0], "name": row[1], "age": row[2], "hobby":row[3], "project":row[4]} for row in me]
    name = myInfo[len(myInfo)-1]["name"]
    age = str(myInfo[len(myInfo)-1]["age"])
    hobby = myInfo[len(myInfo)-1]["hobby"]
    project = myInfo[len(myInfo)-1]["project"]

    title = name
    hobbies = hobby
    desc = hobby
    work = project
    des2 = "Grace is a " + age + "-year-old sophomore at Stevenson High School with a strong passion for both creativity and technology. She loves fashion, photography, and food, and she’s on track to combine these interests with her aspirations to major in computer science and economics. Skilled in Java and Python, and currently working with SQL, HTML, and other web development languages, Grace brings technical expertise to her projects. Her Mongolian heritage adds a rich layer to her appreciation for diverse cultures, especially when it comes to trying new cuisines. With math as her favorite subject, she thrives in analytical challenges, setting her on an exciting path toward a multifaceted future."
    print(title, me, desc)
    return render_template('about.html',
                            my_title = title,
                            my_hobby = hobbies,
                            my_des = desc,
                            my_work = work,
                            my_des2 = des2
                            )

@app.route('/posts', methods=['GET', 'POST'])
def submit_post():
    message = ""
    if request.method == 'POST':
        title = request.form['title']
        post_content = request.form['post']
        post_type = request.form['type']
        conn = sqlite3.connect('titanic.sqlite')
        cursor = conn.cursor()
        # Ensure the post table exists (you might want to modify or remove this part)
        cursor.execute('''CREATE TABLE IF NOT EXISTS post (id INTEGER PRIMARY KEY, title TEXT, post TEXT, type TEXT)''')
        # Insert the submitted form data into the post table
        cursor.execute("INSERT INTO post (title, post, type) VALUES (?, ?, ?)", (title, post_content, post_type))
        conn.commit()
        conn.close()
        message = "Post submitted successfully!"

    return render_template('form.html', message=message)


@app.route('/blog')
def show_blogs():
    conn = sqlite3.connect('titanic.sqlite')
    cursor = conn.cursor()
    # Fetch all posts from the database
    cursor.execute("SELECT title, post, type FROM post")
    posts = cursor.fetchall()
    conn.close()

    # Format posts for rendering
    formatted_posts = [{"title": row[0], "content": row[1], "type": row[2]} for row in posts]

    return render_template('blog.html', posts=formatted_posts)


# Route for registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            flash("Registration successful! Please log in.")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Username already exists. Please try another one.")
        finally:
            conn.close()

    return render_template('register.html')

@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    # Retrieve form data
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    # Insert data into the contacts table
    conn = sqlite3.connect(db_path , check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO contacts (name, email, message)
        VALUES (?, ?, ?)
    ''', (name, email, message))
    conn.commit()
    conn.close()

    # Redirect to the admin page
    return redirect('/admin')

# Route to display admin page
@app.route('/admin')
def admin():
    # Retrieve all contact records
    conn = sqlite3.connect(db_path, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM contacts')
    contacts = cursor.fetchall()
    conn.close()

    # Render the admin page with contact data
    return render_template('admin.html', contacts=contacts)

# Route for login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['username'] = username
            flash("Login successful!")
            return redirect(url_for('show_blogs'))
        else:
            flash("Invalid username or password.")

    return render_template('login.html')

# Route to log out
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("Logged out successfully.")
    return redirect(url_for('login'))


@app.route('/pokemon')
def pokemon_display():

    return render_template('pokemon.html')

if __name__ == '__main__':
    app.run(debug=True)