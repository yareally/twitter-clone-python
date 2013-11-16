from flask import request, render_template, session, redirect, url_for
from redis import StrictRedis
from libs.rediswrapper import UserHelper
import lepl.apps.rfc3696


def login(app):
    """

    :param app:
    :return: :rtype:
    """
    if request.method == 'GET':
        return render_template('login.html', error=None, title='Twic Login')
    elif request.method == 'POST':
        error = list()
        name = request.form['name']
        password = request.form['password']

        # should be verifying via the redis wrapper methods, not using app.*
        # if name != app.config['name']:
        #     error.append('Invalid Username')
        # elif password != app.config['password']:
        #     error.append('Invalid Password')
        # else:
        # Set the session as logged in.
        user = None
        redis = StrictRedis()
        dbh = UserHelper(redis)
        email_validator = lepl.apps.rfc3696.Email()
        valid = email_validator(name)
        if email_validator(name) and dbh.email_exists(name):
            user = dbh.get_user_by_email(request.form['name'])
        elif dbh.username_exists(name):
            user = dbh.get_user_by_username(request.form['name'])
        if user:
            hashed_password = UserHelper.hash_password(password, user.salt)
            if hashed_password == user.password:
                # Save the user to the session
                session['user'] = user.get_dict()
                session['logged_in'] = True
                return redirect(url_for('dash'))

        else:
            error.append('That user does not exist.')

        return render_template('login.html', error=error)

