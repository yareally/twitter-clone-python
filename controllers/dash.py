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
            dbh_user = UserHelper(StrictRedis())
            backward = dbh.get_user_messages(session['user']['id'])
            messages = reversed(backward)
            user = dbh_user.get_user_by_id(session['user']['id'])
            #users = list()
            #for message in messages:
                #user = dbh_user.get_user_by_id(message.user_id)
                #users.append(user)
                #message.user_id = user
            return render_template('dash.html', error=None, title='Twic Dashboard', messages=messages, user=user)

        return render_template('login.html', error='Please log in', title='Login')

    if request.method == 'POST':
        error = list()

