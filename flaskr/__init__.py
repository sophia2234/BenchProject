#INIT PAGE: This page is the initialization of the app/website, configures app and profile picture and 
#imports backend Python files, initializes database, and imports auth.py page and dashboard.py page

import os

from flask import Flask, render_template, request
from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask_mail import Mail, Message

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
        UPLOADED_PHOTOS_DEST= 'flaskr/static/uploads',
        # Flask mail setting..... pip uninstall flask-mail pip install flask_mail==0.9.0
        # Replace username and password
        # Using a gmail account : enable this https://www.google.com/settings/security/lesssecureapps
        MAIL_USERNAME = "*******@gmail.com",
        MAIL_PASSWORD = "*******",
        MAIL_USE_TLS=True,
        MAIL_USE_SSL=False,
        MAIL_PORT=587,
        MAIL_SERVER='smtp.gmail.com',
    )
    #Configure Profile Picture Upload
    photos = UploadSet('photos', IMAGES)
    configure_uploads(app, photos)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    #Importing the Back-End Python files
    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import dashboard
    app.register_blueprint(dashboard.bp)
    app.add_url_rule('/', endpoint='table2')

    return app
