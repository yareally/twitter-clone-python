from flask import Flask, request, render_template
from libs import session
from redis import StrictRedis
import os

app = Flask(__name__)
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['name'] != app.config['name']:
            error = 'Invalid Username'
        elif request.form['password'] != app.config['password']:
            error = 'Invalid Password'
        else:
            # Set the session as logged in.
            userid = 1  # Get the user id from the database.
            if userid:
                session.logged_in = True
                return render_template('dash.html', error=error)
            else:
                error = 'Invalid User'
        return render_template('login.html', error=error)
