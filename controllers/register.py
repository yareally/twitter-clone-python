__author__ = 'tony'
from flask import Flask, request, render_template
from redis import StrictRedis
import os
app = Flask(__name__)
@app.route('/registration', methods=['POST', 'GET'])
def register():
    error = None
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
    else:
        error = 'Invalid method'
        return render_template('login.html', error=error)

    if name == '' or username == '' or email == '' or password == '':
        error = 'All fields are required'
        return render_template('login.html', error=error)
    else:
        # Logic to insert user into database.
        return True

