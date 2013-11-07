__author__ = 'tony'
from flask import Flask, request, render_template, session
from redis import StrictRedis
import os
from libs.rediswrapper import UserHelper
import redis
from models.user import User


def register(self, app):
    """

    @param app:
    @type app: Flask
    @return:
    @rtype:
    """

    error = None

    if request.method == 'POST':
        error = list()
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user = User(username, email, password, name)
        self.redis = redis.StrictRedis()
        self.dbh = UserHelper(self.redis)
        if name == '' or username == '' or email == '' or password == '':
            error.append('All fields are required')
            return render_template('registration.html', error=error, title='Twic Registration', user=user)
        elif self.dbh.email_exists(user.email) or self.dbh.username_exists(user.username):
            error.append('That user already exists. Please login')
            return render_template('login.html', error=error, title='Login To Twic', user=user)
        else:
            self.dbh.add_user(user)
            session['user'] = user
            return render_template('dash.html', title='Twic Registration')
    else:
        error.append('Invalid method')
        return render_template('registration.html', error=error, title='Twic Registration')



