#!/usr/bin/env python3
""" shebang """

from sources.models.schemaValidators.validates import ValidateSchema
from marshmallow import fields
import datetime
from sources.models import db


class Listened(db.Model):
    """ Listened Model """

    # table name
    __tablename__ = 'listened'

    id = db.Column(db.BIGINT, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('medias.id'), nullable=False)
    number_of_listening = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    # class constructor
    def __init__(self, data):
        """ Class constructor """

        self.user_id = data.get('user_id')
        self.song_id = data.get('song_id')
        self.number_of_listening = 1
        self.created_at = datetime.datetime.utcnow()
        self.modified_at = datetime.datetime.utcnow()

    def save(self):
        """ save a new admiration """

        db.session.add(self)
        db.session.commit()

    def update(self, data):
        """ update one listened """

        self.user_id = data.get('user_id')
        self.song_id = data.get('song_id')
        self.number_of_listening = data.get('number_of_listening')
        self.modified_at = datetime.datetime.utcnow()
        db.session.commit()

    def delete(self):
        """ delete a admiration """
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def user_admire_song(song_id, user_id):
        """ if exist song_id admired by user  """

        return Listened.query.filter_by(user_id=user_id, song_id=song_id).first()


class ListenedSchema(ValidateSchema):
    """ ListenedSchema """

    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    song_id = fields.Int(required=True)
    number_of_listening = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)
