import sqlite3

conn = sqlite3.connect("blog.db")
conn.execute("ALTER TABLE users ADD COLUMN image_file VARCHAR")
conn.commit()
conn.close()