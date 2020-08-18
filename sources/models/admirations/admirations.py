#!/usr/bin/env python3
""" shebang """

from sources.models.schemaValidators.validates import ValidateSchema
from marshmallow import fields
import datetime
from sources.models import db


class Admiration(db.Model):
    """ Admiration Model """

    # table name
    __tablename__ = 'admirations'

    id = db.Column(db.BIGINT, primary_key=True)
    admire_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('medias.id'), nullable=True)
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    # class constructor
    def __init__(self, data):
        """ Class constructor """

        self.user_id = data.get('user_id')
        self.song_id = data.get('song_id') if data.get('song_id') else None
        self.admire_id = data.get('admire_id') if data.get('admire_id') else None
        self.created_at = datetime.datetime.utcnow()
        self.modified_at = datetime.datetime.utcnow()

    def save(self):
        """ save a new admiration """

        db.session.add(self)
        db.session.commit()

    def delete(self):
        """ delete a admiration """
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def user_admire_song(song_id, user_id):
        """ if exist song_id admired by user  """

        return Admiration.query.filter_by(user_id=user_id, song_id=song_id).first()


class AdmireSchema(ValidateSchema):
    """ AdmireSchema """

    id = fields.Int(dump_only=True)
    admire_id = fields.Int(allow_none=True)
    user_id = fields.Int(required=True)
    song_id = fields.Int(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)
