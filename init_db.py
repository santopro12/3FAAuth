import sqlite3
conn= sqlite3.connect('database.db')
conn.execute('Create table if not Exists user (username Text, step1 Text,step2 Text, step3 Text) ')
conn.close()