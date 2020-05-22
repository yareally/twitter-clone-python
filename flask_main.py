# coding=utf-8
__author__ = 'wes'
from flask import Flask, render_template, session
from redis import StrictRedis
from controllers.register import register as reg_controller
from controllers.login import login as login_controller
from controllers.dash import dash as dash_controller
from controllers.add_message import add_message as add_message_controller

app = Flask(__name__)
app.secret_key = '\x1c\xba\x97jT\xf1\xdb\x92S\xd7\x83\x0f{\xa3#\xf3\x9fg\xf3;\x96D\x01\x98'


@app.route('/')
@app.route('/home')
@app.route('/dash')
def dash(page_name=None):
    #if session['user']:
        #return render_template('dash.html', page_name='dash')
    #else:
    """

    @param page_name:
    @return: @rtype:
    """
    return dash_controller(app)

@app.route('/login', methods=['POST', 'GET'])
def login(page_name=None):
    """

    @param page_name:
    @return: @rtype:
    """
    return login_controller(app)

@app.route('/registration', methods=['POST', 'GET'])
def registration(page_name=None):
    """

    @param page_name:
    @return: @rtype:
    """
    return reg_controller(app)

@app.route('/logout', methods=['POST', 'GET'])
def logout(page_name=None):
    """

    @param page_name:
    @return: @rtype:
    """
    session.clear()
    return login_controller(app)

@app.route('/add_message', methods=['POST', 'GET'])
def add_message(page_name=None):
    """

    @param page_name:
    @return: @rtype:
    """
    return add_message_controller(app)

@app.route('/async-demo')
def async_route(page_name=None):
    """

    @param page_name:
    @return: @rtype:
    """
    redis = StrictRedis()
    redis.set("test", "redis test value")
    val = redis.get("test")
    return render_template('async_demo.html', page_name=val)

if __name__ == '__main__':
    app.debug = True
    app.run()

