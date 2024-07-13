from flask import Flask, request, render_template, redirect, flash, url_for
import sqlite3
from flask_login import UserMixin, login_user, login_required, current_user, logout_user, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask_mail import Mail, Message
import os
import socket
import re


app = Flask(__name__)

app.secret_key = 'your_secret_key'


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'vishakcode@gmail.com'
app.config['MAIL_PASSWORD'] = 'sivv orgt jgjh gzxb'
#app.config['MAIL_PASSWORD'] = 'getonthefloor'
mail = Mail(app)
serializer = URLSafeTimedSerializer(app.secret_key)

# Initialize SQLite database
def init_sqlite_db():
    connect = sqlite3.connect('mytest.db')
    connect.execute('CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT, password TEXT)')
    connect.close()

init_sqlite_db()

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Specifies the endpoint to redirect to for login

# User class
class User(UserMixin):
    def __init__(self, id, name, email, password):
        self.id = id
        self.name = name
        self.email = email
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    connect = sqlite3.connect('mytest.db')
    cursor = connect.execute('SELECT * FROM user WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    connect.close()
    if user:
        return User(user[0], user[1], user[2], user[3])
    return None

@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == 'POST':
        name = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        
        connect = sqlite3.connect('mytest.db')
        connect.execute('INSERT INTO user (name, email, password) VALUES (?, ?, ?)', (name, email, password))
        connect.commit()
        connect.close()
        # flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))
    return render_template('register.html')


def read_books():
    books = []
    with open('books.txt', 'r') as f:
        for line in f:
            title, author = line.strip().split('|')
            # Convert the title to a URL-safe filename
            image_filename = re.sub(r'\s+', '_', title.lower()) + '.jpg'
            books.append({'title': title, 'author': author, 'image': image_filename})
    return books

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        name = request.form['username']
        password = request.form['password']
        connect = sqlite3.connect('mytest.db')
        cursor = connect.execute('SELECT * FROM user WHERE name = ?', (name,))
        user = cursor.fetchone()
        connect.close()        
        if user and check_password_hash(user[3], password):
            user_obj = User(user[0], user[1], user[2], user[3])
            print("print user object")
            login_user(user_obj)
            print("printing the user")
            user_name = current_user.name
            print(user_name)
            books = read_books() 
            return render_template('home.html', user_name=user_name, books=books)
        else:
            flash("Invalid username or password", "danger")
            return render_template('login.html')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
   # flash("You have been logged out.", "info")
    return redirect(url_for('login'))

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/get')
def get():
    return "hello world"

@app.route('/forgot')
def forgot():
    return render_template('home.html')

@app.route('/reset')
def reset():
    return render_template('reset-password.html')

@app.route('/tools/')
@login_required
def tools():
    return render_template('tools.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        connect = sqlite3.connect('mytest.db')
        cursor = connect.execute('SELECT * FROM user WHERE email = ?', (email,))
        user = cursor.fetchone()
        connect.close()
        
        if user:
            token = serializer.dumps(email, salt='password-reset-salt')
            reset_url = url_for('reset_password', token=token, _external=True)
            msg = Message('Password Reset Request',
                          sender='noreply@example.com',
                          recipients=[email])
            msg.body = f'To reset your password, visit the following link: {reset_url}'
            mail.send(msg)
            flash('Check your email for password reset instructions.')
            return redirect(url_for('login'))
        else:
            flash('Email not found.', 'error')
    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=3600)
    except (SignatureExpired, BadSignature):
        flash('Invalid or expired token.', 'error')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        new_password = request.form['password']
        connect = sqlite3.connect('mytest.db')
        connect.execute('UPDATE user SET password = ? WHERE email = ?', 
                        (generate_password_hash(new_password), email))
        connect.commit()
        connect.close()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html', token=token)


if __name__ == '__main__':
    app.run(debug=True)
