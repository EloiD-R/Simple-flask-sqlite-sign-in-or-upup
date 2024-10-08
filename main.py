"""Imports"""
import os
from os import getenv

from flask import Flask, redirect, session, render_template_string, request, g, send_from_directory, render_template
from flask.globals import request_ctx

from App import index, home, signing_manager
from App.utils.db.user_db import *

global request_counter
globals()['request_counter'] = 0

if __name__ == "__main__":
    # Flask and session cookies secret key init
    flask_app = Flask("sign.in.up - sqlite - flask")
    flask_app.secret_key = b'\xe5\xef\x92\x89\xc9v\x18\x14P\xbf\x88\xd7\x19\xff\x8b\x1aH\xd2\x15\xc7\xd0\x1cv\xf6' # os.urandom(24)

    """DB MANAGEMENT"""
    # Open db when needed
    def get_user_db():
        db = getattr(g, "_database", None)
        if db is None:
            db = g._database = userDB("user_db")
            print("Database initialized")
        print("Opening database")
        return db

    # Close db at each teardown (end of request, exception, ...)
    @flask_app.teardown_appcontext
    def close_user_db_connection(exception):
        db = getattr(g, '_database', None)
        if db is not None:
            print(f"Closing user_db : {exception}")
            db.quit_db()


    @flask_app.before_request
    def check_if_user_is_connected():
        EXCLUDED_ROUTES = ["route_sign_in_or_up", "route_index", "route_favicon", "route_signing_css", "route_blob_image"]  # add routes as needed
        route_to_load = request.endpoint  # To make the code more readable
        print(f"route : {route_to_load}")
        if route_to_load not in EXCLUDED_ROUTES:
            if route_to_load is not None:
                if session.get('login_state') is None or 'login_state' not in session:
                    return redirect("/sign.in.up")
                elif session['login_state'] is True:
                    pass  # Continue and load request (any)
                else:
                    return redirect("/sign.in.up")

            # Typically occurs when an error is triggered ex : 404
            if route_to_load is None and session.get("login_state") != True:
                return redirect("/sign.in.up")
            # Else, continue and load request (from EXCLUDED_ROUTES)

    @flask_app.before_request
    def requests_counter():
        globals()["request_counter"] += 1
        print(f"request n°{globals()['request_counter']} since server was launched ")


    @flask_app.route('/favicon.ico')
    def route_favicon():
        return send_from_directory(os.path.join(flask_app.root_path, 'static'),'favicon.ico', mimetype='image/vnd.microsoft.icon')

    @flask_app.route('/static/css/signing.css')
    def route_signing_css():
        return send_from_directory('static/css', 'signing.css')

    @flask_app.route('/static/images/blob.svg')
    def route_blob_image():
        return send_from_directory('static/images', 'blob.svg')


    @flask_app.route("/", methods=["GET", "POST"])
    def route_index():
        return index.load()

    @flask_app.route("/home", methods=["GET", "POST"])
    def route_home():
        return home.load()

    @flask_app.route("/sign.in.up", methods=["GET", "POST"])
    def route_sign_in_or_up():
        return signing_manager.load(get_user_db())

    @flask_app.errorhandler(404)
    def handle_404(error):
        return render_template("404.html")


    flask_app.run(debug=True, host="0.0.0.0", port=5555)
