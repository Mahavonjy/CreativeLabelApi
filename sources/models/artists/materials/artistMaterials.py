#!/usr/bin/env python3
""" shebang """

import datetime
from sources.models import db
from marshmallow import fields
from sources.models.search.basicSearch import add_new_doc, update_doc
from sources.models.schemaValidators.validates import ValidateSchema


class Materials(db.Model):
    """ Materials Model """

    __tablename__ = 'materials'

    id = db.Column(db.BIGINT, primary_key=True)
    list_of_materials = db.Column(db.ARRAY(db.String), default=[])
    technical_sheet = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    # class constructor
    def __init__(self, data):
        """ Class constructor """

        self.technical_sheet = data.get('technical_sheet')
        self.list_of_materials = data.get('list_of_materials')
        self.created_at = datetime.datetime.utcnow()
        self.modified_at = datetime.datetime.utcnow()

    def save(self):
        """ save a Materials """

        db.session.add(self)
        db.session.commit()
        add_new_doc(self, MaterialsSchema(), index="materials", doc_type="material")

    def update(self, data):
        """ update a Materials """

        self.technical_sheet = data.get('technical_sheet')
        self.list_of_materials = data.get('list_of_materials')
        self.modified_at = datetime.datetime.utcnow()
        db.session.commit()
        update_doc(self, MaterialsSchema(), index="materials", doc_type="material")

    def delete(self):
        """ delete a user Materials """

        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_by_materials_id(materials_id=None):
        """ get one artist service """

        return Materials.query.filter_by(service_id=materials_id).first()


class MaterialsSchema(ValidateSchema):
    """ Materials Schema """

    id = fields.Int(dump_only=True)
    technical_sheet = fields.Str(nullable=True)
    list_of_materials = fields.List(fields.Str(), required=True)
    created_at = fields.DateTime(dump_only=True)  # created date for service
    modified_at = fields.DateTime(dump_only=True)  # date who modified this service
