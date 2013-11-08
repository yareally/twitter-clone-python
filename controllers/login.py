from flask import Flask, request, render_template, session
from redis import StrictRedis
import os
from libs.rediswrapper import UserHelper

from models.user import User


def login(app):
    if request.method == 'GET':
        return render_template('login.html', error=None, title='Twic Login')
    elif request.method == 'POST':
        error = list()
        name = request.form['name']
        password = request.form['password']

        # should be verifying via the redis wrapper methods, not using app.*
        if name != app.config['name']:
            error.append('Invalid Username')
        elif password != app.config['password']:
            error.append('Invalid Password')
        else:
            # Set the session as logged in.
            user = ''
            redis = StrictRedis()
            dbh = UserHelper(redis)
            if dbh.email_exists(name):
                user = dbh.get_user_by_email(request.form['name'])
            elif dbh.username_exists(name):
                user = dbh.get_user_by_username(request.form['name'])
            if user != '':
                hashed_password = UserHelper.hash_password(password, user.salt)
                if hashed_password == user.password:
                    # Save the user to the session
                    session['user'] = user
                    return render_template('dash.html', title='Welcome to Twic')
            else:
                error.append('That user does not exist.')

        return render_template('login.html', error=error)

