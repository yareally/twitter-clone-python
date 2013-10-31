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
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user = User(username, email, password, name)
        if name == '' or username == '' or email == '' or password == '':
            error = 'All fields are required'
            return render_template('registration.html', error=error, user=user)
        else:
            self.redis = redis.StrictRedis()
            self.dbh = UserHelper(self.redis)
            self.dbh.add_user(user)
            return render_template('dash.html')
            # Logic to insert user into database.

    else:
        error = 'Invalid method'
        return render_template('registration.html', error=error)



