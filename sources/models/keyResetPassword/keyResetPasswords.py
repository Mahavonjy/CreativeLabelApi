#!/usr/bin/env python3
""" shebang """

from sources.models.schemaValidators.validates import ValidateSchema
from marshmallow import fields
from sources.models import db
import datetime


class KeyResetPassword(db.Model):
    """ table for logout """

    __tablename__ = 'key_reset_passwords'

    id = db.Column(db.Integer, primary_key=True)
    keys = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, unique=True)
    password_reset = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    def __init__(self, data):
        self.keys = data["keys"]
        self.user_id = data["user_id"]
        try: self.password_reset = data["password_reset"]
        except KeyError: self.password_reset = 0
        self.created_at = datetime.datetime.utcnow()
        self.modified_at = datetime.datetime.utcnow()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, data):
        self.keys = data["keys"]
        self.user_id = data["user_id"]
        try: self.password_reset = data["password_reset"]
        except KeyError: self.password_reset = 0
        self.modified_at = datetime.datetime.utcnow()
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_by_user_id(user_id):
        return KeyResetPassword.query.filter_by(user_id=user_id).first()


class ResetPassword(ValidateSchema):
    """ KeyResetPassword schema"""

    id = fields.Int(dump_only=True)
    keys = fields.Int(required=True)
    password_reset = fields.Int(allow_none=True)
    user_id = fields.Int(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)


class GetKeys(ValidateSchema):
    """ Get keys if is validate schema"""

    keys = fields.Int(required=True)
    email = fields.Email(required=True)
