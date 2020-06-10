#!/usr/bin/env python3
""" shebang """

import datetime

from sqlalchemy import desc
from sqlalchemy.dialects.postgresql import JSON
from sources.models import db
from sources.models.schemaValidators.validates import ValidateSchema
from marshmallow import fields


class ArtistHistory(db.Model):
    """ Artist """

    # table name
    __tablename__ = 'artist_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    months_story = db.Column(JSON, default={})
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    # class constructor
    def __init__(self, data):
        """ Class constructor """

        self.user_id = data.get('user_id')
        self.months_story = data.get('months_story')
        self.created_at = datetime.datetime.utcnow()
        self.modified_at = datetime.datetime.utcnow()

    def save(self):
        """
            save artist story
        """
        db.session.add(self)
        db.session.commit()

    def update(self, data):
        """
            update a payment
        """

        self.months_story = data.get('months_story')
        self.modified_at = datetime.datetime.utcnow()
        db.session.commit()

    def delete(self):
        """
            delete a payment
        """

        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_by_user_id(user_id):
        """

        :param user_id:
        :return: model of ArtistHistory if exist
        """
        return ArtistHistory.query.filter_by(user_id=user_id).first()

    @staticmethod
    def top_last():
        """

        :return: 10 new artist
        """
        return ArtistHistory.query \
            .order_by(desc(ArtistHistory.created_at)) \
            .limit(10) \
            .all()

    @staticmethod
    def get_all():
        """

        :return: list of all month story
        """
        return ArtistHistory.query.all()


class ArtistHistorySchema(ValidateSchema):
    """
        history Schema
    """

    id = fields.Int(dump_only=True)
    months_story = fields.Dict(nullable=True)
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)

