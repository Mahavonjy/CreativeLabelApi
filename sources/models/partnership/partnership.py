#!/usr/bin/env python3
""" shebang """

from sources.models.schemaValidators.validates import ValidateSchema
from marshmallow import fields
from sources.models import db
import datetime


class Partner(db.Model):
    """ table for logout """

    __tablename__ = 'partners'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(155), nullable=False)
    logo = db.Column(db.String(255), nullable=False)
    partnership_desc = db.Column(db.String(255), nullable=False)
    contract_type = db.Column(db.Integer, default=0)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    def __init__(self, data):
        self.name = data.get("name")
        self.logo = data.get("logo")
        self.user_id = data.get("user_id")
        self.contract_type = data.get("contract_type")
        self.partnership_desc = data.get("partnership_desc")
        self.created_at = datetime.datetime.utcnow()
        self.modified_at = datetime.datetime.utcnow()

    def save(self):
        """ save a new partner """

        db.session.add(self)
        db.session.commit()

    def update(self, data):
        """ update a partner """
        self.name = data.get("name")
        self.logo = data.get("logo")
        self.active = data.get("active")
        self.contract_type = data.get("contract_type")
        self.partnership_desc = data.get("partnership_desc")
        self.modified_at = datetime.datetime.utcnow()
        db.session.commit()

    def delete(self):
        """ delete a partner """

        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def partner_by_id(id_):
        """ get a partner by id """

        return Partner.query.filter_by(id=id_).first()

    @staticmethod
    def partner_by_name(name_):
        """ get a partner by name """

        return Partner.query.filter_by(name=name_).first()

    @staticmethod
    def all_partners():
        """ get all partner with us """

        return Partner.query.all()


class PartnerSchema(ValidateSchema):
    """ KeyResetPassword schema"""

    active = fields.Boolean()
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    logo = fields.Str(allow_none=True)
    partnership_desc = fields.Str(required=True)
    contract_type = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)
