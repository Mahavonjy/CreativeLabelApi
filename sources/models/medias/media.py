#!/usr/bin/env python3
""" shebang """

from sources.models.prestigeMoneys.prestigeMoneys import Prestige
from sources.models.search.basicSearch import add_new_doc, update_doc
from sources.models.medias.mediaListened import Listened
from sources.models.admirations.admirations import Admiration
from dateutil.relativedelta import relativedelta
from preferences import defaultDataConf
from sqlalchemy import desc, asc, func
from sources.models.schemaValidators.validates import ValidateSchema
from marshmallow import fields
from sources.models import db
import datetime


class Media(db.Model):
    """ Media Model """

    # table name
    __tablename__ = 'medias'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    photo = db.Column(db.String(255), nullable=True)
    genre_musical = db.Column(db.String(255))
    basic_price = db.Column(db.Float(), nullable=True)
    silver_price = db.Column(db.Float(), nullable=True)
    gold_price = db.Column(db.Float(), nullable=True)
    platinum_price = db.Column(db.Float(), nullable=True)
    prestige = db.relationship(Prestige, lazy='dynamic', cascade="all, delete, save-update")
    admire = db.Column(db.Integer, default=0)
    admiration = db.relationship(Admiration, cascade="all, delete, save-update", lazy='dynamic')
    genre = db.Column(db.String(155), nullable=False)
    artist = db.Column(db.String(125), nullable=False)
    artist_tag = db.Column(db.String(255), nullable=True)
    stems = db.Column(db.String(255), nullable=True)
    beats_wave = db.Column(db.String(255), nullable=True)
    album_id = db.Column(db.Integer, db.ForeignKey('albums.id'), nullable=True)
    album_song = db.Column(db.Boolean, default=False)
    share = db.Column(db.Integer, default=0)
    storage_name = db.Column(db.String(255))
    time = db.Column(db.String(10))
    in_playlist = db.Column(db.Integer, default=0)
    pres_listened = db.Column(db.Integer, default=0)
    number_play = db.Column(db.Integer, default=0)
    bpm = db.Column(db.Float, default=0.0)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    listened = db.relationship(Listened, cascade="all, delete, save-update", lazy='dynamic')
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    # class constructor
    def __init__(self, data):
        """ Class constructor """

        self.user_id = data.get('user_id')
        self.title = data.get('title', data.get('Title'))
        self.in_playlist = 0
        self.pres_listened = 0
        if data.get('album_id'):
            self.album_id = data.get('album_id')
            self.album_song = True
        self.number_play = 0
        self.photo = data.get('photo')
        self.bpm = data.get('bpm', 0)
        self.time = data.get('time')
        self.stems = data.get('stems')
        self.share = data.get('share')
        self.beats_wave = data.get('beats_wave')
        self.artist_tag = data.get('artist_tag')
        self.description = data.get('description') if data.get('description') else data.get('Description')
        self.artist = data.get('artist', data.get('Artist'))
        self.genre_musical = data.get('genre_musical', data.get('Genre_musical'))
        self.basic_price = data.get('basic_price', None)
        self.silver_price = data.get('silver_price', None)
        self.gold_price = data.get('gold_price', None)
        self.platinum_price = data.get('platinum_price', None)
        self.genre = data.get('genre') if data.get('genre') else data.get('Genre')
        self.storage_name = data.get('storage_name')
        self.created_at = datetime.datetime.utcnow()
        self.modified_at = datetime.datetime.utcnow()

    def save(self):
        """save a new media """

        db.session.add(self)
        db.session.commit()
        add_new_doc(self, MediaSchema(), index="albums_and_songs", doc_type="songs")

    def update(self, data):
        """ update one media """

        self.title = data.get('title')
        self.bpm = data.get('bpm')
        self.description = data.get('description')
        self.genre_musical = data.get('genre_musical')
        self.in_playlist = data.get('in_playlist')
        self.artist = data.get('artist')
        self.photo = data.get('photo')
        self.genre = data.get('genre')
        self.admire = data.get('admire')
        self.basic_price = data.get('basic_price')
        self.silver_price = data.get('silver_price')
        self.gold_price = data.get('gold_price')
        self.platinum_price = data.get('platinum_price')
        self.time = data.get('time')
        self.stems = data.get('stems')
        self.share = data.get('share')
        self.beats_wave = data.get('beats_wave')
        self.artist_tag = data.get('artist_tag')
        self.pres_listened = data.get('pres_listened')
        self.number_play = data.get('number_play')
        self.storage_name = data.get('storage_name')
        self.modified_at = datetime.datetime.utcnow()
        db.session.commit()
        update_doc(self, MediaSchema(), index="albums_and_songs", doc_type="songs")

    def delete(self):
        """ delete one media """

        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_song_by_id(song_id):
        """ get one song by id """

        return Media.query.filter_by(id=song_id).first()

    @staticmethod
    def get_song_by_storage_name(storage_name):
        """ get one song by storage_name """

        return Media.query.filter_by(storage_name=storage_name).first()

    @staticmethod
    def get_song_by_genre(genre_musical, genre_name):
        """ get all song by genre """

        last_3_month = datetime.datetime.now() + relativedelta(months=-3)
        return Media.query.filter_by(genre=genre_name, genre_musical=genre_musical) \
            .filter(Media.created_at > last_3_month) \
            .order_by(desc(Media.number_play)) \
            .limit(10) \
            .all()

    @staticmethod
    def get_all_song_not_album():
        """ get all song single"""

        return Media.query.filter_by(album_song=False).all()

    @staticmethod
    def get_all_song_by_album_id(album_id):
        """ get all song by album_id """

        return Media.query.filter_by(album_id=album_id).all()

    @staticmethod
    def all_songs_in_three_last_month():
        """ get all song at the month """

        last_3_month = datetime.datetime.now() + relativedelta(months=-3)
        return Media.query.filter_by(album_song=False, genre_musical="music") \
            .filter(Media.created_at > last_3_month) \
            .order_by(desc(Media.number_play)) \
            .limit(10) \
            .all()

    @staticmethod
    def ten_last_songs(genre_musical):
        """ top 20 news songs """

        return Media.query.filter_by(album_song=False, genre_musical=genre_musical) \
            .order_by(asc(Media.created_at)) \
            .limit(10) \
            .all()

    @staticmethod
    def randomize_beats():
        """ get randomize 10 beats """

        return Media.query.filter_by(album_song=False, genre_musical="beats") \
            .order_by(func.random()) \
            .limit(10) \
            .all()

    @staticmethod
    def increasing_beats():
        """ get randomize 10 beats """

        return Media.query.filter_by(album_song=False, genre_musical="beats") \
            .order_by(asc(Media.created_at)) \
            .limit(10) \
            .all()

    @staticmethod
    def descending_beats():
        """ get randomize 10 beats """

        return Media.query.filter_by(album_song=False, genre_musical="beats") \
            .order_by(desc(Media.created_at)) \
            .limit(10) \
            .all()

    @staticmethod
    def top_beats_3_last_month():
        """ Return 20 of beats Ranking """

        return Media.query.filter_by(album_song=False, genre_musical="beats") \
            .order_by(desc(Media.number_play), desc(Media.admire), desc(Media.share)) \
            .limit(50) \
            .all()

    @staticmethod
    def african_discovery_beats():
        """ Return 10 of beats discovery """

        discovery_list = []
        for genre in defaultDataConf.discovery_allowed_genres:
            discovery_list.append(Media.query.filter_by(album_song=False, genre_musical="beats")
                                  .filter(Media.genre == genre)
                                  .limit(5)
                                  .all())
        return discovery_list

    @staticmethod
    def ten_last_beats():
        """ Ten latest beats """

        last_3_month = datetime.datetime.now() + relativedelta(months=-3)
        return Media.query.filter_by(album_song=False, genre_musical="beats") \
            .filter(Media.created_at > last_3_month) \
            .order_by(asc(Media.created_at)) \
            .limit(10) \
            .all()

    @staticmethod
    def isl_playlist_beats():
        """ Return 10 of beats isl playlist """

        try:
            _min = db.session.query(db.func.max(Media.number_play)).scalar() / 2
            return Media.query.filter_by(album_song=False, genre_musical="beats") \
                .filter(Media.number_play < round(_min + (_min / 2)), Media.number_play > round(_min - (_min / 2))) \
                .limit(20) \
                .all()
        except TypeError:
            return None


class MediaSchema(ValidateSchema):
    """ Media Schema """

    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    description = fields.Str(nullable=True)
    artist = fields.Str(required=True)
    artist_tag = fields.Str(nullable=True)
    stems = fields.Str(nullable=True)
    beats_wave = fields.Str(nullable=True)
    genre = fields.Str(required=True)
    genre_musical = fields.Str(required=True)
    storage_name = fields.Str(nullable=True)
    photo = fields.Str(nullable=True)
    album_id = fields.Int(nullable=True)
    admire = fields.Int(nullable=True)
    share = fields.Int(nullable=True)
    bpm = fields.Float(nullable=True)
    time = fields.Str(nullable=True)
    basic_price = fields.Float(nullable=True)
    silver_price = fields.Float(nullable=True)
    gold_price = fields.Float(nullable=True)
    platinum_price = fields.Float(nullable=True)
    in_playlist = fields.Int(nullable=True)
    number_play = fields.Int(nullable=True)
    pres_listened = fields.Int(nullable=True)
    album_song = fields.Int(nullable=True)
    user_id = fields.Int(nullable=True)
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)
