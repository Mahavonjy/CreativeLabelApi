#!/usr/bin/env python3
""" shebang """

from marshmallow import Schema, ValidationError, validates, fields
from preferences.defaultDataConf import type_of_isl_artist, allowed_events


class ValidateSchema(Schema):
    event = fields.Str()
    iban = fields.Str()
    swift = fields.Str()
    country = fields.Str()
    services = fields.Dict()
    rules = fields.Boolean()
    user_type = fields.Str()
    note = fields.List(fields.Int())
    events = fields.List(fields.Str())
    travel_expenses = fields.Dict()
    unit_of_the_preparation_time = fields.Str()
    unit_duration_of_the_service = fields.Str()

    @validates('unit_of_the_preparation_time')
    def validate_unit_of_the_preparation_time(self, value):
        if value not in ["day", "hours", "min", "sec"]:
            raise ValidationError("unit_of_the_preparation_time not allowed")

    @validates('unit_duration_of_the_service')
    def validate_unit_duration_of_the_service(self, value):
        if value not in ["day", "hours", "min", "sec"]:
            raise ValidationError("unit_duration_of_the_service not allowed")

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

    @validates('country')
    def validate_country(self, values):

        countries = ["Madagascar", "France", "Belgique", "Luxembourg", "Mauritius", "Mayotte", "Allemagne"]
        if values not in countries:
            raise ValidationError("country not allowed")

    @validates('services')
    def validate_services(self, values):

        if values.get('unit_of_the_preparation_time') not in ["day", "hours", "min", "sec"]:
            raise ValidationError("not allowed")

        if values.get('unit_duration_of_the_service') not in ["day", "hours", "min", "sec"]:
            raise ValidationError("not allowed")

        if values.get('event') and values.get('event') not in allowed_events:
            raise ValidationError("event " + values.get('event') + " not allowed")

        if values.get('user_type') and not values.get('services'):
            raise ValidationError("I need the first service details")
