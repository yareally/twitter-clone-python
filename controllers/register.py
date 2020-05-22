# coding=utf-8
__author__ = 'tony'
from flask import Flask, request, render_template, session, redirect, url_for
from redis import StrictRedis
import os
from libs.rediswrapper import UserHelper
from models.user import User


def register(app):
    """

    @param app:
    @type app: Flask
    @return:
    @rtype:
    """

    if request.method == 'GET':
        return render_template('registration.html', error=None, title='Twic Registration')

    if request.method == 'POST':
        errors = list()
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user = User(username, email, password, name)
        dbh = UserHelper(StrictRedis())

        if not name or not username or not email or not password:
            errors.append('All fields are required')

        if dbh.username_exists(user.username):
            errors.append('That username already exists. Please choose another')

        if dbh.email_exists(user.email):
            errors.append('That email already exists. Please choose another')

        if len(errors):
            return render_template('registration.html', error=errors, title='Twic Registration', user=user)

        dbh.add_user(user)
        session['user'] = user.get_dict()
        session['logged_in'] = True
        return redirect(url_for('dash'))




