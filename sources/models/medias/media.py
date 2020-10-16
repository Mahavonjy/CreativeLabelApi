#!/usr/bin/env python3
""" shebang """

from sources.models.prestigeMoneys.prestigeMoneys import Prestige
from sources.models.elastic.fillInElastic import add_new_doc, update_doc
from sources.models.admirations.admirations import Admiration
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
    basic_price = db.Column(db.Float(), nullable=True)
    silver_price = db.Column(db.Float(), nullable=True)
    gold_price = db.Column(db.Float(), nullable=True)
    platinum_price = db.Column(db.Float(), nullable=True)
    genre = db.Column(db.String(155), nullable=False)
    artist = db.Column(db.String(125), nullable=False)
    artist_tag = db.Column(db.String(255), nullable=True)
    stems = db.Column(db.String(255), nullable=True)
    wave = db.Column(db.String(255), nullable=True)
    mp3 = db.Column(db.String(255), nullable=True)
    share = db.Column(db.Integer, default=0)
    time = db.Column(db.String(10))
    listened = db.Column(db.Integer, default=0)
    bpm = db.Column(db.Float, default=0.0)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    # Relationship
    prestige = db.relationship(Prestige, lazy='dynamic', cascade="all, delete, save-update")
    admirations = db.relationship(Admiration, cascade="all, delete, save-update", lazy='dynamic')

    # class constructor
    def __init__(self, data):
        """ Class constructor """

        self.user_id = data.get('user_id')
        self.title = data.get('title')
        self.listened = 0
        self.photo = data.get('photo')
        self.bpm = data.get('bpm', 0)
        self.time = data.get('time')
        self.mp3 = data.get('mp3')
        self.stems = data.get('stems')
        self.share = data.get('share')
        self.wave = data.get('wave')
        self.artist_tag = data.get('artist_tag')
        self.description = data.get('description') if data.get('description') else data.get('Description')
        self.artist = data.get('artist', data.get('Artist'))
        self.basic_price = data.get('basic_price', None)
        self.silver_price = data.get('silver_price', None)
        self.gold_price = data.get('gold_price', None)
        self.platinum_price = data.get('platinum_price', None)
        self.genre = data.get('genre') if data.get('genre') else data.get('Genre')
        self.created_at = datetime.datetime.utcnow()
        self.modified_at = datetime.datetime.utcnow()

    def save(self):
        """save a new media """

        db.session.add(self)
        db.session.commit()
        add_new_doc(self, MediaSchema(), index="beats", doc_type="songs")

    def update(self, data):
        """ update one media """

        self.title = data.get('title')
        self.bpm = data.get('bpm')
        self.description = data.get('description')
        self.artist = data.get('artist')
        self.photo = data.get('photo')
        self.genre = data.get('genre')
        self.basic_price = data.get('basic_price')
        self.silver_price = data.get('silver_price')
        self.gold_price = data.get('gold_price')
        self.platinum_price = data.get('platinum_price')
        self.time = data.get('time')
        self.mp3 = data.get('mp3')
        self.stems = data.get('stems')
        self.share = data.get('share')
        self.wave = data.get('wave')
        self.artist_tag = data.get('artist_tag')
        self.listened = data.get('listened')
        self.modified_at = datetime.datetime.utcnow()
        db.session.commit()
        update_doc(self, MediaSchema(), index="beats", doc_type="songs")

    def delete(self):
        """ delete one media """

        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_song_by_id(song_id):
        """ get one song by id """

        return Media.query.filter_by(id=song_id).first()

    @staticmethod
    def isl_playlist_beats():
        """ Return 10 of beats isl playlist """

        try:
            _min = db.session.query(db.func.max(Media.listened)).scalar() / 2
            return Media.query \
                .filter(Media.listened < round(_min + (_min / 2)), Media.listened > round(_min - (_min / 2))) \
                .limit(20) \
                .all()
        except TypeError:
            return None


class MediaSchema(ValidateSchema):
    """ Media Schema """

    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    artist = fields.Str(required=True)
    artist_tag = fields.Str(allow_none=True)
    stems = fields.Str(allow_none=True)
    wave = fields.Str(allow_none=True)
    mp3 = fields.Str(allow_none=True)
    genre = fields.Str(required=True)
    photo = fields.Str(allow_none=True)
    share = fields.Int(allow_none=True)
    bpm = fields.Float(allow_none=True)
    time = fields.Str(allow_none=True)
    basic_price = fields.Float(allow_none=True)
    silver_price = fields.Float(allow_none=True)
    gold_price = fields.Float(allow_none=True)
    platinum_price = fields.Float(allow_none=True)
    listened = fields.Int(allow_none=True)
    user_id = fields.Int(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)


class MediaOnStreamSchema(ValidateSchema):
    """ Media Stream Schema """

    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    artist = fields.Str(required=True)
    artist_tag = fields.Str(allow_none=True)
    mp3 = fields.Str(allow_none=True)
    genre = fields.Str(required=True)
    photo = fields.Str(allow_none=True)
    share = fields.Int(allow_none=True)
    bpm = fields.Float(allow_none=True)
    time = fields.Str(allow_none=True)
    basic_price = fields.Float(allow_none=True)
    silver_price = fields.Float(allow_none=True)
    gold_price = fields.Float(allow_none=True)
    platinum_price = fields.Float(allow_none=True)
    listened = fields.Int(allow_none=True)
    user_id = fields.Int(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)
