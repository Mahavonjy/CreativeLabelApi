# sources/app.py
""" shebang """

import os
import sentry_sdk
from flask_cors import CORS
from flask import Flask, request
from sources.models import custom_response
from preferences.config import app_config
from .models import db, bcrypt, mail, migrate
from flask_swagger_ui import get_swaggerui_blueprint
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from sources.controllers.carts.cartsControllers import cart_api
from sources.controllers.users.userControllers import user_api as user_blueprint
from sources.controllers import refresh_all_api as refresh_all_blueprint
from sources.controllers.medias.albumControllers import album_api as album_blueprint
from sources.controllers.medias.mediaControllers import media_api as media_blueprint
from sources.controllers.medias.beatsControllers import beats_api as beats_blueprint
from sources.controllers.stars.starsControllers import user_stars as stars_blueprint
from sources.controllers.profiles.profilesControllers import profile_api as profile_blueprint
from sources.controllers.country.countryControllers import flags_api as flags_api_blueprint
from sources.controllers.banking.bankingControllers import banking_api as banking_blueprint
from sources.controllers.playlists.playlistControllers import playlist_api as playlist_blueprint
from sources.controllers.partnership.partnershipControllers import partner_api as partner_blueprint
from sources.controllers.artists.payments.paymentsControllers import payment_api as payment_blueprint
from sources.controllers.artists.condtitions.conditionsControllers import artist_condition
from sources.controllers.search.mediaSearch import api_medias_search as media_search_blueprint
from sources.controllers.artists.options.optionsControllers import options_api as options_blueprint
from sources.controllers.admirations.admirationsControllers import admiration_api as admiration_blueprint
from sources.controllers.reservations.reservationsControllers import reservation_api as reservation_blueprint
from sources.controllers.prestigeMoneys.prestigeMoneys import prestige_api as prestige_blueprint
from sources.controllers.artists.artistTypes.types import artist_type_api as artist_type_blueprint
from sources.controllers.supportMessages.messages import support_message_api as messages_blueprint
from sources.controllers.search.serviceSearch import api_service_search as service_search_blueprint
from sources.controllers.artists.materials.materialsControllers import materials_api as materials_blueprint
from sources.controllers.medias.artistSuggestion import artist_suggestion as artist_suggestion_blueprint
from sources.controllers.artists.services.servicesControllers import artist_services_api as artist_services_blueprint
from sources.controllers.artists.contractBeatMaking.contractBeatmaking import contract_beat_api as beat_maker_contract


def welcome(env_name):
    """ Create app """

    # app initiliazation
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(app_config[env_name])
    app.secret_key = os.getenv('FN_FLASK_SECRET_KEY')
    sentry_sdk.init(
        dsn="https://8ca78b489b6e4cc6b1a26ffd5852a8e8@sentry.io/1814450",
        integrations=[FlaskIntegration(), SqlalchemyIntegration()]
    )

    # initializing bcrypt, db, mail and migration
    bcrypt.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    # swagger
    SWAGGER_URL = '/doc'
    API_URL = '../static/swagger.yaml'
    SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "Creative Label API"
        }
    )
    app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)

    # ------------------------------------route-----------------------------------#
    # Route Prefix Carts
    app.register_blueprint(cart_api, url_prefix='/api/carts')
    # Route Prefix Users
    app.register_blueprint(user_blueprint, url_prefix='/api/users')
    # Route Prefix Beats
    app.register_blueprint(beats_blueprint, url_prefix='/api/beats')
    # Route Prefix for user stars
    app.register_blueprint(stars_blueprint, url_prefix='/api/stars')
    # Route Prefix Albums
    app.register_blueprint(album_blueprint, url_prefix='/api/albums')
    # Route Prefix Audios
    app.register_blueprint(media_blueprint, url_prefix='/api/medias')
    # Route Prefix Banking details
    app.register_blueprint(banking_blueprint, url_prefix='/api/banking')
    # Route Prefix Options
    app.register_blueprint(options_blueprint, url_prefix='/api/options')
    # Route for all country in creative
    app.register_blueprint(flags_api_blueprint, url_prefix='/api/flags')
    # Route Prefix Partners
    app.register_blueprint(partner_blueprint, url_prefix='/api/partners')
    # Route Prefix Profiles
    app.register_blueprint(profile_blueprint, url_prefix='/api/profiles')
    # Route Prefix Prestige
    app.register_blueprint(prestige_blueprint, url_prefix='/api/prestige')
    # Route Prefix Playlists
    app.register_blueprint(playlist_blueprint, url_prefix='/api/playlists')
    # Route Prefix Materials
    app.register_blueprint(materials_blueprint, url_prefix='/api/materials')
    # Route Prefix Refresh all
    app.register_blueprint(refresh_all_blueprint, url_prefix='/api/refresh')
    # Route Prefix Admiration
    app.register_blueprint(admiration_blueprint, url_prefix='/api/admiration')
    # Payment routes
    app.register_blueprint(payment_blueprint, url_prefix='/api/beats/payment')
    # Route for reservation service
    app.register_blueprint(reservation_blueprint, url_prefix='/api/reservation')
    # Condition for artist
    app.register_blueprint(artist_condition, url_prefix='/api/artist_conditions')
    # Route Prefix Contract Beats
    app.register_blueprint(beat_maker_contract, url_prefix='/api/beats/contract')
    # Artist Type
    app.register_blueprint(artist_type_blueprint, url_prefix='/api/artist_types')
    # Route for support message
    app.register_blueprint(messages_blueprint, url_prefix='/api/support_messages')
    # Route Prefix for search medias
    app.register_blueprint(media_search_blueprint, url_prefix='/api/medias_search')
    # Route for search service
    app.register_blueprint(service_search_blueprint, url_prefix='/api/service_search')
    # Route Prefix artist services
    app.register_blueprint(artist_services_blueprint, url_prefix='/api/artist_services')
    # Route Prefix Artist suggestion
    app.register_blueprint(artist_suggestion_blueprint, url_prefix='/api/artistSuggestion')
    # ------------------------------------route-----------------------------------#

    @app.route('/', methods=['GET'])
    def home():
        """ API home page """

        return custom_response("Welcome to API ISL", 200)

    @app.errorhandler(404)
    def page_not_found(error):
        """ Page does not exist """

        return custom_response(str(error), 777)

    @app.route('/route', methods=['GET'])
    def route():
        """ Return all route and method existing on API """

        links, count = {}, 0
        for rule in app.url_map.iter_rules():
            temp = request.url_root
            new, url_root = list(rule.methods), temp.rsplit('/', 1)
            method = [x for x in new if x not in ('OPTIONS', 'HEAD')]
            links[count], count = {"Method": method[0], "url": url_root[0] + str(rule)}, count + 1
        return custom_response(links, 200)

    return app
