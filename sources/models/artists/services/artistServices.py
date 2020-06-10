#!/usr/bin/env python3
""" shebang """

import datetime
from sources.models import db
from marshmallow import fields
from sqlalchemy.dialects.postgresql import JSON
from sources.models.search.basicSearch import add_new_doc, update_doc
from sources.models.schemaValidators.validates import ValidateSchema


class Services(db.Model):
    """ Services Model """

    # table name
    __tablename__ = 'services'

    id = db.Column(db.BIGINT, primary_key=True)
    special_dates = db.Column(JSON, default={})
    hidden = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text(), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    country = db.Column(db.String(200), nullable=False)
    events = db.Column(db.ARRAY(db.String), default=[])
    galleries = db.Column(db.ARRAY(db.String), default=[])
    thematics = db.Column(db.ARRAY(db.String), default=[])
    others_city = db.Column(db.ARRAY(db.String), default=[])
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    reference_city = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float(), nullable=False, default=1.00)
    travel_expenses = db.Column(db.Float(), nullable=False, default=1.00)
    number_of_artists = db.Column(db.Integer(), nullable=False, default=1)
    unit_duration_of_the_service = db.Column(db.String(10), nullable=False)
    preparation_time = db.Column(db.Float(), nullable=False, default=1.00)
    unit_of_the_preparation_time = db.Column(db.String(10), nullable=False)
    refund_policy = db.Column(db.String(45), nullable=False, default='flexible')
    duration_of_the_service = db.Column(db.Float(), nullable=False, default=1.00)
    materials_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)
    material = db.relationship(
        "Materials",
        cascade="all, delete, save-update",
        backref=db.backref("materials_of_services", uselist=False)
    )

    # class constructor
    def __init__(self, data):
        """ Class constructor """

        self.title = data.get('title')
        self.price = data.get('price')
        self.country = data.get('country')
        self.events = data.get('events')
        self.user_id = data.get('user_id')
        self.hidden = data.get('hidden', False)
        self.galleries = data.get('galleries')
        self.thematics = data.get('thematics')
        self.description = data.get('description')
        self.others_city = data.get('others_city')
        self.special_dates = data.get('special_dates')
        self.materials_id = data.get('materials_id')
        self.reference_city = data.get('reference_city')
        self.travel_expenses = data.get('travel_expenses')
        self.preparation_time = data.get('preparation_time')
        self.number_of_artists = data.get('number_of_artists')
        self.refund_policy = data.get('refund_policy', 'flexible')
        self.duration_of_the_service = data.get('duration_of_the_service')
        self.unit_duration_of_the_service = data.get('unit_duration_of_the_service')
        self.unit_of_the_preparation_time = data.get('unit_of_the_preparation_time')
        self.created_at = datetime.datetime.utcnow()
        self.modified_at = datetime.datetime.utcnow()

    def save(self):
        """ save a Services """

        db.session.add(self)
        db.session.commit()
        add_new_doc(self, ServiceSchema(), index="services", doc_type="prestations")

    def update(self, data):
        """ update a Services """

        self.title = data.get('title')
        self.hidden = data.get('hidden')
        self.country = data.get('country')
        self.description = data.get('description')
        self.events = data.get('events')
        self.galleries = data.get('galleries')
        self.thematics = data.get('thematics')
        self.others_city = data.get('others_city')
        self.user_id = data.get('user_id')
        self.reference_city = data.get('reference_city')
        self.special_dates = data.get('special_dates')
        self.price = data.get('price')
        self.refund_policy = data.get('refund_policy')
        self.materials_id = data.get('materials_id')
        self.travel_expenses = data.get('travel_expenses')
        self.number_of_artists = data.get('number_of_artists')
        self.duration_of_the_service = data.get('duration_of_the_service')
        self.unit_duration_of_the_service = data.get('unit_duration_of_the_service')
        self.preparation_time = data.get('preparation_time')
        self.unit_of_the_preparation_time = data.get('unit_of_the_preparation_time')
        self.modified_at = datetime.datetime.utcnow()
        db.session.commit()
        update_doc(self, ServiceSchema(), index="services", doc_type="prestations")

    def delete(self):
        """ delete a user Services """

        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_by_service_id(service_id=None):
        """ get one artist service """

        return Services.query.filter_by(id=service_id).first()


class ServiceSchema(ValidateSchema):
    """ Profile Schema """

    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    country = fields.Str(required=True)
    user_id = fields.Int(nullable=True)
    price = fields.Float(required=True)
    hidden = fields.Boolean(nullable=True)
    description = fields.Str(nullable=True)
    materials_id = fields.Int(nullable=True)
    reference_city = fields.Str(required=True)
    special_dates = fields.Dict(nullable=True)
    refund_policy = fields.Str(required=True)
    travel_expenses = fields.Float(nullable=True)
    number_of_artists = fields.Int(required=True)
    preparation_time = fields.Float(nullable=True)
    events = fields.List(fields.Str(), required=True)
    galleries = fields.List(fields.Str(), nullable=True)
    thematics = fields.List(fields.Str(), required=True)
    others_city = fields.List(fields.Str(), nullable=True)
    duration_of_the_service = fields.Float(nullable=True)
    unit_duration_of_the_service = fields.Str(required=True)
    unit_of_the_preparation_time = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)  # created date for service
    modified_at = fields.DateTime(dump_only=True)  # date who modified this service
