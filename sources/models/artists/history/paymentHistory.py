#!/usr/bin/env python3
""" shebang """

from sources.models.schemaValidators.validates import ValidateSchema
from marshmallow import fields
from sources.models import db
import datetime


class PaymentHistory(db.Model):
    """ Payment history Model """

    # table name
    __tablename__ = 'payment_history'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    media_id = db.Column(db.Integer, db.ForeignKey('medias.id'), nullable=True)
    reference = db.Column(db.String(100))
    name = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.Integer, nullable=False)
    phone = db.Column(db.String(200), nullable=True, default="")
    ip_address = db.Column(db.String(100))
    artist_amount = db.Column(db.Float(), nullable=True)
    type = db.Column(db.String(150))
    paid = db.Column(db.BOOLEAN, default=False)
    service_fee = db.Column(db.BOOLEAN, default=False)
    refund = db.Column(db.BOOLEAN, default=False)
    tva = db.Column(db.Float(), nullable=True)
    isl_amount = db.Column(db.Float(), nullable=True)
    total_amount = db.Column(db.Float(), nullable=True)
    licenses_name = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)
    media = db.relationship("Media", backref=db.backref("media_payment_story", uselist=False))

    # class constructor
    def __init__(self, data):
        """ Class constructor """

        self.tva = data.get('tva')
        self.type = data.get('type')
        self.name = data.get('name')
        self.paid = data.get('paid')
        self.service_fee = data.get('service_fee')
        self.refund = data.get('refund')
        self.lastname = data.get('lastname')
        self.email = data.get('email')
        self.address = data.get('address')
        self.city = data.get('city')
        self.postal_code = data.get('postal_code')
        self.phone = data.get('phone')
        self.ip_address = data.get('ip_address')
        self.buyer_id = data.get('buyer_id')
        self.artist_id = data.get('artist_id')
        self.reference = data.get('reference')
        self.isl_amount = data.get('isl_amount')
        self.media_id = data.get('media_id')
        self.total_amount = data.get('total_amount')
        self.licenses_name = data.get('licenses_name')
        self.artist_amount = data.get('artist_amount')
        self.created_at = datetime.datetime.utcnow()
        self.modified_at = datetime.datetime.utcnow()

    def save(self):
        """save a new payment """

        db.session.add(self)
        db.session.commit()

    def update(self, data):
        """ update a payment """

        self.tva = data.get('tva')
        self.type = data.get('type')
        self.name = data.get('name')
        self.paid = data.get('paid')
        self.service_fee = data.get('service_fee')
        self.refund = data.get('refund')
        self.lastname = data.get('lastname')
        self.email = data.get('email')
        self.address = data.get('address')
        self.city = data.get('city')
        self.postal_code = data.get('postal_code')
        self.phone = data.get('phone')
        self.media_id = data.get('media_id')
        self.ip_address = data.get('ip_address')
        self.buyer_id = data.get('buyer_id')
        self.artist_id = data.get('artist_id')
        self.reference = data.get('reference')
        self.isl_amount = data.get('isl_amount')
        self.total_amount = data.get('total_amount')
        self.licenses_name = data.get('licenses_name')
        self.artist_amount = data.get('artist_amount')
        self.modified_at = datetime.datetime.utcnow()
        db.session.commit()

    def delete(self):
        """ delete a payment """

        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_payment_history_by_id(payment_history_id):
        """ get a payment by id """

        return PaymentHistory.query.filter_by(id=payment_history_id).first()

    @staticmethod
    def get_payment_history_by_reference(reference):
        """ get a payment by reference """

        return PaymentHistory.query.filter_by(reference=reference).first()


class PaymentHistorySchema(ValidateSchema):
    """ Payment history Schema """

    lastname = fields.Str()
    id = fields.Int(dump_only=True)
    tva = fields.Float(required=True)
    total_amount = fields.Float(required=True)
    isl_amount = fields.Float(required=True)
    artist_amount = fields.Float(required=True)
    licenses_name = fields.Str(nullable=True)
    paid = fields.Boolean(nullable=True)
    service_fee = fields.Boolean(nullable=True)
    refund = fields.Boolean(nullable=True)
    type = fields.Str(required=True)
    reference = fields.Str(required=True)
    name = fields.Str(required=True)
    email = fields.Str(required=True)
    address = fields.Str(required=True)
    city = fields.Str(required=True)
    postal_code = fields.Int(required=True)
    buyer_id = fields.Int(nullable=True)
    media_id = fields.Int(nullable=True)
    ip_address = fields.Str(nullable=True)
    artist_id = fields.Int(required=True)
    phone = fields.String(nullable=True, required=False)
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)
