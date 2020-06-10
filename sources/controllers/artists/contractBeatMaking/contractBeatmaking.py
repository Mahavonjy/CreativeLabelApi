#!/usr/bin/env python3
""" shebang """

from flask import request
from flask import Blueprint
from sources.models import custom_response
from preferences import defaultDataConf
from auth.authentification import Auth
from sources.tools.tools import validate_data
from sources.models.artists.beatMakers.contractBeatmaking.contractBeatmaking import ContractBeatMaking, \
    ContractBeatMakingSchema

contract_beat_api = Blueprint('contract_beat', __name__)
contract_schema = ContractBeatMakingSchema()


def create_all_default_contract(user_id):
    """ if user is beatMaker, we create all default contract name """

    data_basic_lease = {
        "mp3": True,
        "contract_name": "basic_lease",
        "price": defaultDataConf.beats_pricing['basic'],
        "number_audio_stream": 10000,
        "user_id": user_id
    }
    ContractBeatMaking(data_basic_lease).save()
    data_silver_lease = {
        "mp3": True,
        "wave": True,
        "contract_name": "silver_lease",
        "price": defaultDataConf.beats_pricing['silver'],
        "number_of_distribution_copies": 10000,
        "number_audio_stream": 100000,
        "number_music_video": 3000,
        "number_radio_station": 4000,
        "user_id": user_id
    }
    ContractBeatMaking(data_silver_lease).save()
    data_gold_lease = {
        "mp3": True,
        "wave": True,
        "stems": True,
        "contract_name": "gold_lease",
        "price": defaultDataConf.beats_pricing['gold'],
        "number_of_distribution_copies": 20000,
        "number_audio_stream": 200000,
        "number_music_video": 20000,
        "number_radio_station": 999999,
        "user_id": user_id
    }
    ContractBeatMaking(data_gold_lease).save()
    data_platinum_lease = {
        "mp3": True,
        "wave": True,
        "stems": True,
        "contract_name": "platinum_lease",
        "price": defaultDataConf.beats_pricing['platinum'],
        "number_of_distribution_copies": 999999,
        "number_audio_stream": 999999,
        "number_music_video": 999999,
        "number_radio_station": 999999,
        "user_id": user_id,
        "unlimited": True
    }
    ContractBeatMaking(data_platinum_lease).save()

    return True


@contract_beat_api.route('/update_basic', methods=['PUT'])
@Auth.auth_required
def update_contract_basic(user_connected_model, user_connected_schema):
    """ Update user basic lease """

    data, error = validate_data(contract_schema, request)
    if error:
        return custom_response(data, 400)

    user_basic_lease = user_connected_model.ContractBeat.filter_by(contract_name="basic_lease").first()
    if user_basic_lease:
        user_basic_lease.update(data)
        return custom_response("Basic lease updated", 200)
    return custom_response("contract not found", 400)


@contract_beat_api.route('/update_silver', methods=['PUT'])
@Auth.auth_required
def update_contract_silver(user_connected_model, user_connected_schema):
    """ Update user silver lease """

    data, error = validate_data(contract_schema, request)
    if error:
        return custom_response(data, 400)

    user_silver_lease = user_connected_model.ContractBeat.filter_by(contract_name="silver_lease").first()
    if user_silver_lease:
        user_silver_lease.update(data)
        return custom_response("Silver lease updated", 200)
    return custom_response("contract not found", 400)


@contract_beat_api.route('/update_gold', methods=['PUT'])
@Auth.auth_required
def update_contract_gold(user_connected_model, user_connected_schema):
    """ Update user gold lease """

    data, error = validate_data(contract_schema, request)
    if error:
        return custom_response(data, 400)

    user_gold_lease = user_connected_model.ContractBeat.filter_by(contract_name="gold_lease").first()
    if user_gold_lease:
        user_gold_lease.update(data)
        return custom_response("gold lease updated", 200)
    return custom_response("contract not found", 400)


@contract_beat_api.route('/update_platinum', methods=['PUT'])
@Auth.auth_required
def update_contract_platinum(user_connected_model, user_connected_schema):
    """ Update user platinum lease """

    data, error = validate_data(contract_schema, request)
    if error:
        return custom_response(data, 400)

    user_platinum_lease = user_connected_model.ContractBeat.filter_by(contract_name="platinum_lease").first()
    if user_platinum_lease:
        user_platinum_lease.update(data)
        return custom_response("platinum lease updated", 200)
    return custom_response("contract not found", 400)


@contract_beat_api.route('/user_artist_contract', methods=['GET'])
@Auth.auth_required
def get_user_beat_maker_contract(user_connected_model, user_connected_schema):
    """ get all contract user in DB """

    all_user_contract, data = user_connected_model.ContractBeat.all(), {}
    for contract in all_user_contract:
        contract = contract_schema.dump(contract)
        data[contract['contract_name']] = contract

    return custom_response(data, 200)
