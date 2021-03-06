#!/usr/bin/env python3
""" shebang """

from sources.models.schemaValidators.validates import ValidateSchema
from marshmallow import fields
import datetime
from sources.models import db


class Prestige(db.Model):
    """ Prestige Model """

    # table name
    __tablename__ = 'prestige_moneys'

    id = db.Column(db.Integer, primary_key=True)
    key_share = db.Column(db.String(255))
    prestige = db.Column(db.String(125))
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    beat_id = db.Column(db.Integer, db.ForeignKey('medias.id'), nullable=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=True)
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    # class constructor
    def __init__(self, data):
        """ Class constructor """

        self.key_share = data.get('key_share')
        self.prestige = data.get('prestige')
        self.sender_id = data.get('sender_id')
        self.recipient_id = data.get('recipient_id')
        self.beat_id = data.get('beat_id')
        self.service_id = data.get('service_id')
        self.created_at = datetime.datetime.utcnow()
        self.modified_at = datetime.datetime.utcnow()

    def save(self):
        """ sav a prestige """

        db.session.add(self)
        db.session.commit()

    def delete(self):
        """ delete an prestige """

        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_all_transaction():
        """ check all prestige """

        return Prestige.query.all()


class PrestigeSchema(ValidateSchema):
    """ Prestige Schema """

    id = fields.Int(dump_only=True)
    key_share = fields.Str(required=True)
    sender_id = fields.Int(required=True)
    recipient_id = fields.Int(required=True)
    beat_id = fields.Int(required=True)
    service_id = fields.Int(required=True)
    prestige = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)
