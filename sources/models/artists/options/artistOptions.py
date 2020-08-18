#!/usr/bin/env python3
""" shebang """

import datetime
from sources.models import db
from marshmallow import fields
from sqlalchemy.dialects.postgresql import JSON
from sources.models.search.basicSearch import add_new_doc, update_doc
from sources.models.schemaValidators.validates import ValidateSchema


class Options(db.Model):
    """ Options Model """

    __tablename__ = 'options'

    id = db.Column(db.BIGINT, primary_key=True)
    special_dates = db.Column(JSON, default={})
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text(), nullable=True)
    artist_tagged = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float(), nullable=False, default=1.00)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    services_id_list = db.Column(db.ARRAY(db.Integer), default=[])
    materials_id = db.Column(db.Integer, db.ForeignKey('materials.id'))
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)
    material = db.relationship(
        "Materials",
        cascade="all, delete, save-update",
        backref=db.backref("materials_of_options", uselist=False)
    )

    # class constructor
    def __init__(self, data):
        """ Class constructor """

        self.name = data.get('name')
        self.price = data.get('price')
        self.user_id = data.get('user_id')
        self.description = data.get('description')
        self.materials_id = data.get('materials_id')
        self.artist_tagged = data.get('artist_tagged')
        self.special_dates = data.get('special_dates')
        self.services_id_list = data.get('services_id_list')
        self.created_at = datetime.datetime.utcnow()
        self.modified_at = datetime.datetime.utcnow()

    def save(self):
        """ save a Options """

        db.session.add(self)
        db.session.commit()
        add_new_doc(self, OptionsSchema(), index="options", doc_type="option")

    def update(self, data):
        """ update a Options """

        self.name = data.get('name')
        self.price = data.get('price')
        self.user_id = data.get('user_id')
        self.description = data.get('description')
        self.materials_id = data.get('materials_id')
        self.artist_tagged = data.get('artist_tagged')
        self.special_dates = data.get('special_dates')
        self.services_id_list = data.get('services_id_list')
        self.modified_at = datetime.datetime.utcnow()
        db.session.commit()
        update_doc(self, OptionsSchema(), index="options", doc_type="option")

    def delete(self):
        """ delete a user Options """

        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_by_options_id(options_id=None):
        """ get one artist service """

        return Options.query.filter_by(service_id=options_id).first()


class OptionsSchema(ValidateSchema):
    """ Options Schema """

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    user_id = fields.Int(allow_none=True)
    price = fields.Float(required=True)
    description = fields.Str(required=False)
    materials_id = fields.Int(allow_none=True)
    artist_tagged = fields.Str(allow_none=False)
    special_dates = fields.Dict(required=True)
    services_id_list = fields.List(fields.Int(), allow_none=True)
    created_at = fields.DateTime(dump_only=True)  # created date for service
    modified_at = fields.DateTime(dump_only=True)  # date who modified this service
