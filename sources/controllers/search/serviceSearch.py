#!/usr/bin/env python3
""" shebang """
from operator import itemgetter

from preferences.defaultDataConf import all_genre_of_different_artist
from sources.controllers.stars.starsControllers import check_service_stars
from sources.tools.tools import validate_data
from sources.models.search.basicSearch import ServiceSearchSchema
from sources.models import custom_response, es
from flask import Blueprint, request
from sources.models.users.user import User

api_service_search = Blueprint('service_search', __name__)
search_service_schema = ServiceSearchSchema()


def indexation(options, query_string):
    return es.search(
        index="services",
        body={"from": 0, "size": 10, "query": {"bool": {"must": options, "filter": query_string}}}
    )


def indexation_with_city(options, city, thematics):
    indexed = []
    query_string = {"query_string": {"fields": ["thematics", "others_city"], "query": city + "AND" + thematics}}
    indexed.append(indexation(options, query_string))
    query_string = {"query_string": {"fields": ["thematics"], "query": thematics}}
    indexed.append(indexation(options + [{"match": {"reference_city": city}}], query_string))
    return indexed


def indexation_with_event(options, event, thematics):
    indexed = []
    query_string = {"query_string": {"fields": ["thematics", "events"], "query": event + "AND" + thematics}}
    indexed.append(indexation(options, query_string))
    return indexed


def indexation_with_event_and_city(options, event, city, thematics):
    indexed = []
    query_string = {
        "query_string": {
            "fields": ["thematics", "others_city", "events"], "query": city + "AND" + thematics + "AND" + event
        }
    }
    indexed.append(indexation(options, query_string))
    query_string = {"query_string": {"fields": ["thematics", "events"], "query": thematics + "AND" + event}}
    indexed.append(indexation(options + [{"match": {"reference_city": city}}], query_string))
    return indexed


def filter_indexed_list(indexed_data, all_indexed_data):
    for indexed in indexed_data:
        for _l in indexed['hits']['hits']:
            if _l["_source"] not in all_indexed_data:
                all_indexed_data.append(_l["_source"])
    return all_indexed_data


def add_others_information_to_list_of_service(all_indexed_data):
    new_list_of_all_indexed_data = []
    for service in all_indexed_data:
        material = es.search(
            index="materials",
            body={"query": {"bool": {"must": [{"match": {"id": service["materials_id"]}}]}}})
        option = es.search(
            index="options",
            body={"query": {"bool": {"must": [{"match": {"user_id": service["user_id"]}}], "filter":
                {"query_string": {"fields": ["services_id_list"], "query": service["id"]}}}}})
        service["materials"] = material['hits']['hits'][0]["_source"]
        service["artist_name"] = User.get_one_user(service["user_id"]).name
        service["notes"] = check_service_stars(service["id"])
        service["options"] = [d["_source"] for d in option['hits']['hits']]
        new_list_of_all_indexed_data.append(service)

    return sorted(new_list_of_all_indexed_data, key=itemgetter('price'))


@api_service_search.route('/moment', methods=['POST'])
def search_services_enable_in_this_date():
    """ search matching with text_ in table medias """

    data, error = validate_data(search_service_schema, request)
    if error:
        return custom_response(data, 400)

    all_indexed_data = []
    options = [{"match": {"country": data["country"]}}]
    for thematic in data.get("thematics"):
        list_of_thematics_genre = all_genre_of_different_artist[thematic]
        for thematics_genre in list_of_thematics_genre:
            indexed_data = []
            if data.get("city"):
                indexed_data += indexation_with_city(options, data.get("city"), thematics_genre)
            if data.get("event"):
                indexed_data += indexation_with_event(options, data.get("event"), thematics_genre)
            if data.get("event") and data.get("city"):
                indexed_data += indexation_with_event_and_city(options, data["event"], data["city"], thematics_genre)
            indexed_data += [indexation(options, {"query_string": {"fields": ["thematics"], "query": thematics_genre}})]
            all_indexed_data = filter_indexed_list(indexed_data, all_indexed_data)

    return custom_response(add_others_information_to_list_of_service(all_indexed_data), 200)


@api_service_search.route('/moment/events/<string:event>', methods=['GET'])
def search_all_services_with_specific_event(event):
    indexed_data = es.search(
        index="services",
        body={"from": 0, "size": 50,
              "query": {"bool": {"filter": {"query_string": {"fields": ["events"], "query": event}}}}}
    )

    all_indexed_data = [d["_source"] for d in indexed_data['hits']['hits']]
    return custom_response(add_others_information_to_list_of_service(all_indexed_data), 200)


@api_service_search.route('/moment/thematics/<string:thematic>', methods=['GET'])
def search_all_services_with_specific_thematic(thematic):
    all_indexed_data = []
    list_of_thematics_genre = all_genre_of_different_artist[thematic]
    for thematics_genre in list_of_thematics_genre:
        indexed_data = es.search(
            index="services",
            body={"from": 0, "size": 50,
                  "query": {"bool": {"filter": {"query_string": {"fields": ["thematics"], "query": thematics_genre}}}}}
        )
        all_indexed_data += [indexed_data]

    let_new_all_indexed_data = []
    for service in all_indexed_data:
        let_new_all_indexed_data += [d["_source"] for d in service['hits']['hits']]

    return custom_response(add_others_information_to_list_of_service(let_new_all_indexed_data), 200)
