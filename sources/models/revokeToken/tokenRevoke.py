#!/usr/bin/env python3
""" shebang """

from sources.models import db


class RevokedTokenModel(db.Model):
    """
    Here is my table BlackToken
    All Token in this table is revoked
                                        """

    __tablename__ = 'revoked_tokens'

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.Text())
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    def __init__(self, jwt):
        self.jti = jwt

    def save(self):
        """ Save TokenBlackListed """

        db.session.add(self)
        db.session.commit()

    @staticmethod
    def is_jti_blacklisted(jti):
        """ Check if token is BlackListed"""

        return RevokedTokenModel.query.filter_by(jti=jti).first()
