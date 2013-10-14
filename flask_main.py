from flask import Flask, render_template
import os

app = Flask(__name__)


@app.route('/')
def hello_world(page_name=None):
    #return 'test'
    return render_template('index.html', page_name='index')


if __name__ == '__main__':
    app.debug = True
    app.run()
