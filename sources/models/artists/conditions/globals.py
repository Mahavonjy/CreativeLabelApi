#!/usr/bin/env python3
""" shebang """

import datetime
from sources.models import db
from sources.models.schemaValidators.validates import ValidateSchema
from marshmallow import fields
from sqlalchemy.dialects.postgresql import JSON


class ConditionGlobals(db.Model):
    """
        Globals condition for all type of artist
    """

    # table name
    __tablename__ = 'condition_globals'

    id = db.Column(db.Integer, primary_key=True)
    travel_expenses = db.Column(JSON, default={})
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    refund_policy = db.Column(db.String(45), default='flexible')
    monday = db.Column(db.Boolean, default=True)
    tuesday = db.Column(db.Boolean, default=True)
    wednesday = db.Column(db.Boolean, default=True)
    thursday = db.Column(db.Boolean, default=True)
    friday = db.Column(db.Boolean, default=True)
    saturday = db.Column(db.Boolean, default=True)
    sunday = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    # class constructor
    def __init__(self, data):
        """ Class constructor """

        self.user_id = data.get('user_id')
        self.monday = data.get('monday')
        self.tuesday = data.get('tuesday')
        self.wednesday = data.get('wednesday')
        self.thursday = data.get('thursday')
        self.friday = data.get('friday')
        self.saturday = data.get('saturday')
        self.sunday = data.get('sunday')
        self.refund_policy = data.get('refund_policy')
        self.travel_expenses = data.get('travel_expenses', {"from": 0, "to": 0})
        self.created_at = datetime.datetime.utcnow()
        self.modified_at = datetime.datetime.utcnow()

    def save(self):
        """ save a playlist """

        db.session.add(self)
        db.session.commit()

    def update(self, data):
        """
            Update a user globals condition
        """

        self.monday = data.get('monday')
        self.tuesday = data.get('tuesday')
        self.wednesday = data.get('wednesday')
        self.thursday = data.get('thursday')
        self.friday = data.get('friday')
        self.saturday = data.get('saturday')
        self.sunday = data.get('sunday')
        self.refund_policy = data.get('refund_policy')
        self.travel_expenses = data.get('travel_expenses')
        self.modified_at = datetime.datetime.utcnow()
        db.session.commit()

    def delete(self):
        """ delete a playlist """

        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_condition_globals_by_user_id(user_id):
        """
            check globals id by id
        """

        return ConditionGlobals.query.filter_by(user_id=user_id).first()


class ConditionGlobalSchema(ValidateSchema):
    """ Condition Globals Schema """

    id = fields.Int(dump_only=True)
    monday = fields.Boolean(required=True)
    tuesday = fields.Boolean(required=True)
    wednesday = fields.Boolean(required=True)
    thursday = fields.Boolean(required=True)
    friday = fields.Boolean(required=True)
    saturday = fields.Boolean(required=True)
    sunday = fields.Boolean(required=True)
    refund_policy = fields.Str(nullable=True)
    travel_expenses = fields.Dict(nullable=True)
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)
