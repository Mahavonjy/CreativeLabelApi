#!/usr/bin/env python3
""" shebang """

from sources.models.schemaValidators.validates import ValidateSchema
from marshmallow import fields
from sources.models import db
import datetime


class ContractBeatMaking(db.Model):
    """ Contract BeatMaking Model """

    # table name
    __tablename__ = 'contract_beat_making'

    id = db.Column(db.Integer, primary_key=True)
    contract_name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float(), default=0)
    mp3 = db.Column(db.BOOLEAN, default=False)
    wave = db.Column(db.BOOLEAN, default=False)
    stems = db.Column(db.BOOLEAN, default=False)
    enabled = db.Column(db.BOOLEAN, default=True)
    number_of_distribution_copies = db.Column(db.Integer, default=0)
    number_audio_stream = db.Column(db.Integer, default=0)
    number_music_video = db.Column(db.Integer, default=0)
    number_radio_station = db.Column(db.Integer, default=0)
    unlimited = db.Column(db.BOOLEAN, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    # class constructor
    def __init__(self, data):
        """ Class constructor """

        self.user_id = data.get('user_id')
        self.contract_name = data.get('contract_name')
        self.price = data.get('price')
        self.mp3 = data.get('mp3') or False
        self.wave = data.get('wave') or False
        self.stems = data.get('stems') or False
        self.enabled = data.get('enabled')
        self.number_of_distribution_copies = data.get('number_of_distribution_copies')
        self.number_audio_stream = data.get('number_audio_stream')
        self.number_music_video = data.get('number_music_video')
        self.number_radio_station = data.get('number_radio_station')
        self.unlimited = data.get('unlimited')
        self.modified_at = datetime.datetime.utcnow()
        self.created_at = datetime.datetime.utcnow()

    def save(self):
        """save a new contract """

        db.session.add(self)
        db.session.commit()

    def update(self, data):
        """ update one media """

        self.price = data.get('price')
        self.enabled = data.get('enabled')
        self.number_of_distribution_copies = data.get('number_of_distribution_copies')
        self.number_audio_stream = data.get('number_audio_stream')
        self.number_music_video = data.get('number_music_video')
        self.number_radio_station = data.get('number_radio_station')
        self.unlimited = data.get('unlimited')
        self.modified_at = datetime.datetime.utcnow()
        db.session.commit()

    def delete(self):
        """ delete one media """

        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_contract_name_by_user_id(contract_name=None, user_id=None):
        """ get one contract name by user id """

        if contract_name and not user_id:
            return ContractBeatMaking.query.filter_by(contract_name=contract_name).all()
        if not contract_name and user_id:
            return ContractBeatMaking.query.filter_by(user_id=user_id).all()
        return ContractBeatMaking.query.filter_by(contract_name=contract_name, user_id=user_id).first()


class ContractBeatMakingSchema(ValidateSchema):
    """ ContractBeatMaking Schema """

    id = fields.Int(dump_only=True)
    user_id = fields.Int(allow_none=True)
    price = fields.Float(required=True)
    mp3 = fields.Boolean(required=True)
    wave = fields.Boolean(required=True)
    stems = fields.Boolean(required=True)
    enabled = fields.Boolean(required=True)
    contract_name = fields.Str(required=True)
    unlimited = fields.Boolean(required=True)
    number_audio_stream = fields.Float(required=False)
    number_music_video = fields.Float(required=False)
    number_radio_station = fields.Float(required=False)
    number_of_distribution_copies = fields.Float(required=False)
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)
