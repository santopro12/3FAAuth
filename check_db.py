import sqlite3

DATABASE = 'database.db'

def check_database():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    if not users:
        print("No users found in the database.")
    else:
        print("Users found in the database:")
        for user in users:
            print(f"Username: {user[0]}, Password Hash: {user[1]}, Images: {user[2]}")

    conn.close()

if __name__ == '__main__':
    check_database()