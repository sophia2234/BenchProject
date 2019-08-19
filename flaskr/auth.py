#AUTH PAGE: This page is for new user REGISTRATION and validation [with error displays], displays LOGIN page
#[with registered users and successful new registered users] with validation, redirects user to RECCOMMENDED page,
#starts session data for user, logouts user [if needed] and redirects to LOGIN page, and redirects non-logged in user to LOGIN page
import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flask_mail import Message, Mail
from flaskr.__init__ import create_app

from flaskr.db import get_db
import random

import re

bp = Blueprint('auth', __name__, url_prefix='/auth')

# This method is called when a new user registers and renders register.html or redirects to
# the login page if user successfully registers
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        passwordConfirmation = request.form['password2']
        email = request.form['email']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        description = request.form['description']
        db = get_db()
        # allow all errors to display at the top
        error = []
        if not username:
            error.extend(['Username is required.'])
        if re.match(".{8,}", username) is None:
            error.extend(['Please Enter a Username with at least 8 Characters.'])

        if re.match("^[a-zA-Z0-9]{8,}$", username) is None:
            error.extend(['Please include only Letters and Numbers for Username.'])

        if not password:
            error.extend(['Password is required.'])
        if not passwordConfirmation:
            error.extend(['Must confirm password.'])
        if password != passwordConfirmation:
            error.extend(['Passwords do not match.'])
        if not email:
            error.extend(['Email is required.'])

        if not firstName:
            error.extend(['First Name is required.'])

        if not lastName:
            error.extend(['Last Name is required.'])

        x = True;
        while x:
            if not re.search("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", password):
                error.extend(["Please enter a password at of least 8 characters containing an uppercase letter, lowercase letter, number, and special character."])
                break
            else:
                x = False
        if db.execute(
            'SELECT userId FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error.extend(
                ['User {} is already registered. Please choose a different username or log in.'.format(username)])
        if db.execute(
            'SELECT email FROM user WHERE email = ?', (email,)
        ).fetchone() is not None:
            error.extend(
                ['User with email address {} is already registered.'.format(email)])

        elif not error:
            db.execute(
                'INSERT INTO user (username, password, email, firstName, lastName, description, profilePicture) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (username, generate_password_hash(password), email, firstName, lastName, description, 'uploads/stickfigure.png')
            )
            db.commit()
            return redirect(url_for('auth.login'))

        for eror in error:
            flash(eror)

    return render_template('auth/register.html')


# This method renders the login page and redirects the user to the recommended properties page
# if they successfully log in
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['userId']
            return redirect(url_for('dashboard.table2'))

        flash(error)

    return render_template('auth/login.html')


# This method loads the logged in user if they leave the page and return
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE userId = ?', (user_id,)
        ).fetchone()


# This method logs out the user and redirects to login page
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
# local variable for forgot password and update password
random.seed( 30 )
pin = ''.join(random.choice('0123456789') for num in range(8))
# Method that renders forgot_password.html
@bp.route('/forgot_password', methods=('GET', 'POST'))
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        db = get_db()
        if db.execute(
                'SELECT email FROM user WHERE email = ?', (email,)
        ).fetchone() is None:
            flash('There is no email address: {}, please create an account.'.format(email))
        else:
            find_username = db.execute(
                'SELECT username FROM user WHERE email = ?', (email,)
            ).fetchone()
            username = str(find_username[0])
            # Title of email , define sender and recipient as the email inputted in forgot password
            msg = Message("Hello, you receiving this email in regards to PropertyPicker. Your username is : " + username,
                          sender=email,
                          recipients=[email])
            # The body message for the email
            msg.html = " To reset your password please enter " + pin + " by " + "<a href='http://127.0.0.1:5000/auth/update_password'>clicking here: </a>"
            # To send it using Flask-Mail library (https://pythonhosted.org/Flask-Mail/)
            app = create_app(None)
            mail = Mail(app)
            mail.send(msg)
            flash('Email has been sent to email address: {}, please check your email.'.format(email))


    return render_template('auth/forgot_password.html')

# Method that renders update_password.html
@bp.route('/update_password', methods=('GET', 'POST'))
def update_password():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        passwordConfirmation = request.form['password2']
        inputPin = request.form['pin']
        db = get_db()
        error = []
        if pin != inputPin:
            error.extend(['Pin is required.'])
        if not username:
            error.extend(['Username is required.'])
        if re.match(".{8,}", username) is None:
            error.extend(['Please Enter a Username with at least 8 Characters.'])

        if re.match("^[a-zA-Z0-9]{8,}$", username) is None:
            error.extend(['Please include only Letters and Numbers for Username.'])

        if not password:
            error.extend(['Password is required.'])
        if not passwordConfirmation:
            error.extend(['Must confirm password.'])
        if password != passwordConfirmation:
            error.extend(['Passwords do not match.'])
        x = True;
        while x:
            if not re.search("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", password):
                error.extend([
                                 "Please enter a password at of least 8 characters containing an uppercase letter, lowercase letter, number, and special character."])
                break
            else:
                x = False
        if not error:
            db.execute(
                'UPDATE user SET password = ? WHERE userId =? ',
                (password, username)
            )
            db.commit()
            return redirect(url_for('auth.login'))

        for eror in error:
            flash(eror)
    return render_template('auth/update_password.html')


# This method is called when a user must be logged in to view a page (all html pages in dashboard folder)
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view





