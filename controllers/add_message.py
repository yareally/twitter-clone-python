__author__ = 'tony'
from flask import request, render_template, session, redirect, url_for
from redis import StrictRedis
from libs.rediswrapper import MessageHelper
from models.message import Message

def add_message(app):
    error = list()
    if request.method == 'GET':
        error.append('Message could not be saved.')
        # return redirect(url_for('dash'))
    else:
        print 'Message added'
        message = request.form['message']
        if session.has_key('user'):
            dbh = MessageHelper(StrictRedis())
            message_object = Message(session['user']['id'], message)
            dbh.post_message(message_object)

        else:
            return redirect(url_for('login'))
    return redirect(url_for('dash'))
