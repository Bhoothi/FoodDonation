import sqlite3

import sqlite3

# Connect to the SQLite database (or create it if it doesn't exist)
import sqlite3

from sqlalchemy.engine import cursor

conn = sqlite3.connect(r"C:\Users\bhoot\downloads\bhootharaju\mydatabase.db")


# Create a new table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS donation (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    food_type TEXT,
                    quantity REAL,
                    donor_name	TEXT,
                    date TEXT)''')

# Insert a donation record
cursor.execute("INSERT INTO donation (user_id, food_type, quantity, date) VALUES (?, ?, ?, ?)",
               (1, 'Pasta', 2.5, '2024-12-05'))
conn.commit()

# Retrieve and display all donations
cursor.execute("SELECT * FROM donation")
donations = cursor.fetchall()
for donation in donations:
    print(donation)

# Close the connection
conn.close()
