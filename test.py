from flask import Flask
from flask_mail import Mail, Message

app = Flask(__name__)

# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'vishakcode@gmail.com'
app.config['MAIL_PASSWORD'] = 'sivv orgt jgjh gzxb'

mail = Mail(app)

@app.route('/send_mail')
def send_mail():
    msg = Message('Hello from Flask-Mail', sender='your_email@gmail.com', recipients=['recipient@example.com'])
    msg.body = 'This is a test email sent from a Flask application!'
    mail.send(msg)
    return 'Mail sent!'

if __name__ == '__main__':
    app.run(debug=True)
