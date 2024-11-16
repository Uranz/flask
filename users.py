# Run this code once to set up the users table
import sqlite3
import hashlib

conn = sqlite3.connect('db/titanic.sqlite')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS me
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    age INTEGER,
                    hobby TEXT,
                    project TEXT)''')
print("execution done")

name_insert = "Grance"
age_insert = 15
hobby_insert = "my hobby"
project_insert = "my project"

# Insert the submitted form data into the me table
cursor.execute("INSERT INTO me (name, age, hobby, project) VALUES (?, ?, ?, ?)", (name_insert, age_insert, hobby_insert, project_insert))



# Create the contacts table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS contacts (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT  NOT NULL,
                    message TEXT NOT NULL,
                    current_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

conn.commit()
conn.close()