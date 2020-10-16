#!/usr/bin/env python3
""" shebang """

import datetime

from dateutil.relativedelta import relativedelta
from marshmallow import fields

from preferences import USER_AUDITOR_PRO, USER_ARTIST_BEATMAKER
from sources.app import bcrypt
from sources.models import db
from sources.models.artists.artistPayment.payment import Payment
from sources.models.artists.beatMakers.contractBeatmaking.contractBeatmaking import ContractBeatMaking
from sources.models.artists.history.paymentHistory import PaymentHistory
from sources.models.artists.options.artistOptions import Options
from sources.models.artists.services.artistServices import Services, ServiceSchema
from sources.models.carts.cart import Carts
from sources.models.medias.media import Media
from sources.models.schemaValidators.validates import ValidateSchema
from sources.models.stars.noteStars import Stars

_f = "Reservations.artist_owner_id"
booking_f = "Reservations.auditor_who_reserve_id"
u_f = "Admiration.user_id"
a_f = "Admiration.admire_id"
_h = "PaymentHistory.artist_id"
p_f = "PaymentHistory.buyer_id"


class User(db.Model):
    """ User Model """

    # table name
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    right = db.Column(db.Integer, default=0)
    name = db.Column(db.String(128))
    if_choice = db.Column(db.Integer, default=0)
    beats_id_liked_list = db.Column(db.ARRAY(db.Integer), default=[])
    beats_id_listened_list = db.Column(db.ARRAY(db.Integer), default=[])
    email = db.Column(db.String(125), unique=True, nullable=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'))
    social = db.Column(db.String(128), nullable=True)
    social_id = db.Column(db.String(128), unique=True, nullable=True)
    fileStorage_key = db.Column(db.String(100), unique=True)
    user_type = db.Column(db.String(50), default=USER_AUDITOR_PRO)
    password = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    # All Users Relationship
    medias = db.relationship(Media, lazy='dynamic')
    carts = db.relationship(Carts, lazy='dynamic')
    services = db.relationship(Services, lazy='dynamic')
    options = db.relationship(Options, lazy='dynamic')
    all_admires = db.relationship('Admiration', foreign_keys=u_f, backref='user', lazy='dynamic', uselist=True)
    my_admirers = db.relationship('Admiration', foreign_keys=a_f, backref='admire', lazy='dynamic', uselist=True)
    purchase_history = db.relationship(PaymentHistory, foreign_keys=p_f, backref='buyer', lazy='dynamic', uselist=True)
    purchased_history = db.relationship(PaymentHistory, foreign_keys=_h, backref='artist', lazy='dynamic', uselist=True)
    booking_list = db.relationship('Reservations', foreign_keys=booking_f, backref='sender_reservation', lazy='dynamic')
    reservation_list = db.relationship('Reservations', foreign_keys=_f, backref='recipient_reservation', lazy='dynamic')
    profile = db.relationship("Profiles", backref=db.backref("profiles", uselist=False))
    reset_password_key = db.relationship("KeyResetPassword", backref=db.backref("key_reset_passwords", uselist=False))
    banking = db.relationship("BankingDetails", backref=db.backref("banking_details", uselist=False))
    payment = db.relationship(Payment, backref=db.backref("payment", uselist=False))
    condition_globals = db.relationship("ConditionGlobals", backref=db.backref("condition_globals", uselist=False))
    stars = db.relationship(Stars, backref=db.backref("stars", uselist=False))
    ContractBeat = db.relationship(ContractBeatMaking, lazy='dynamic')
    prestige_sends = db.relationship('Prestige', foreign_keys='Prestige.sender_id', backref='sender', lazy='dynamic')
    prestige_receipts = db.relationship(
        'Prestige',
        foreign_keys='Prestige.recipient_id',
        backref='recipient',
        lazy='dynamic'
    )

    # class constructor
    def __init__(self, data):
        """ Class constructor """

        self.name = data.get('name')
        self.profile_id = data.get('profile_id')
        self.email = data.get('email')
        self.social = data.get('social')
        self.user_type = data.get('user_type')
        self.social_id = data.get('social_id')
        self.password = None if data.get('social', None) else self.generate_hash(data.get('password'))
        self.beats_id_liked_list = data.get("beats_id_liked_list", None)
        self.beats_id_listened_list = data.get("beats_id_listened_list", None)
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
        """

        Args:
            data:
        """
        self.name = data.get('name')
        self.email = data.get('email')
        self.right = data.get('right')
        self.user_type = data.get('user_type')
        self.if_choice = data.get('if_choice')
        self.beats_id_liked_list = data.get("beats_id_liked_list")
        self.beats_id_listened_list = data.get("beats_id_listened_list")
        self.modified_at = datetime.datetime.utcnow()
        db.session.commit()

    def delete(self):
        """ delete user """

        db.session.delete(self)
        db.session.commit()

    def check_hash(self, password):
        """

        Args:
            password:

        Returns:

        """
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
    def all_beat_maker_in_three_last_month():
        """ get all BeatMaker at the six last month """

        last_6_month = datetime.datetime.now() + relativedelta(months=-6)
        return User.query.filter(User.created_at > last_6_month, User.user_type == USER_ARTIST_BEATMAKER) \
            .limit(10) \
            .all()


class UserSchema(ValidateSchema):
    """ User Schema """

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    right = fields.Int(allow_none=True)
    if_choice = fields.Int(allow_none=True)
    password = fields.Str(required=True)
    user_type = fields.Str(allow_none=True)
    services = fields.Nested(ServiceSchema)
    fileStorage_key = fields.Str(allow_none=True)
    beats_id_liked_list = fields.List(fields.Int(), allow_none=True)
    beats_id_listened_list = fields.List(fields.Int(), allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)


class UserSocial(ValidateSchema):
    """ Get Social """

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Email(allow_none=True)
    right = fields.Int(allow_none=True)
    social = fields.Str(required=True)
    social_id = fields.Str(required=True)
    fileStorage_key = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)


class GetMail(ValidateSchema):
    """ Get email user """

    email = fields.Email(required=True)


class GetPassword(ValidateSchema):
    """ Get Password """

    email = fields.Email(required=True)
    password = fields.Str(required=True)
