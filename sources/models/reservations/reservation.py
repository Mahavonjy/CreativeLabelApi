#!/usr/bin/env python3
""" shebang """

from preferences import PENDING
from sources.models.schemaValidators.validates import ValidateSchema
from marshmallow import fields
from sources.models import db
import datetime


class Reservations(db.Model):
    """ Reservations Model """

    # table name
    __tablename__ = 'reservations'

    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(50), nullable=False)
    event_date = db.Column(db.DateTime, nullable=False)
    invoice = db.Column(db.String(255), nullable=True)
    payment_history_id = db.Column(db.Integer, db.ForeignKey('payment_history.id'))
    services_id = db.Column(db.Integer, db.ForeignKey('services.id'))
    auditor_who_reserve_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    artist_owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.String(10), nullable=False, default=PENDING)
    options_id_list = db.Column(db.ARRAY(db.Integer), default=[])
    total_amount = db.Column(db.Float(), nullable=True)
    address = db.Column(db.String(200), nullable=False)
    refund_policy = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)
    payment_history = db.relationship("PaymentHistory", backref=db.backref("reservation_payment_story", uselist=False))
    service = db.relationship(
        "Services", cascade="all, delete, save-update", backref=db.backref("service_reservation", uselist=False)
    )

    # class constructor
    def __init__(self, data):
        """ Class constructor """

        self.event = data.get('event')
        self.status = data.get('status')
        self.address = data.get("address")
        self.refund_policy = data.get("refund_policy")
        self.event_date = data.get('event_date')
        self.services_id = data.get("services_id")
        self.invoice = data.get("invoice")
        self.payment_history_id = data.get("payment_history_id")
        self.auditor_who_reserve_id = data.get("auditor_who_reserve_id")
        self.artist_owner_id = data.get("artist_owner_id")
        self.options_id_list = data.get("options_id_list")
        self.total_amount = data.get('total_amount')
        self.created_at = datetime.datetime.utcnow()
        self.modified_at = datetime.datetime.utcnow()

    def save(self):
        """save a new reservation """

        db.session.add(self)
        db.session.commit()

    def update(self, data):
        """ update a reservation """

        self.event = data.get('event')
        self.status = data.get('status')
        self.address = data.get("address")
        self.event_date = data.get('event_date')
        self.refund_policy = data.get('refund_policy')
        self.services_id = data.get("services_id")
        self.invoice = data.get("invoice")
        self.payment_history_id = data.get("payment_history_id")
        self.auditor_who_reserve_id = data.get("auditor_who_reserve_id")
        self.artist_owner_id = data.get("artist_owner_id")
        self.options_id_list = data.get("options_id_list")
        self.total_amount = data.get('total_amount')
        self.modified_at = datetime.datetime.utcnow()
        db.session.commit()

    def delete(self):
        """ delete one media """

        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_reservation_by_payment_history_id(payment_history_id):
        """ get by payment by id """

        return Reservations.query.filter_by(payment_history_id=payment_history_id).first()


class ReservationSchema(ValidateSchema):
    """ Reservation Schema """

    id = fields.Int(dump_only=True)
    event = fields.Str(required=True)
    status = fields.Str(allow_none=True)
    address = fields.Str(required=True)
    name = fields.Str(allow_none=True)
    lastname = fields.Str(allow_none=True)
    email = fields.Str(allow_none=True)
    invoice = fields.Str(allow_none=True)
    city = fields.Str(allow_none=True)
    postal_code = fields.Int(allow_none=True)
    phone = fields.String(allow_none=True)
    services_id = fields.Int(allow_none=False)
    total_amount = fields.Float(required=True)
    event_date = fields.DateTime(required=True)
    artist_owner_id = fields.Int(allow_none=False)
    stripe_token = fields.Dict(allow_none=True)
    payment_history_id = fields.Int(allow_none=False)
    auditor_who_reserve_id = fields.Int(allow_none=False)
    options_id_list = fields.List(fields.Int(), allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)


class ReservationRSchema(ValidateSchema):
    """ Reservation to basic return Schema """

    id = fields.Int(dump_only=True)
    event = fields.Str(required=True)
    status = fields.Str(allow_none=True)
    address = fields.Str(required=True)
    invoice = fields.Str(allow_none=True)
    services_id = fields.Int(allow_none=False)
    total_amount = fields.Float(required=True)
    event_date = fields.DateTime(dump_only=True)
    artist_owner_id = fields.Int(allow_none=False)
    stripe_token = fields.Dict(allow_none=True)
    refund_policy = fields.Str(required=False)
    payment_history_id = fields.Int(allow_none=False)
    auditor_who_reserve_id = fields.Int(allow_none=False)
    options_id_list = fields.List(fields.Int(), allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)