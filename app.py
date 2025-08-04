from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import base64
import qrcode
from io import BytesIO
import secrets 
import random

app = Flask(__name__)
app.secret_key = 'your_super_secret_key'  # Replace with your own secret key

DATABASE = 'database.db'

# ---------------------------
# 🔹 Helper: DB Connection
# ---------------------------
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ---------------------------
# 🔹 Initialize DB (users table)
# ---------------------------
def init_db():
    if not os.path.exists(DATABASE):
        conn = get_db_connection()
        conn.execute('''CREATE TABLE users (
                            username TEXT PRIMARY KEY,
                            password TEXT NOT NULL,
                            images TEXT NOT NULL
                        )''')
        conn.commit()
        conn.close()

init_db()

# ---------------------------
# 🔹 Route: Home (Redirect to login)
# ---------------------------
@app.route('/')
def home():
    return render_template('home.html')

# ---------------------------
# 🔹 Route: Register
# ---------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        selected_images = request.form.getlist('selected_images')
        
        if len(selected_images) != 3:
            flash('Please select exactly 3 images.')
            return redirect(url_for('register'))
        print("username:",username)
        print("password:",password)
        print("selected Images:",selected_images)      
        image_string = ','.join(selected_images)

        conn = get_db_connection()
        existing = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if existing:
            flash("Username already exists", "warning")
            return redirect(url_for('register'))
        conn.execute("INSERT INTO users (username, password, images) VALUES (?, ?, ?)",
                     (username, password, image_string))
        conn.commit()
        conn.close()
        flash("Registered successfully. Please login.", "success")
        return redirect(url_for('registration_successful'))

    return render_template('register.html')

# In app.py
# ---------------------------
# 🔹 Route: Registration Successful
# ---------------------------
@app.route('/registration_successful')
def registration_successful():
    return render_template('registration_successful.html')
# ---------------------------
# 🔹 Route: Login (Step 1)
# ---------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['username'] = username
            session['registered_images'] = user['images'].split(',')
            session['authenticated'] = False
            return redirect(url_for('image_auth'))
        else:
            flash("Invalid username or password", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')

# @app.route('/image-auth', methods=['GET', 'POST'])
# def image_auth():
#     # 💡 FIX: Ensure user has passed the password login step
#     if 'username' not in session or 'registered_images' not in session:
#         flash("Please log in first.", "info")
#         return redirect(url_for('login'))

#     if request.method == 'POST':
#         # 💡 FIX: The form data should be 'selected_images', not 'images'
#         selected = request.form.getlist('selected_images')
        
#         # Get the registered images from the session
#         registered_images = session.get('registered_images')
        
#         if sorted(selected) == sorted(registered_images):
#             session['authenticated'] = True
#             return redirect(url_for('captcha_auth')) # Redirect to the next step
#         else:
#             flash("Incorrect images selected. Try again.", "danger")
#             # 💡 FIX: Render the template again with a fresh set of images
#             all_images = [f'img{i}.jpg' for i in range(1, 10)]
#             random.shuffle(all_images)
#             return render_template('image_auth.html', images=all_images)
            
#     # For a GET request, shuffle images to present them in a random order
#     all_images = [f'img{i}.jpg' for i in range(1, 10)]
#     random.shuffle(all_images)
#     return render_template('image_auth.html', images=all_images)


# ---------------------------
# 🔹 Route: Image Authentication (Step 2) - CORRECTED for QR
# ---------------------------
@app.route('/image-auth', methods=['GET', 'POST'])
def image_auth():
    # Ensure user has passed the password login step
    if 'username' not in session or 'registered_images' not in session:
        flash("Please log in first.", "info")
        return redirect(url_for('login'))

    if request.method == 'POST':
        selected = request.form.getlist('selected_images')
        registered_images = session.get('registered_images')
        
        if sorted(selected) == sorted(registered_images):
            # 💡 FIX: Generate a unique token for QR authentication
            qr_token = secrets.token_urlsafe(16)
            session['qr_token'] = qr_token
            # 💡 FIX: Redirect to the new QR code page
            return redirect(url_for('qr_auth'))
        else:
            flash("Incorrect images selected. Try again.", "danger")
            # For a failed attempt, we need to show the image selection again.
            # We'll get a fresh, random set of images.
            all_images = [f'img{i}.jpg' for i in range(1, 10)]
            random.shuffle(all_images)
            return render_template('image_auth.html', images=all_images)
            
    # For a GET request, shuffle images to present them in a random order
    all_images = [f'img{i}.jpg' for i in range(1, 10)]
    random.shuffle(all_images)
    return render_template('image_auth.html', images=all_images)






# # ---------------------------
# # 🔹 Route: CAPTCHA Authentication (Step 3)
# # ---------------------------
# @app.route('/captcha-auth', methods=['GET', 'POST'])
# def captcha_auth():
#     if 'username' not in session or not session.get('authenticated'):
#         return redirect(url_for('login'))

#     if request.method == 'GET':
#         a = random.randint(1, 10)
#         b = random.randint(1, 10)
#         session['captcha'] = a + b
#         return render_template('captcha_auth.html', a=a, b=b)

#     if request.method == 'POST':
#         answer = request.form['captcha']
#         try:
#             if int(answer) == session.get('captcha'):
#                 return render_template('success.html', username=session['username'])
#             else:
#                 flash("Incorrect CAPTCHA. Try again.", "danger")
#                 return redirect(url_for('captcha_auth'))
#         except:
#             flash("Invalid input", "danger")
#             return redirect(url_for('captcha_auth'))

# ---------------------------
# 🔹 Route: QR Authentication (Step 3) - NEW
# ---------------------------
@app.route('/qr-auth', methods=['GET', 'POST'])
def qr_auth():
    # Check if the user has an active session and token
    if 'username' not in session or 'qr_token' not in session:
        flash("Please complete the previous steps.", "info")
        return redirect(url_for('login'))

    if request.method == 'GET':
        # Generate the QR code as an image
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        
        # 💡 The QR code payload is a URL that the user's phone will visit
        # We need to make this URL publicly accessible
        # Example: 'http://<your-public-ip-or-domain>/verify-qr?token=<the-token>'
        # For local testing, you can use a local IP or a service like ngrok
        # base_url = 'http://192.168.43.113' # Change this for deployment
        base_url = 'https://visualauth.onrender.com' # Change this for deployment
        qr_data = f"{base_url}/verify-qr?token={session['qr_token']}"
        
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # Save the image to a buffer and encode it for the HTML template
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        qr_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        return render_template('qr_auth.html', qr_image=qr_image)

# ---------------------------
# 🔹 Route: Verify QR (Final Step) - NEW
# ---------------------------
@app.route('/verify-qr', methods=['GET'])
def verify_qr():
    token_from_phone = request.args.get('token')
    
    # Check if the token from the phone matches the session's token
    if token_from_phone and token_from_phone == session.get('qr_token'):
        # Token is correct! Authenticate the user.
        session['authenticated'] = True
        
        # 💡 Optional: Clear the QR token from the session to prevent re-use
        session.pop('qr_token', None)
        
        return "Authentication Successful! You can now close this window on your phone and go back to your computer."
    else:
        return "Authentication Failed. Please try again."



# ---------------------------
# 🔹 Route: Logout
# ---------------------------
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

# ---------------------------
# 🔹 Run App
# ---------------------------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0',port=5000)
