#!/usr/bin/env python3
""" shebang """

import datetime
from sources.models import db
from sources.models.schemaValidators.validates import ValidateSchema
from marshmallow import fields


class SupportMessages(db.Model):
    """ of Support messages """

    # table name
    __tablename__ = 'messages'

    id = db.Column(db.BIGINT, primary_key=True)
    title = db.Column(db.String(125), nullable=False)
    user_email = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text(), nullable=False)
    resolved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    # class constructor
    def __init__(self, data):
        """ Class constructor """

        self.title = data.get('title')
        self.user_email = data.get('user_email')
        self.message = data.get('gender')
        self.created_at = datetime.datetime.utcnow()
        self.modified_at = datetime.datetime.utcnow()

    def save(self):
        """ save a message """

        db.session.add(self)
        db.session.commit()

    def update(self, data):
        """ update a message """

        self.title = data.get('title')
        self.user_email = data.get('user_email')
        self.message = data.get('gender')
        self.modified_at = datetime.datetime.utcnow()
        db.session.commit()

    def delete(self):
        """ delete a message """

        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_message_by_id(support_message_id):
        """ get one support message """

        return SupportMessages.query.filter_by(id=support_message_id).first()

    @staticmethod
    def get_support_message_resolved():
        """ get all support message resolved """

        return SupportMessages.query.filter_by(resolved=True).all()

    @staticmethod
    def get_support_message_not_resolved():
        """ get all support message resolved """

        return SupportMessages.query.filter_by(resolved=False).all()


class SupportMessagesSchema(ValidateSchema):
    """ Profile Schema """

    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    user_email = fields.Str(required=True)
    message = fields.Str(required=True)
    resolved = fields.Boolean(nullable=True)
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)
