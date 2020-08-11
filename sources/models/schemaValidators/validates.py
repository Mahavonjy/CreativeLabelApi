#!/usr/bin/env python3
""" shebang """

from marshmallow import Schema, ValidationError, validates, fields, validates_schema

from preferences.defaultDataConf import type_of_isl_artist, allowed_events, allowed_cirque_or_child_options, \
    allowed_audio_visual_options, allowed_chant_and_music_options, allowed_beat_maker_options,\
    allowed_magician_options, allowed_comedian_options, allowed_dance_options, allowed_dj_options


class ValidateSchema(Schema):
    event = fields.Str()
    iban = fields.Str()
    swift = fields.Str()
    rules = fields.Boolean()
    note = fields.List(fields.Int())
    user_type = fields.List(fields.Int())
    events = fields.List(fields.Str())
    travel_expenses = fields.Dict()

    @validates('rules')
    def validate_rules(self, value):
        if value is False:
            raise ValidationError("you should accept the rules")

    @validates('iban')
    def validate_iban(self, value):
        if len(value) < 16:
            raise ValidationError("IBAN insufficient digits")

    @validates('swift')
    def validate_swift(self, value):
        if 8 > len(value) > 12:
            raise ValidationError("SWIFT/BIC insufficient digits")

    @validates('note')
    def validate_note(self, value):
        if not 5 >= value[0] >= 0:
            raise ValidationError("note must be greater or equal than 0 or least or equal 5.")

    @validates('user_type')
    def validate_user_type(self, value):
        if value not in [k.get('name') for k in type_of_isl_artist]:
            raise ValidationError("artist type not allowed")

    @validates('events')
    def validate_events(self, values):
        for event in values:
            if event not in allowed_events:
                raise ValidationError("event " + event + " not allowed")

    @validates('travel_expenses')
    def validate_travel_expenses(self, values):
        try:
            type_allowed = [int, float]
            if type(values['from']) not in type_allowed:
                raise ValidationError("type not allowed for the values of key 'from'")
            if type(values['to']) not in type_allowed:
                raise ValidationError("type not allowed for the values of key 'to'")
            if values['to'] != 0 and values['to'] < values['from']:
                raise ValidationError("Value not accepted")
        except KeyError:
            raise ValidationError("need key from and to")

    @validates_schema
    def validate_all(self, data, **kwargs):

        if data.get('user_type') and data.get('services').get('thematics'):
            user_type_ = data.get('user_type')
            thematics = data.get('services').get('thematics')
            for thematic in thematics:
                if user_type_ == "dj" and thematic not in allowed_dj_options or \
                        user_type_ == "dancers" and thematic not in allowed_dance_options or \
                        user_type_ == "comedian" and thematic not in allowed_comedian_options or \
                        user_type_ == "magician" and thematic not in allowed_magician_options or \
                        user_type_ == "beatmaker" and thematic not in allowed_beat_maker_options or \
                        user_type_ == "artist_musician" and thematic not in allowed_chant_and_music_options or \
                        user_type_ == "audiovisual_specialist" and thematic not in allowed_audio_visual_options or \
                        user_type_ == "street_artists" and thematic not in allowed_cirque_or_child_options:
                    raise ValidationError(user_type_ + " type don't match with thematics")

        if data.get('user_type') and not data.get('services'):
            raise ValidationError("I need the first service details")

        if data.get('event') and data.get('event') not in allowed_events:
            raise ValidationError("event " + data.get('event') + " not allowed")
