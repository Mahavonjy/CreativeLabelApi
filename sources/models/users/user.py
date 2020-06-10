#!/usr/bin/env python3
""" shebang """

import datetime

from sqlalchemy import asc
from sources.models import db
from sources.app import bcrypt
from marshmallow import fields
from sources.models.carts.cart import Carts
from sources.models.medias.media import Media
from sources.models.medias.albums import Albums
from dateutil.relativedelta import relativedelta
from sources.models.stars.noteStars import Stars
from sources.models.playlists.playlist import Playlists
from preferences.defaultDataConf import USER_AUDITOR_PRO
from sources.models.artists.options.artistOptions import Options
from sources.models.artists.artistPayment.payment import Payment
from sources.models.schemaValidators.validates import ValidateSchema
from sources.models.artists.history.paymentHistory import PaymentHistory
from sources.models.artists.services.artistServices import Services, ServiceSchema
from sources.models.artists.beatMakers.contractBeatmaking.contractBeatmaking import ContractBeatMaking

_f = "Reservations.artist_owner_id"
a_f = "Admiration.admire_id"
booking_f = "Reservations.auditor_who_reserve_id"
u_f = "Admiration.user_id"
_h = "PaymentHistory.artist_id"
p_f = "PaymentHistory.buyer_id"


class User(db.Model):
    """ User Model """

    # table name
    __tablename__ = 'users'

    medias = db.relationship(Media, lazy='dynamic')
    albums = db.relationship(Albums, lazy='dynamic')
    Carts = db.relationship(Carts, lazy='dynamic')
    services = db.relationship(Services, lazy='dynamic')
    options = db.relationship(Options, lazy='dynamic')
    right = db.Column(db.Integer, default=0)
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    if_choice = db.Column(db.Integer, default=0)
    user_genre_list = db.Column(db.ARRAY(db.String), default=[])
    email = db.Column(db.String(125), unique=True, nullable=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'))
    user = db.relationship('Admiration', foreign_keys=u_f, backref='user', lazy='dynamic', uselist=True)
    admire = db.relationship('Admiration', foreign_keys=a_f, backref='admire', lazy='dynamic', uselist=True)
    purchase_history = db.relationship(PaymentHistory, foreign_keys=p_f, backref='buyer', lazy='dynamic', uselist=True)
    purchased_history = db.relationship(PaymentHistory, foreign_keys=_h, backref='artist', lazy='dynamic', uselist=True)
    booking_list = db.relationship('Reservations', foreign_keys=booking_f, backref='sender_reservation', lazy='dynamic')
    reservation_list = db.relationship('Reservations', foreign_keys=_f, backref='recipient_reservation', lazy='dynamic')
    profile = db.relationship("Profiles", backref=db.backref("profiles", uselist=False))
    history = db.relationship("ArtistHistory", backref=db.backref("artist_history", uselist=False))
    reset_password_key = db.relationship("KeyResetPassword", backref=db.backref("key_reset_passwords", uselist=False))
    banking = db.relationship("BankingDetails", backref=db.backref("banking_details", uselist=False))
    payment = db.relationship(Payment, backref=db.backref("payment", uselist=False))
    condition_globals = db.relationship("ConditionGlobals", backref=db.backref("condition_globals", uselist=False))
    stars = db.relationship(Stars, backref=db.backref("stars", uselist=False))
    ContractBeat = db.relationship(ContractBeatMaking, lazy='dynamic')
    playlists = db.relationship(Playlists, lazy='dynamic')
    sender = db.relationship('Prestige', foreign_keys='Prestige.sender_id', backref='sender', lazy='dynamic')
    recipient = db.relationship('Prestige', foreign_keys='Prestige.recipient_id', backref='recipient', lazy='dynamic')
    social = db.Column(db.String(128), nullable=True)
    social_id = db.Column(db.String(128), unique=True, nullable=True)
    music_shared = db.Column(db.Integer, default=0)
    beats_shared = db.Column(db.Integer, default=0)
    album_shared = db.Column(db.Integer, default=0)
    fileStorage_key = db.Column(db.String(100), unique=True)
    user_type = db.Column(db.String(50), default=USER_AUDITOR_PRO)
    artist = db.Column(db.Integer, default=0)
    client = db.Column(db.Integer, default=0)
    password = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    # class constructor
    def __init__(self, data):
        """ Class constructor """

        self.name = data.get('name')
        self.profile_id = data.get('profile_id')
        self.email = data.get('email')
        self.social = data.get('social')
        self.user_type = data.get('user_type')
        self.social_id = data.get('social_id')
        self.artist = data.get('artist', 0)
        self.password = None if data.get('social', None) else self.generate_hash(data.get('password'))
        self.music_genres_love_list_id = None or data.get("music_genres_love_list_id")
        self.fileStorage_key = data.get('fileStorage_key')
        self.created_at = datetime.datetime.utcnow()
        self.modified_at = datetime.datetime.utcnow()

    def save(self):
        """ save a new user """

        db.session.add(self)
        db.session.commit()

    def update_password(self, password):
        """ reset a password """

        self.password = self.generate_hash(password)
        self.modified_at = datetime.datetime.utcnow()
        db.session.commit()

    def update(self, data):
        """ update a user """

        self.name = data.get('name')
        self.email = data.get('email')
        self.right = data.get('right')
        self.user_type = data.get('user_type')
        self.artist = data.get('artist')
        self.client = data.get('client')
        self.if_choice = data.get('if_choice')
        self.music_shared = data.get('music_shared')
        self.beats_shared = data.get('beats_shared')
        self.album_shared = data.get('album_shared')
        self.user_genre_list = data.get('user_genre_list')
        self.music_genres_love_list_id = data.get("music_genres_love_list_id")
        self.modified_at = datetime.datetime.utcnow()
        db.session.commit()

    def delete(self):
        """ delete user """

        db.session.delete(self)
        db.session.commit()

    def check_hash(self, password):
        """ check if password match """

        return bcrypt.check_password_hash(self.password, password)

    @staticmethod
    def generate_hash(password):
        """ generate password hash """

        return bcrypt.generate_password_hash(password, rounds=10).decode("utf-8")

    @staticmethod
    def get_one_user(user_id):
        """ get on user by user id """

        return User.query.get(user_id)

    @staticmethod
    def get_user_by_email(email):
        """ get one user by email """

        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_user_by_social_id(social_id):
        """ get user by social id """

        return User.query.filter_by(social_id=social_id).first()

    @staticmethod
    def get_len_artist():
        """ get length of artist """

        return User.query.filter_by(artist=1).count(), User.query.filter_by(artist=1).all()

    @staticmethod
    def all_beat_maker_in_three_last_month():
        """ get all BeatMaker at the six last month """

        last_6_month = datetime.datetime.now() + relativedelta(months=-6)
        return User.query.filter_by(artist=1) \
            .filter(User.created_at > last_6_month, User.beats_shared >= 1) \
            .order_by(asc(User.beats_shared)) \
            .limit(10) \
            .all()


class UserSchema(ValidateSchema):
    """ User Schema """

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    right = fields.Int(nullable=True)
    if_choice = fields.Int(nullable=True)
    password = fields.Str(required=True)
    artist = fields.Int(nullable=True)
    user_type = fields.Str(nullable=True)
    client = fields.Int(nullable=True)
    services = fields.Nested(ServiceSchema)
    music_shared = fields.Int(nullable=True)
    beats_shared = fields.Int(nullable=True)
    album_shared = fields.Int(nullable=True)
    fileStorage_key = fields.Str(nullable=True)
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)
    user_genre_list = fields.List(fields.Str(), nullable=True)
    music_genres_love_list_id = fields.Str(nullable=True)


class UserSocial(ValidateSchema):
    """ Get Social """

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Email(nullable=True)
    right = fields.Int(nullable=True)
    social = fields.Str(required=True)
    social_id = fields.Str(required=True)
    fileStorage_key = fields.Str(nullable=True)
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)


class GetMail(ValidateSchema):
    """ Get email user """

    email = fields.Email(required=True)


class GetPassword(ValidateSchema):
    """ Get Password """

    email = fields.Email(required=True)
    password = fields.Str(required=True)
