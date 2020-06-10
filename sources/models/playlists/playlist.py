#!/usr/bin/env python3
""" shebang """

import datetime
from sources.models.schemaValidators.validates import ValidateSchema
from sources.models import db
from marshmallow import fields


class Playlists(db.Model):
    """ Albums Model """

    # table name
    __tablename__ = 'playlists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(125))
    photo = db.Column(db.String(255), nullable=True)
    photo_storage_name = db.Column(db.String(255), nullable=True)
    description = db.Column(db.String(255), nullable=True)
    genre = db.Column(db.String(155), nullable=True)
    number_views = db.Column(db.Integer, default=0)
    status = db.Column(db.String(125))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    song_id_list = db.Column(db.ARRAY(db.Integer), default=[])
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    # class constructor
    def __init__(self, data):
        """ Class constructor """

        self.user_id = data.get('user_id')
        self.name = data.get('name')
        self.description = data.get('description')
        self.status = data.get('status') if data.get('status') else "Public"
        self.photo = data.get('photo')
        self.photo_storage_name = data.get('photo_storage_name')
        self.genre = data.get('genre')
        self.created_at = datetime.datetime.utcnow()
        self.modified_at = datetime.datetime.utcnow()

    def save(self):
        """ save a playlist """

        db.session.add(self)
        db.session.commit()

    def update(self, data):
        """ update a playlist """
        self.name = data.get('name')
        self.photo = data.get('photo')
        self.photo_storage_name = data.get('photo_storage_name')
        self.description = data.get('description')
        self.genre = data.get('genre')
        self.song_id_list = data.get('song_id_list')
        self.number_views = data.get('number_views')
        self.status = data.get('status')
        self.modified_at = datetime.datetime.utcnow()
        db.session.commit()

    def delete(self):
        """ delete a playlist """

        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_all_user_playlist(id_user):
        """ all user playlist"""

        return Playlists.query.filter_by(user_id=id_user).all()

    @staticmethod
    def get_playlist(playlist_id):
        """ one playlist """

        return Playlists.query.filter_by(id=playlist_id).first()

    @staticmethod
    def if_is_exist(id_user, playlist_name):
        """ if a playlist exist """

        return Playlists.query.filter_by(user_id=id_user, name=playlist_name).first()


class PlaylistSchema(ValidateSchema):
    """ Media Schema """

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(nullable=True)
    genre = fields.Str(nullable=True)
    photo = fields.Str(nullable=True)
    photo_storage_name = fields.Str(nullable=True)
    number_views = fields.Int(nullable=True)
    status = fields.Str(nullable=True)
    user_id = fields.Int(nullable=True)
    song_id_list = fields.List(fields.Int(), nullable=True)
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)
