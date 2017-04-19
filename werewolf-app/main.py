import logging

from flask import Flask, current_app
from flask_cors import CORS


app = Flask(__name__)
CORS(app)


@app.route('/')
def home():
    return current_app.send_static_file('home.html')


@app.route('/login')
def login():
    return current_app.send_static_file('login.html')


@app.route('/register')
def register():
    return current_app.send_static_file('register.html')


@app.route('/main')
def main():
    return current_app.send_static_file('main.html')


@app.route('/room')
def room():
    return current_app.send_static_file('room.html')


@app.route('/join_room')
def join_room():
    return current_app.send_static_file('join_room.html')


@app.route('/role')
def role():
    return current_app.send_static_file('role.html')


@app.route('/result')
def result():
    return current_app.send_static_file('result.html')


@app.route('/leaderboard')
def leaderboard():
    return current_app.send_static_file('leaderboard.html')


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
    app.run()
