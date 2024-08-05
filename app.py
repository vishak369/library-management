from flask import Flask, request, render_template, redirect, flash, url_for
import sqlite3
from flask_login import UserMixin, login_user, login_required, current_user, logout_user, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask_mail import Mail, Message
import os
import socket
import re


app = Flask(__name__)

app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/images'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'vishakcode@gmail.com'
app.config['MAIL_PASSWORD'] = 'sivv orgt jgjh gzxb'
#app.config['MAIL_PASSWORD'] = 'getonthefloor'
mail = Mail(app)
serializer = URLSafeTimedSerializer(app.secret_key)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
# Initialize SQLite database
def init_sqlite_db():
    connect = sqlite3.connect('mytest.db')
    connect.execute('CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT, password TEXT, is_admin BOOLEAN NOT NULL DEFAULT 0)')
    connect.close()
init_sqlite_db()

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Specifies the endpoint to redirect to for login

# User class
class User(UserMixin):
    def __init__(self, id, name, email, password, is_admin):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.is_admin = is_admin

@login_manager.user_loader
def load_user(user_id):
    connect = sqlite3.connect('mytest.db')
    cursor = connect.execute('SELECT * FROM user WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    connect.close()
    if user:
        return User(user[0], user[1], user[2], user[3], user[4])
    return None


@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        file = request.files['image']
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            with sqlite3.connect('mytest.db') as db:
                db.execute('INSERT INTO books (title, author, image) VALUES (?, ?, ?)', (title, author, filename))
                db.commit()
            flash('Book added successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
    return render_template('admin2.html')

@app.route('/admin2', methods=['GET', 'POST'])
@login_required
def admin_dashboard2():
    if not current_user.is_admin:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        file = request.files['image']
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            with sqlite3.connect('mytest.db') as db:
                db.execute('INSERT INTO books (title, author, image) VALUES (?, ?, ?)', (title, author, filename))
                db.commit()
            flash('Book added successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
    return render_template('admin.html')

@app.route('/get/<int:book_id>/<string:book_name>')
@login_required
def get_book(book_id,book_name):
    connect = sqlite3.connect('mytest.db')
    cursor = connect.execute('INSERT INTO user_books (user_id, name, book_id, book_name) VALUES (?, ?, ?, ?)', (current_user.id,current_user.name, book_id, book_name))
    connect.commit()
    connect.close()
    flash('Book taken successfully!', 'success')
    return redirect(url_for('home'))

@app.route('/return/<int:book_id>')
@login_required
def return_book(book_id):
    connect = sqlite3.connect('mytest.db')
    cursor = connect.execute('DELETE FROM user_books WHERE user_id = ? AND book_id = ?', (current_user.id, book_id))
    connect.commit()
    connect.close()
    flash('Book returned successfully!', 'success')
    return redirect(url_for('home'))


@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == 'POST':
        name = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        
        connect = sqlite3.connect('mytest.db')
        connect.execute('INSERT INTO user (name, email, password, is_admin) VALUES (?, ?, ?, ?)', (name, email, password, 0))
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(username)
        print(password)
        connect = sqlite3.connect('mytest.db')
        cursor = connect.execute('SELECT * FROM user WHERE name = ?', (username,))
        user = cursor.fetchone()
        print(user)
        connect.close()

        if user and check_password_hash(user[3], password):
       # if user and user[3] == password:
            print("printing the user:",user[3])
            user_obj = User(user[0], user[1], user[2], user[3], user[4])
            login_user(user_obj)
            if user_obj.is_admin:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('home'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')


@app.route('/add_book', methods=['POST'])
@login_required
def add_book():
    if not current_user.is_admin:
        return redirect(url_for('home'))
    title = request.form['title']
    author = request.form['author']
    connect = sqlite3.connect('mytest.db')
    connect.execute('INSERT INTO book (title, author) VALUES (?, ?)', (title, author))
    connect.commit()
    return redirect(url_for('admin'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
   # flash("You have been logged out.", "info")
    return redirect(url_for('login'))


#@app.route('/get')
#def get():
#    return "hello world"

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


@app.route('/delete_book/<int:book_id>', methods=['POST'])
@login_required
def delete_book(book_id):
    if not current_user.is_admin:
        flash("You do not have permission to delete books.")
        return redirect(url_for('home'))

    connect = sqlite3.connect('mytest.db')
    cursor = connect.cursor()
    cursor.execute('DELETE FROM books WHERE id = ?', (book_id,))
    connect.commit()
    connect.close()

    flash("Book deleted successfully.")
    return redirect(url_for('home'))



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

@app.route('/home')
@login_required
def home():
    connect = sqlite3.connect('mytest.db')
    cursor = connect.execute('SELECT * FROM books')
    books = cursor.fetchall()
    connect.close()
    return render_template('home.html', books=books, user_name=current_user.name, is_admin=current_user.is_admin)


@app.route('/view_user_books')
@login_required
def view_user_books():
    connect = sqlite3.connect('mytest.db')
    cursor = connect.execute('select DISTINCT name from user_books;')
    username = cursor.fetchall()
    print(username)
    mm=[]
    for i in username:
        print(i)
        mm.append(i)
        cursor = connect.execute('select book_name from user_books where name=?;', (i))
        booknames1 = cursor.fetchall()
        print(booknames1)
    connect.close()
    if username:
        return render_template('view_user_books.html', name1=mm, booknames1=booknames1) 
    else:
        return "No books found for this user."
    #return render_template('home.html', books=books, user_name=current_user.name, is_admin=current_user.is_admin)

@app.route('/my_books')
@login_required
def my_books():
    connect = sqlite3.connect('mytest.db')
    cursor = connect.execute('select book_name from user_books where name=?;', (user_name))
    username = cursor.fetchall()
    return render_template('my_books.html', username=username) 
def update_schema():
    with sqlite3.connect('mytest.db') as db:
        cursor = db.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            is_admin INTEGER NOT NULL DEFAULT 0
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            image TEXT
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS user_books (
            user_id INTEGER,
            book_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES user(id),
            FOREIGN KEY (book_id) REFERENCES books(id),
            PRIMARY KEY (user_id, book_id)
        )''')
        db.commit()

update_schema()


if __name__ == '__main__':
    app.run(debug=True)
