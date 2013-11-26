# coding=utf-8
from flask import Flask, request, render_template, session
from redis import StrictRedis
import os
from libs.rediswrapper import UserHelper
from libs.rediswrapper import MessageHelper
from models.message import Message
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
            dbh = MessageHelper(StrictRedis())
            messages = dbh.get_user_messages(session['user']['id'])
            message = Message(6, 'This is a message to check if it gets rendered in the dash.')
            messages.append(message)
            return render_template('dash.html', error=None, title='Twic Dashboard', messages=messages)
        else:
            return render_template('login.html', error='Please log in', title='Login')
    elif request.method == 'POST':
        error = list()
        dbh = UserHelper(StrictRedis())
        dbh.add_user(user)
        session['user'] = user.__str__()
        return render_template('registration.html', title='Twic Registration')
