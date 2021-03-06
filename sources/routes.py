#!/usr/bin/env python3
""" shebang """

from sources.controllers.carts.cartsControllers import cart_api
from sources.controllers.users.userControllers import user_api as user_blueprint
from sources.controllers.medias.beatsControllers import beats_api as beats_blueprint
from sources.controllers.stars.starsControllers import user_stars as stars_blueprint
from sources.controllers.profiles.profilesControllers import profile_api as profile_blueprint
from sources.controllers.country.countryControllers import flags_api as flags_api_blueprint
from sources.controllers.banking.bankingControllers import banking_api as banking_blueprint
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
from sources.controllers.medias.beatSuggestion import beats_suggestion as beats_suggestion_blueprint
from sources.controllers.artists.services.servicesControllers import artist_services_api as artist_services_blueprint
from sources.controllers.artists.contractBeatMaking.contractBeatmaking import contract_beat_api as beat_maker_contract


def routing(app):
    # Route Prefix Carts
    app.register_blueprint(cart_api, url_prefix='/api/carts')
    # Route Prefix Users
    app.register_blueprint(user_blueprint, url_prefix='/api/users')
    # Route Prefix Beats
    app.register_blueprint(beats_blueprint, url_prefix='/api/beats')
    # Route Prefix for user stars
    app.register_blueprint(stars_blueprint, url_prefix='/api/stars')
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
    # Route Prefix Materials
    app.register_blueprint(materials_blueprint, url_prefix='/api/materials')
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
    app.register_blueprint(beats_suggestion_blueprint, url_prefix='/api/beats_suggestions')
