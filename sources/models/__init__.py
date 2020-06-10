# sources/Models/__init__.py
""" shebang """

import stripe
from werkzeug.utils import secure_filename
from preferences.config import app_config
from elasticsearch import Elasticsearch
from flask_sqlalchemy import SQLAlchemy
from flask import json, Response
from google.cloud import storage
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
from flask_mail import Mail
import datetime
import json
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


# calculate the percent value
class Percent:
    """ calc percent """

    def __init__(self, base=None, percentage=None):

        self.result = float(base) * float(percentage) / float(100)


def check_reservation_info_with_service_info(reservation_basic_schema, Services, User, data_to_dump, req=None):

    tmp = reservation_basic_schema.dump(data_to_dump)
    tmp["title"] = Services.get_by_service_id(tmp["services_id"]).title
    tmp["artist_name"] = User.get_one_user(tmp["artist_owner_id"]).name
    tmp["auditor_name"] = User.get_one_user(tmp["auditor_who_reserve_id"]).name
    if req:
        return {"reservations": tmp}
    return tmp


def check_all_user_payment_history(user_connected_model, p_h_schema, User, Reservations):
    payment_history_obj = []
    payment_list = user_connected_model.purchased_history.all() + user_connected_model.purchase_history.all()
    if payment_list:
        for p in payment_list:
            p_h_obj = p_h_schema.dump(p)
            p_h_obj["buyer_name"] = User.get_one_user(p_h_obj["buyer_id"]).name
            p_h_obj["artist_name"] = User.get_one_user(p_h_obj["artist_id"]).name
            try:
                reservation_tmp = Reservations.get_reservation_by_payment_history_id(p_h_obj["id"])
                p_h_obj["event"] = reservation_tmp.event
                p_h_obj["invoice"] = reservation_tmp.invoice
                p_h_obj["services_id"] = reservation_tmp.services_id
            except AttributeError:
                p_h_obj["event"] = ""
            payment_history_obj.append(p_h_obj)
    return payment_history_obj


def payment_stripe(total_price, stripe_token_id, description):
    """

    :param total_price: this is a amount for user paid
    :param stripe_token_id: token for payment stripe
    :param description: some description payment
    :return: return result off creating stripe charge
    """

    return stripe.Charge.create(
        amount=int(total_price * 100),
        currency="eur",
        description=description,
        source=stripe_token_id
    )


def send_file_to_storage(bucket_name, uploaded_file, b_n, type_, public=True):

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(b_n)
    blob.upload_from_string(uploaded_file.read(), content_type=type_) # "image/jpeg" switched to type_

    if public:
        blob.make_public()
        return blob.public_url
    blob.upload_from_string(uploaded_file.read(), content_type=type_)
    return blob.generate_signed_url(expiration=datetime.timedelta(hours=1))


# add file in storage google
def add_in_storage(bucket_name, ser_user, uploaded_file, file_storage=None,
                   album_song=None, extension=None, req=None, beats=None,):
    """ add song in database with or not photo """

    filename = secure_filename(uploaded_file.filename)
    if file_storage:
        b_n = file_storage + ser_user['fileStorage_key'] + '_' + str(ser_user['id']) + '/' + filename
        # switch "image/jpeg" to uploaded_file.content_type
        return send_file_to_storage(bucket_name, uploaded_file, b_n, uploaded_file.content_type)
    if album_song:
        b_n = ser_user['fileStorage_key'] + '_' + str(album_song) + '_' + str(ser_user['id']) + '/' + filename
        return send_file_to_storage(bucket_name, uploaded_file, b_n, "audio/" + extension, public=False)
    if beats:
        b_n = beats + '/' + ser_user['fileStorage_key'] + '_' + str(ser_user['id']) + '/' + filename
        return send_file_to_storage(bucket_name, uploaded_file, b_n, uploaded_file.content_type, public=False)
    b_n = ser_user['fileStorage_key'] + '_' + str(ser_user['id']) + '/' + filename
    if req:
        return send_file_to_storage(
            bucket_name, uploaded_file, b_n, uploaded_file.content_type or "application/pdf"
        )
    return send_file_to_storage(bucket_name, uploaded_file, b_n, uploaded_file.content_type, public=False)


# compare time created_at with now time
def get_time(created_at, min_value: int) -> bool:
    """ compare created time and now """

    now_time = datetime.datetime.now()
    date, rest = created_at.split('T')
    hour, _ = rest.split('.')
    hours, min_, sec = hour.split(":")
    year, month, day = date.split('-', 3)
    date_for_created_cart = datetime.datetime(int(year), int(month), int(day), int(hours), int(min_), int(sec))
    x = now_time - date_for_created_cart
    return divmod(x.days * 86400 + x.seconds, 60)[0] <= min_value


# initialize json return
def custom_response(response, status_code):
    """ Custom Response Function """

    return Response(
        mimetype="application/json",
        response=json.dumps(response),
        status=status_code
    )
