# Run this code once to set up the users table
import sqlite3
import hashlib

conn = sqlite3.connect('titanic.sqlite')
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


conn.commit()
conn.close()