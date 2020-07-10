
import cs50
import csv

# Create database by opening and closing an empty file first
open("bluefrog.db", "w").close()
db = cs50.SQL("sqlite:///bluefrog.db")

# Create tables
db.execute("CREATE TABLE places (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, title TEXT NOT NULL, dest_id INTEGER NOT NULL, url TEXT, email TEXT, phone TEXT, description TEXT, public BOOLEAN, 'timestamp' TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL, FOREIGN KEY(dest_id) REFERENCES destinations(id))")

db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, name TEXT NOT NULL, email TEXT NOT NULL, hash TEXT NOT NULL)")

db.execute("CREATE TABLE visitors (user_id INT, place_id INT, FOREIGN KEY(user_id) REFERENCES users(id), FOREIGN KEY(place_id) REFERENCES places(id))")

db.execute("CREATE TABLE authors (user_id INT, place_id INT, FOREIGN KEY(user_id) REFERENCES users(id), FOREIGN KEY(place_id) REFERENCES places(id))")

db.execute("CREATE TABLE category (place_id INT, category TEXT NOT NULL, FOREIGN KEY(place_id) REFERENCES places(id))")

db.execute("CREATE TABLE destinations (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, destination TEXT NOT NULL)")
