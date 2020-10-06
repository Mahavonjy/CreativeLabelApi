# /sources/config.py
""" shebang """

import os

import sentry_sdk
import cloudinary
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration


class Default:
    """ all default config """

    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET")
    )

    # run sentry only production
    if os.getenv('FLASK_ENV') == 'production':
        sentry_sdk.init(
            dsn=os.getenv('SENTRY_SDK_DSN'),
            integrations=[FlaskIntegration(), SqlalchemyIntegration()]
        )

    DEBUG = True  # Auto refresh run
    SQLALCHEMY_POOL_SIZE = 100
    SQLALCHEMY_MAX_OVERFLOW = 15
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')

    # sign in facebook
    FACEBOOK_APP_ID = os.getenv('FACEBOOK_APP_ID')
    FACEBOOK_APP_SECRET = os.getenv('FACEBOOK_APP_SECRET')

    # sign in Google
    CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    USER_INFO = os.getenv('GOOGLE_USER_INFO')

    # Email Connection config
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True


class DevelopmentTest(Default):
    """ Development environment configuration """

    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://cynthionmahavonjy:2245@localhost:5432/creative_test'
    ES_HOST = {"host": "localhost", "port": 9200}
    ES_INDEX = ["beats", "services", "options", "materials"]
    MAIL_USERNAME = 'mahavonjy.cynthion@gmail.com'
    MAIL_PASSWORD = 'Mallow11!'


class Development(Default):
    """ Development environment configuration """

    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://cynthionmahavonjy:2245@localhost:5432/creative'
    ES_HOST = {"host": "localhost", "port": 9200}
    ES_INDEX = ["beats", "services", "options", "materials"]
    MAIL_USERNAME = os.getenv('MAIL_DEV_USERNAME_API')
    MAIL_PASSWORD = os.getenv('MAIL_DEV_PASSWORD_API')


class Production(Default):
    """ Production environment configurations """

    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://cynthionmahavonjy:2245@creative-db/creative'
    ES_HOST = {"host": "elasticsearch", "port": 9200}
    ES_INDEX = ["beats", "services", "options", "materials"]
    MAIL_USERNAME = os.getenv('MAIL_PROD_USERNAME_API')
    MAIL_PASSWORD = os.getenv('MAIL_PROD_PASSWORD_API')


app_config = {
    'development': Development,
    'development_test': DevelopmentTest,
    'production': Production,
}
