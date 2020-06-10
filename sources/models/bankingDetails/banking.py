#!/usr/bin/env python3
""" shebang """

import datetime
from sources.models import db
from marshmallow import fields
from sources.models.schemaValidators.validates import ValidateSchema


class BankingDetails(db.Model):
    """ Materials Model """

    __tablename__ = 'banking_details'

    id = db.Column(db.BIGINT, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    rules = db.Column(db.BOOLEAN, nullable=False)
    lastname = db.Column(db.String(200))
    country = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(125), nullable=True)
    iban = db.Column(db.String(125), nullable=False)
    swift = db.Column(db.String(125), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    email = db.Column(db.String(125), nullable=False)
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    # class constructor
    def __init__(self, data):
        """ Class constructor """

        self.name = data.get('name')
        self.rules = data.get('rules')
        self.country = data.get('country')
        self.phone = data.get('phone')
        self.lastname = data.get('lastname')
        self.iban = data.get('iban')
        self.swift = data.get('swift')
        self.email = data.get('email')
        self.user_id = data.get('user_id')
        self.created_at = datetime.datetime.utcnow()
        self.modified_at = datetime.datetime.utcnow()

    def save(self):
        """ save a Materials """

        db.session.add(self)
        db.session.commit()

    def update(self, data):
        """ update a Materials """

        self.name = data.get('name')
        self.rules = data.get('rules')
        self.country = data.get('country')
        self.phone = data.get('phone')
        self.lastname = data.get('lastname')
        self.iban = data.get('iban')
        self.swift = data.get('swift')
        self.email = data.get('email')
        self.user_id = data.get('user_id')
        self.modified_at = datetime.datetime.utcnow()
        db.session.commit()

    def delete(self):
        """ delete a user Materials """

        db.session.delete(self)
        db.session.commit()


class BankingSchema(ValidateSchema):
    """ Banking Schema """

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    iban = fields.Str(required=True)
    swift = fields.Str(required=True)
    country = fields.Str(required=True)
    user_id = fields.Int(required=False)
    email = fields.Email(required=True)
    phone = fields.String(nullable=True)
    lastname = fields.Str(required=False)
    rules = fields.Boolean(required=True)
    created_at = fields.DateTime(dump_only=True)  # created date for service
    modified_at = fields.DateTime(dump_only=True)  # date who modified this service
