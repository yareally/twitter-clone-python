__author__ = 'tony'
from flask import request, render_template, session, redirect, url_for, jsonify
from redis import StrictRedis
from libs.rediswrapper import MessageHelper
from models.message import Message


def add_message(page_name=None):
    error = list()
    json = None

    #  if request.method == 'GET':
    #   error.append('Message could not be saved.')
    # return redirect(url_for('dash'))
    # else:
    #print('Message added')

    if request.method == 'POST':
        message = request.form['message']
    else:
        #json = request.get_json()
        #if not json:
        message = request.args.get('message', '', type=str)

    if 'user' in session:
        dbh = MessageHelper(StrictRedis())
        message_object = Message(session['user']['id'], message)
        dbh.post_message(message_object)

    else:
        return redirect(url_for('login'))

    if request.method == 'GET':
        return jsonify(post_time=message_object.posted_time,
                       format_time=message_object.formatted_time,
                       msg_id=message_object.id)
    else:
        return render_template('dash.html')

        #return add_message_controller(app)
