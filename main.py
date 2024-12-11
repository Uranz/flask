from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
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

API_URL = 'https://random-word-api.herokuapp.com/word?number=1'  # Generates 1 random word

def get_random_word():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            return data[0].upper()
    except requests.RequestException as e:
        print(f"Error fetching word: {e}")
    return "PYTHON"  # Fallback word

@app.route('/hangman')
def hangman():
    if 'word' not in session:
        session['word'] = get_random_word()
        session['guesses'] = []
        session['misses'] = 0
        session['message'] = ''
    word_display = ''.join(
        letter if letter in session['guesses'] else '_' for letter in session['word']
    )
    return render_template(
        'hangman.html',
        word_display=word_display,
        guesses=session['guesses'],
        misses=session['misses'],
        message=session.get('message', ''),
        word=session['word'],
    )

@app.route('/reset')
def reset_hangman():
    session.pop('word', None)
    session.pop('guesses', None)
    session.pop('misses', None)
    session.pop('message', None)
    return redirect(url_for('hangman'))

@app.route('/guesses', methods=['POST'])
def guesses_hangman():
    guess = request.form['guess'].upper()
    if not guess.isalpha() or len(guess) != 1:
        session['message'] = "Invalid input! Please guess a single letter."
        return redirect(url_for('hangman'))

    if guess not in session['guesses']:
        session['guesses'].append(guess)
        if guess in session['word']:
            session['message'] = f"Good Guess! '{guess}' is in the word."
        else:
            session['misses'] += 1
            session['message'] = f"Sorry! '{guess}' is not in the word."
    else:
        session['message'] = f"You already guessed '{guess}'."
    return redirect(url_for('hangman'))




# Get the base directory of the current script
basedir = os.path.abspath(os.path.dirname(__file__))

# Construct the database path dynamically
db_path = os.path.join(basedir, 'db', 'titanic.sqlite')


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
    sprite_url = fetch_pokemon_sprite("pikachu")

    des2 = "Grace is a " + age + "-year-old sophomore at Stevenson High School with a strong passion for both creativity and technology. She loves fashion, photography, and food, and she’s on track to combine these interests with her aspirations to major in computer science and economics. Skilled in Java and Python, and currently working with SQL, HTML, and other web development languages, Grace brings technical expertise to her projects. Her Mongolian heritage adds a rich layer to her appreciation for diverse cultures, especially when it comes to trying new cuisines. With math as her favorite subject, she thrives in analytical challenges, setting her on an exciting path toward a multifaceted future."
    print(title, me, desc)
    return render_template('about.html',
                            my_title = title,
                            my_hobby = hobbies,
                            my_des = desc,
                            my_work = work,
                            my_des2 = des2,
                            sprite_url = sprite_url
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

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    conn = sqlite3.connect(db_path, check_same_thread=False)
    cursor = conn.cursor()
    
    # Fetch all table names in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    selected_table = None
    table_data = []
    table_columns = []
    
    if request.method == 'POST':
        # Get the selected table from the dropdown
        selected_table = request.form.get('table_name')
        if selected_table:
            # Fetch data and column names for the selected table
            cursor.execute(f"PRAGMA table_info({selected_table})")
            table_columns = [info[1] for info in cursor.fetchall()]
            
            cursor.execute(f"SELECT * FROM {selected_table}")
            table_data = cursor.fetchall()
    
    conn.close()
    
    # Render the admin page with table data
    return render_template(
        'admin.html', 
        tables=tables, 
        selected_table=selected_table, 
        table_data=table_data, 
        table_columns=table_columns
    )


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



# Fetch list of Pokémon names
def fetch_pokemon_names():
    url = "https://pokeapi.co/api/v2/pokemon?limit=1000"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return [pokemon['name'] for pokemon in data['results']]
    else:
        return []

# Fetch Pokémon sprite URL
def fetch_pokemon_sprite(pokemon_name):
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}"
    response = requests.get(url)
    if response.status_code == 200:
        raw_data = response.json()
        return raw_data['sprites']['front_default']
    else:
        return None

# Fetch list of Pokémon names
def fetch_pokemon_names():
    url = "https://pokeapi.co/api/v2/pokemon?limit=1000"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return [pokemon['name'] for pokemon in data['results']]
    else:
        return []

# Fetch Pokémon sprite URL
def fetch_pokemon_sprite(pokemon_name):
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}"
    response = requests.get(url)
    if response.status_code == 200:
        raw_data = response.json()
        return raw_data['sprites']['front_default']
    else:
        return None

@app.route("/pokemon", methods=["GET", "POST"])
def index():
    pokemon_names = fetch_pokemon_names()
    selected_pokemon = None
    sprite_url = None

    if request.method == "POST":
        selected_pokemon = request.form.get("pokemon_name")
        sprite_url = fetch_pokemon_sprite(selected_pokemon)

    return render_template(
        "pokemon.html",
        pokemon_names=pokemon_names,
        selected_pokemon=selected_pokemon,
        sprite_url=sprite_url,
    )

@app.route("/sprite/<pokemon_name>")
def sprite(pokemon_name):
    sprite_url = fetch_pokemon_sprite(pokemon_name)
    if sprite_url:
        response = requests.get(sprite_url)
        if response.status_code == 200:
            return Response(response.content, mimetype="image/png")
    return ["Sprite not found", 404]

@app.route("/calculator", methods=["GET", "POST"])
def calculator():
    result = None
    if request.method == "POST":
        try:
            num1 = float(request.form["num1"])
            num2 = float(request.form["num2"])
            operation = request.form["operation"]

            # Perform the calculation based on the operation
            if operation == "+":
                result = num1 + num2
            elif operation == "-":
                result = num1 - num2
            elif operation == "*":
                result = num1 * num2
            elif operation == "/":
                result = num1 / num2
            else:
                result = "Invalid operation"
        except ValueError:
            result = "Please enter valid numbers."

    return render_template("calculator.html", result=result)

if __name__ == '__main__':
    app.run(debug=True)