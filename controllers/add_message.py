# coding=utf-8
__author__ = 'tony'
from flask import request, session, redirect, url_for, jsonify
from redis import StrictRedis
from libs.rediswrapper import MessageHelper, UserHelper
from models.message import Message


def add_message(page_name=None):
    """

    @param page_name:
    @return: @rtype:
    """
    error = list()

    #  if request.method == 'GET':
    #   error.append('Message could not be saved.')
    # return redirect(url_for('dash'))
    # else:
    #print('Message added')

    if request.method == 'GET':
        message = request.args.get('message', '', type=str)
    else:
        message = request.form['message']

    if 'user' in session:
        dbh = MessageHelper(StrictRedis())
        message_object = Message(session['user']['id'], message)
        dbh.post_message(message_object)
       # user = UserHelper(StrictRedis()).get_user_by_id(session['user']['id'])
        msg_count = dbh.get_msg_count(session['user']['id'])

    else:
        return redirect(url_for('login'))

    if request.method == 'GET':
        return jsonify(post_time=message_object.posted_time,
                       format_time=message_object.formatted_time,
                       msg_id=message_object.id,
                       msg_count=msg_count)

    return redirect(url_for('dash'))
