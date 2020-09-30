#!/usr/bin/env python3
""" shebang """

from preferences.env import app_config
from elasticsearch import Elasticsearch
from flask_sqlalchemy import SQLAlchemy
from flask import json, Response
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
from flask_mail import Mail
import os

load_dotenv()
env_path = os.path.join(os.path.join(os.path.dirname(__file__), '../..'), '.env')
load_dotenv(dotenv_path=env_path)

# initialize elastic_search
es = Elasticsearch(hosts=[app_config[os.getenv("FLASK_ENV")].ES_HOST])

migrate = Migrate()

# initialize our db
db = SQLAlchemy()

# Crypt Password
bcrypt = Bcrypt()

# initialize mail
mail = Mail()


# initialize json return
def custom_response(response, status_code):
    """ Custom Response Function """

    return Response(
        mimetype="application/json",
        response=json.dumps(response),
        status=status_code
    )
