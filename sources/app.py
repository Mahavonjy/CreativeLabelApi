# sources/app.py
""" shebang """

import os
import sentry_sdk
from flask_cors import CORS
from flask import Flask, request
from sources.models import custom_response
from preferences.config import app_config
from .models import db, bcrypt, mail, migrate
from flask_swagger_ui import get_swaggerui_blueprint
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from .routes import routing


def welcome(env_name):
    """ Create app """

    # app initiliazation
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(app_config[env_name])
    app.secret_key = os.getenv('FN_FLASK_SECRET_KEY')
    # sentry_sdk.init(
    #     dsn="https://8ca78b489b6e4cc6b1a26ffd5852a8e8@sentry.io/1814450",
    #     integrations=[FlaskIntegration(), SqlalchemyIntegration()]
    # )

    # initializing bcrypt, db, mail and migration
    bcrypt.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    # swagger
    SWAGGER_URL = '/doc'
    API_URL = '../static/swagger.yaml'
    SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "Creative Label API"
        }
    )
    app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)

    # ------------------------------------routes-----------------------------------#
    routing(app)
    # ------------------------------------routes-----------------------------------#

    @app.route('/', methods=['GET'])
    def home():
        """ API home page """

        return custom_response("Welcome to API ISL", 200)

    @app.errorhandler(404)
    def page_not_found(error):
        """ Page does not exist """

        return custom_response(str(error), 777)

    @app.route('/route', methods=['GET'])
    def route():
        """ Return all route and method existing on API """

        links, count = {}, 0
        for rule in app.url_map.iter_rules():
            temp = request.url_root
            new, url_root = list(rule.methods), temp.rsplit('/', 1)
            method = [x for x in new if x not in ('OPTIONS', 'HEAD')]
            links[count], count = {"Method": method[0], "url": url_root[0] + str(rule)}, count + 1
        return custom_response(links, 200)

    return app
