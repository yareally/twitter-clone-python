# coding=utf-8
from models.user import User

__author__ = 'wes'
from flask import request, session, redirect, url_for, jsonify
from redis import StrictRedis
from libs.rediswrapper import MessageHelper, UserHelper
from models.message import Message


def search(page_name=None):
    """

    @param page_name:
    @return: @rtype:
    """
    error = list()

    # get the id of the user you want to follow
    if request.method == 'GET':
        # via ajax
        search_request = request.args.get('search-request', '', type=str)
    else:
        # via no javascript post
        search_request = request.form['search-request']

    if 'user' in session:
        dbh = UserHelper(StrictRedis())
        user = dbh.get_user_by_id(session['user']['id'])
        dbh.get_all_usernames()
        dbh.post_message(message_object)

    else:
        return redirect(url_for('login'))

    if request.method == 'GET':
        return jsonify(post_time=message_object.posted_time,
                       format_time=message_object.formatted_time,
                       msg_id=message_object.id)

    return redirect(url_for('dash'))
