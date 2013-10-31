from flask import Flask, request, render_template, session
from libs import session
from redis import StrictRedis
import os
from libs.rediswrapper import UserHelper
import redis
from models.user import User


def login(self, app):
    error = None
    if request.method == 'POST':
        if request.form['name'] != app.config['name']:
            error = 'Invalid Username'
        elif request.form['password'] != app.config['password']:
            error = 'Invalid Password'
        else:
            # Set the session as logged in.
            self.redis = redis.StrictRedis()
            self.dbh = UserHelper(self.redis)
            if self.dbh.email_exists(request.form['name']):
                user = self.dbh.get_user_by_email(request.form['name'])
            elif self.dbh.username_exists(request.form['name']):
                user = self.dbh.get_user_by_username(request.form['name'])
            #  Todo: Need to find out how to validate the user.
        return render_template('login.html', error=error)
