# /sources/config.py
""" shebang """

import os


class DevelopmentTest:
    """ Development environment configuration """

    DEBUG = True  # Auto refresh run
    TESTING = True
    SQLALCHEMY_POOL_SIZE = 100
    SQLALCHEMY_MAX_OVERFLOW = 15
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = 'postgresql://cynthionmahavonjy:2245@localhost:5432/creative_test'
    ES_HOST = {"host": "localhost", "port": 9200}
    ES_INDEX = ["albums_and_songs"]

    # Email Config
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USERNAME = os.getenv('MAIL_USERNAME_API')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD_API')
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True

    # sign in facebook
    FACEBOOK_APP_ID = os.getenv('FACEBOOK_APP_ID')
    FACEBOOK_APP_SECRET = os.getenv('FACEBOOK_APP_SECRET')

    # sign in Google
    CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    USER_INFO = os.getenv('GOOGLE_USER_INFO')


class Development:
    """ Development environment configuration """

    DEBUG = True  # Auto refresh run
    TESTING = False
    SQLALCHEMY_POOL_SIZE = 100
    SQLALCHEMY_MAX_OVERFLOW = 15
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = 'postgresql://cynthionmahavonjy:2245@localhost:5432/creative'
    ES_HOST = {"host": "localhost", "port": 9200}
    ES_INDEX = ["albums_and_songs", "services", "options", "materials"]

    # Email Config
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USERNAME = os.getenv('MAIL_USERNAME_API')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD_API')
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True

    # sign in facebook
    FACEBOOK_APP_ID = os.getenv('FACEBOOK_APP_ID')
    FACEBOOK_APP_SECRET = os.getenv('FACEBOOK_APP_SECRET')

    # sign in Google
    CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    USER_INFO = os.getenv('GOOGLE_USER_INFO')


class Production:
    """ Production environment configurations """

    DEBUG = True  # Auto refresh run
    TESTING = False
    SQLALCHEMY_POOL_SIZE = 100
    SQLALCHEMY_MAX_OVERFLOW = 15
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = 'postgresql://cynthionmahavonjy:2245@creative-db/creative'
    ES_HOST = {"host": "elasticsearch", "port": 9200}
    ES_INDEX = ["albums_and_songs", "services", "options", "materials"]

    # Email Config
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USERNAME = os.getenv('MAIL_USERNAME_API')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD_API')
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True

    # sign in facebook
    FACEBOOK_APP_ID = os.getenv('FACEBOOK_APP_ID')
    FACEBOOK_APP_SECRET = os.getenv('FACEBOOK_APP_SECRET')

    # sign in Google
    CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    USER_INFO = os.getenv('GOOGLE_USER_INFO')


app_config = {
    'development': Development,
    'development_test': DevelopmentTest,
    'production': Production,
}
