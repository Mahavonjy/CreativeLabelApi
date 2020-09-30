#!/usr/bin/env python3
""" shebang """

import datetime
from sources.models import db
from sources.models.schemaValidators.validates import ValidateSchema
from marshmallow import fields


class Profiles(db.Model):
    """ Profile Model """

    # table name
    __tablename__ = 'profiles'

    id = db.Column(db.BIGINT, primary_key=True)
    name = db.Column(db.String(125))
    artist_name = db.Column(db.String(125), nullable=True)
    email = db.Column(db.String(125), unique=True, nullable=True)
    social_id = db.Column(db.String(128), unique=True, nullable=True, default=None)
    photo = db.Column(db.String(255), nullable=True)
    cover_photo = db.Column(db.String(255), nullable=True)
    gender = db.Column(db.String(155), nullable=True)
    birth = db.Column(db.Date, nullable=True)
    address = db.Column(db.String(155), nullable=True)
    phone = db.Column(db.String(125), nullable=True)
    country = db.Column(db.String(255), nullable=True)
    region = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(255), nullable=True)
    attached = db.Column(db.Integer, default=0)
    description = db.Column(db.String(255), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    # class constructor
    def __init__(self, data):
        """ Class constructor """

        self.name = data.get('name')
        self.email = data.get('email')
        self.photo = data.get('photo')
        self.cover_photo = data.get('cover_photo')
        self.gender = data.get('gender')
        self.birth = data.get('birth')
        self.address = data.get('address')
        self.phone = data.get('phone')
        self.attached = data.get('attached')
        self.social_id = data.get('social_id')
        self.country = data.get('country')
        self.region = data.get('region')
        self.city = data.get('city')
        self.age = data.get('age')
        self.description = data.get('description')
        self.artist_name = data.get('artist_name') if data.get('artist_name') else None
        self.created_at = datetime.datetime.utcnow()
        self.modified_at = datetime.datetime.utcnow()

    def save(self):
        """ save a profile """

        db.session.add(self)
        db.session.commit()

    def update(self, data):
        """ update a profile """

        self.name = data.get('name')
        self.email = data.get('email')
        self.photo = data.get('photo')
        self.cover_photo = data.get('cover_photo')
        self.gender = data.get('gender')
        self.birth = data.get('birth')
        self.address = data.get('address')
        self.phone = data.get('phone')
        self.country = data.get('country')
        self.social_id = data.get('social_id')
        self.region = data.get('region')
        self.city = data.get('city')
        self.attached = data.get('attached')
        self.artist_name = data.get('artist_name')
        self.description = data.get('description')
        self.age = data.get('age')
        self.modified_at = datetime.datetime.utcnow()
        db.session.commit()

    def delete(self):
        """ delete a user profile """

        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_profile(email=None, social_id=None, profile_id=None):
        """ get a user profile """

        if email:
            return Profiles.query.filter_by(email=email).first()
        if profile_id:
            return Profiles.query.filter_by(id=profile_id).first()
        if social_id:
            return Profiles.query.filter_by(social_id=social_id).first()


class ProfileSchema(ValidateSchema):
    """ Profile Schema """

    id = fields.Int(dump_only=True)
    name = fields.Str(allow_none=False)
    email = fields.Str(allow_none=False)
    photo = fields.Str(allow_none=True)
    cover_photo = fields.Str(allow_none=True)
    gender = fields.Str(allow_none=True)
    birth = fields.Date(allow_none=True)
    address = fields.Str(allow_none=True)
    social_id = fields.Str(allow_none=True)
    phone = fields.Number(allow_none=True)
    country = fields.Str(allow_none=True)
    region = fields.Str(allow_none=True)
    city = fields.Str(allow_none=True)
    attached = fields.Int(allow_none=True)
    description = fields.Str(allow_none=True)
    age = fields.Int(allow_none=True)
    artist_name = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)
