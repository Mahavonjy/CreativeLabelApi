#!/usr/bin/env python3
""" shebang """

import datetime
from sources.models import db
from marshmallow import fields
from sources.models.schemaValidators.validates import ValidateSchema
from sqlalchemy.dialects.postgresql import JSON


class Stars(db.Model):
    """
        Globals condition for all type of artist
    """

    # table name
    __tablename__ = 'stars'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), unique=True, nullable=True)
    note = db.Column(db.ARRAY(db.Integer), default=[])
    users_who_rated = db.Column(JSON, default={})
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    # class constructor
    def __init__(self, data):
        """ Class constructor """

        self.note = data.get('note')
        self.user_id = data.get('user_id')
        self.service_id = data.get('service_id')
        self.users_who_rated = data.get('users_who_rated', {})
        self.created_at = datetime.datetime.utcnow()
        self.modified_at = datetime.datetime.utcnow()

    def save(self):
        """ save a playlist """

        db.session.add(self)
        db.session.commit()

    def update(self, data):
        """
            Update a user notes condition
        """

        self.note = data.get('note')
        self.service_id = data.get('service_id')
        self.users_who_rated = data.get('users_who_rated')
        self.modified_at = datetime.datetime.utcnow()
        db.session.commit()

    def delete(self):
        """ delete a playlist """

        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_stars_by_user_id(user_id):
        """
            check notes user_id
        """

        return Stars.query.filter_by(user_id=user_id).first()


    @staticmethod
    def get_stars_by_service_id(service_id):
        """
            check notes by service_id
        """

        return Stars.query.filter_by(service_id=service_id).first()


class StarSchema(ValidateSchema):
    """ Condition Globals Schema """

    id = fields.Int(dump_only=True)
    note = fields.List(fields.Int(), required=True)
    user_id = fields.Int(allow_none=True)
    service_id = fields.Int(allow_none=True)
    users_who_rated = fields.Dict(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)
