#!/usr/bin/env python3
""" shebang """

import datetime
from sources.models import db
from sqlalchemy import func, desc, asc
from marshmallow import fields
from sources.models.medias.media import Media
from dateutil.relativedelta import relativedelta
from sources.models.search.basicSearch import update_doc, add_new_doc
from sources.models.prestigeMoneys.prestigeMoneys import Prestige
from sources.models.schemaValidators.validates import ValidateSchema


class Albums(db.Model):
    """ Albums Model """

    # table name
    __tablename__ = 'albums'

    id = db.Column(db.Integer, primary_key=True)
    album_name = db.Column(db.String(125), nullable=True)
    album_photo = db.Column(db.String(255), nullable=True)
    description = db.Column(db.String(255), nullable=True)
    prestige = db.relationship(Prestige, lazy='dynamic')
    genre = db.Column(db.String(155), nullable=False)
    genre_musical = db.Column(db.String(255))
    stream_total = db.Column(db.Integer, default=0)
    number_songs = db.Column(db.Integer)
    artist = db.Column(db.String(125))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    medias = db.relationship(Media, cascade="all, delete, save-update", lazy='dynamic')
    keys = db.Column(db.Integer, unique=True)
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    # class constructor
    def __init__(self, data):
        """ Class constructor """

        self.user_id = data.get('user_id')
        self.album_photo = data.get('album_photo')
        self.album_name = data.get('album_name')
        self.description = data.get('description')
        self.number_songs = data.get('number_songs')
        self.artist = data.get('artist')
        self.genre_musical = data.get('genre_musical')
        self.genre = data.get('genre')
        self.keys = data.get('keys')
        self.stream_total = 0
        self.created_at = datetime.datetime.utcnow()
        self.modified_at = datetime.datetime.utcnow()

    def save(self):
        """ save an album """

        db.session.add(self)
        db.session.commit()
        add_new_doc(self, AlbumSchema(), index="albums_and_songs", doc_type="albums")

    def update(self, data):
        """ update an album """

        self.album_name = data.get('album_name')
        self.stream_total = data.get('stream_total')
        self.album_photo = data.get('album_photo')
        self.description = data.get('description')
        self.genre_musical = data.get('genre_musical')
        self.genre = data.get('genre')
        self.number_songs = data.get('number_songs')
        self.artist = data.get('artist')
        self.keys = data.get('keys')
        self.modified_at = datetime.datetime.utcnow()
        db.session.commit()
        update_doc(self, AlbumSchema(), index="albums_and_songs", doc_type="albums")

    def delete(self):
        """ delete an album """

        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_all_albums():
        """ ge all albums < 15 """

        return Albums.query.all()

    @staticmethod
    def get_album_info(keys):
        """ get one album by keys """

        return Albums.query.filter_by(keys=keys).first()

    @staticmethod
    def get_album_id(id_album):
        """ get one album by id """

        return Albums.query.filter_by(id=id_album).first()

    @staticmethod
    def get_album_genre(genre):
        """ get all album by genre """

        return Albums.query.filter_by(genre=genre).all()

    @staticmethod
    def get_len_table():
        """ get length of table """

        return db.session.query(func.count(Albums.id)).scalar()

    @staticmethod
    def album_in_the_last_1_year():
        """ get all albums who uploaded in the 3 last month """

        last_4_month = datetime.datetime.now() + relativedelta(months=-4)
        return Albums.query\
            .filter(Albums.created_at > last_4_month)\
            .order_by(desc(Albums.stream_total))\
            .limit(10)\
            .all()

    @staticmethod
    def ten_last_albums():
        """ get all news albums """

        return Albums.query\
            .order_by(asc(Albums.created_at))\
            .limit(10)\
            .all()


class AlbumSchema(ValidateSchema):
    """ Media Schema """

    id = fields.Int(dump_only=True)
    description = fields.Str(required=True)
    artist = fields.Str(required=True)
    album_name = fields.Str(required=True)
    album_photo = fields.Str(allow_none=True)
    album_id = fields.Str(allow_none=True)
    genre_musical = fields.Str(required=True)
    genre = fields.Str(required=True)
    number_songs = fields.Int(allow_none=True)
    stream_total = fields.Int(allow_none=True)
    user_id = fields.Int(allow_none=True)
    keys = fields.Int(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)
