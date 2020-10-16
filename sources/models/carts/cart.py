#!/usr/bin/env python3
""" shebang """

from sources.models.schemaValidators.validates import ValidateSchema
from marshmallow import fields
from sources.models import db
import datetime


class Carts(db.Model):
    """ Cart Model """

    # table name
    __tablename__ = 'carts'

    id = db.Column(db.BIGINT, primary_key=True)
    beat_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    price = db.Column(db.Float())
    license = db.Column(db.String(50))
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    # class constructor
    def __init__(self, data):
        """ Class constructor """

        self.beat_id = data.get("beat_id")
        self.user_id = data.get("user_id")
        self.price = data.get("price")
        self.license = data.get("license")
        self.created_at = datetime.datetime.now()
        self.modified_at = datetime.datetime.now()

    def save(self):
        """ save an article """

        db.session.add(self)
        db.session.commit()

    def delete(self):
        """ delete an article """

        db.session.delete(self)
        db.session.commit()


class CartSchema(ValidateSchema):
    """ Cart Schema """

    user_id = fields.Int()
    id = fields.Int(dump_only=True)
    beat_id = fields.Int(required=True)
    price = fields.Float(required=False)
    license = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)
