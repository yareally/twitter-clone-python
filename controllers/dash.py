# coding=utf-8
from flask import Flask, request, render_template, session
from redis import StrictRedis
import os
from libs.rediswrapper import UserHelper
from models.user import User


def dash(app):
    """

    @param app:
    @type app: Flask
    @return:
    @rtype:
    """

    if request.method == 'GET':
        if session.has_key('user'):
            return render_template('dash.html', error=None, title='Twic Dashboard')
        else:
            return render_template('login.html', error='Please log in', title='Login')
    elif request.method == 'POST':
        error = list()
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user = User(username, email, password, name)
        dbh = UserHelper(StrictRedis())

        if name == '' or username == '' or email == '' or password == '':
            error.append('All fields are required')
            return render_template('registration.html', error=error, title='Twic Registration', user=user)
        elif dbh.email_exists(user.email) or dbh.username_exists(user.username):
            error.append('That username already exists. Please choose another')
            return render_template('registration.html', error=error, title='Twic Registration', user=user)
        elif dbh.email_exists(user.email):
            error.append('That email already exists. Please choose another')
            return render_template('registration.html', error=error, title='Twic Registration', user=user)
        else:
            dbh.add_user(user)
            session['user'] = user.__str__()
            return render_template('dash.html', title='Twic Registration')
