from flask import Flask, render_template
import os
from redis import StrictRedis

app = Flask(__name__)



@app.route('/')
@app.route('/home')
@app.route('/dash')
def dash(page_name=None):
    return render_template('dash.html', page_name='dash')

@app.route('/login')
def login(page_name=None):
    return render_template('login.html', page_name='login')

@app.route('/registration')
def registration(page_name=None):
    return render_template('registration.html', page_name='registration')


@app.route('/async-demo')
def async_route(page_name=None):
    redis = StrictRedis()
    redis.set("test", "redis test value")
    val = redis.get("test")
    return render_template('async_demo.html', page_name=val)

if __name__ == '__main__':
    app.debug = True
    app.run()
