__author__ = 'tony'
from flask import Flask, request, render_template
from redis import StrictRedis
import os

from libs.RedisWrapper import UserHelper

def register(app):
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
    else:
        error = 'Invalid method'
        return render_template('registration.html', error=error)

    if name == '' or username == '' or email == '' or password == '':
        error = 'All fields are required'
        return render_template('registration.html', error=error)
    else:

        return 'everything okay!'
        # Logic to insert user into database.

