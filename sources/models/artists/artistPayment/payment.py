#!/usr/bin/env python3
""" shebang """

from sources.models.schemaValidators.validates import ValidateSchema
from marshmallow import fields
from sources.models import db
import datetime


class Payment(db.Model):
    """ Payment Model """

    # table name
    __tablename__ = 'payment'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reference = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float(), nullable=False)
    type = db.Column(db.String(150), nullable=False)
    licenses_name = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    # class constructor
    def __init__(self, data):
        """ Class constructor """

        self.artist_id = data.get('artist_id')
        self.amount = data.get('amount')
        self.type = data.get('type')
        self.licenses_name = data.get('licenses_name')
        self.reference = data.get('reference')
        self.created_at = datetime.datetime.utcnow()
        self.modified_at = datetime.datetime.utcnow()

    def save(self):
        """save a new payment """

        db.session.add(self)
        db.session.commit()

    def update(self, data):
        """ update a payment """

        self.artist_id = data.get('artist_id')
        self.amount = data.get('amount')
        self.type = data.get('type')
        self.licenses_name = data.get('licenses_name')
        self.reference = data.get('reference')
        self.modified_at = datetime.datetime.utcnow()
        db.session.commit()

    def delete(self):
        """ delete a payment """

        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_payment_by_id(payment_id):
        """ get a payment by id """

        return Payment.query.filter_by(id=payment_id).first()

    @staticmethod
    def get_payment_by_reference(reference):
        """ get a payment by reference """

        return Payment.query.filter_by(reference=reference).first()


class PaymentSchema(ValidateSchema):
    """ Payment Schema """

    id = fields.Int(dump_only=True)
    amount = fields.Float(required=True)
    type = fields.Str(required=True)
    licenses_name = fields.Str(required=True)
    reference = fields.Str(required=True)
    artist_id = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)
