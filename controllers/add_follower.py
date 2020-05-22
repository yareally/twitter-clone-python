# coding=utf-8
__author__ = 'wes'
from flask import request, session, redirect, url_for, jsonify
from redis import StrictRedis
from libs.rediswrapper import MessageHelper
from models.message import Message


def add_follower(page_name=None):
    """

    @param page_name:
    @return: @rtype:
    """
    error = list()

    # get the id of the user you want to follow
    if request.method == 'GET':
        # via ajax
        message = request.args.get('follow-user-id', '', type=str)
    else:
        # via no javascript post
        message = request.form['follow-user-id']

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

    return redirect(url_for('dash'))
