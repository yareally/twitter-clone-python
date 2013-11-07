from flask import Flask, request, render_template, session
from redis import StrictRedis
import os
from libs.rediswrapper import UserHelper
import redis
from models.user import User


def login(self, app):
    error = list()
    name = request.form['name']
    password = request.form['password']
    if request.method == 'POST':
        if name != app.config['name']:
            error.append('Invalid Username')
        elif password != app.config['password']:
            error.append('Invalid Password')
        else:
            # Set the session as logged in.
            user = ''
            self.redis = redis.StrictRedis()
            self.dbh = UserHelper(self.redis)
            if self.dbh.email_exists(name):
                user = self.dbh.get_user_by_email(request.form['name'])
            elif self.dbh.username_exists(name):
                user = self.dbh.get_user_by_username(request.form['name'])
            if user != '':
                hashed_password = User.hash_password(password, user.salt)
                if hashed_password == user.password:
                    # Save the user to the session
                    session['user'] = user
                    return render_template('dash.html', title='Welcome to Twic')
            else:
                error.append('That user does not exist.')

        return render_template('login.html', error=error)
