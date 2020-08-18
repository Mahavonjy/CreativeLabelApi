#!/usr/bin/env python3
""" shebang """
from operator import itemgetter

from preferences.defaultDataConf import all_genre_of_different_artist
from sources.controllers.stars.starsControllers import check_service_stars
from sources.models.artists.services.artistServices import ServiceSearchSchema
from sources.tools.tools import remove_in_indexed_list_by_event_date, validate_data
from sources.models import custom_response, es
from flask import Blueprint, request
from sources.models.users.user import User

api_service_search = Blueprint('service_search', __name__)
search_service_schema = ServiceSearchSchema()


def indexation(options, query_string=None):
    args_to_search = dict(must=options)
    if query_string:
        args_to_search['filter'] = query_string

    return es.search(
        index="services",
        body={"from": 0, "size": 50, "query": {"bool": args_to_search}}
    )


def indexation_with_thematics(data, options, all_data):
    for thematic in data.get("thematics"):
        for thematics_genre in all_genre_of_different_artist[thematic]:
            indexed_data = []

            if not data.get('city') and not data.get('event'):
                indexed_data += [
                    indexation(options, {"query_string": {"fields": ["thematics"], "query": thematics_genre}})]
            else:
                if data.get("city"):
                    indexed_data += indexation_with_city(options, data.get("city"), thematics_genre)
                if data.get("event"):
                    indexed_data += indexation_with_event(options, data.get("event"), thematics_genre)

            all_data = indexed_filter(indexed_data, all_data, data['event_date'])

    return all_data


def indexation_with_city(options, city, thematics=None):
    indexed = []

    if not thematics:
        query_string = {"query_string": {"fields": ["others_city"], "query": city}}
        indexed.append(indexation(options, query_string))
        indexed.append(indexation(options + [{"match": {"reference_city": city}}]))
        return indexed

    query_string = {"query_string": {"fields": ["thematics", "others_city"], "query": city + "AND" + thematics}}
    indexed.append(indexation(options, query_string))
    query_string = {"query_string": {"fields": ["thematics"], "query": thematics}}
    indexed.append(indexation(options + [{"match": {"reference_city": city}}], query_string))
    return indexed


def indexation_with_event(options, event, thematics=None):
    indexed = []

    if not thematics:
        query_string = {"query_string": {"fields": ["events"], "query": event}}
        indexed.append(indexation(options, query_string))
        return indexed

    query_string = {"query_string": {"fields": ["thematics", "events"], "query": event + "AND" + thematics}}
    indexed.append(indexation(options, query_string))
    return indexed


def indexed_filter(indexed_data, all_indexed_data, event_dt=None):
    for indexed in indexed_data:
        for _l in indexed['hits']['hits']:
            if _l["_source"] not in all_indexed_data:
                if event_dt:
                    if not remove_in_indexed_list_by_event_date(_l["_source"], event_dt):
                        all_indexed_data.append(_l["_source"])
                    continue
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


@api_service_search.route('/moment/suggest/<string:country>', methods=['GET'])
def suggest_service_by_country(country, listed=False):
    """ search matching with text_ in table medias """

    options = [{"match": {"country": country}}]
    service_indexed = add_others_information_to_list_of_service(indexed_filter([indexation(options)], []))

    if listed:
        return service_indexed
    return custom_response(service_indexed, 200)


@api_service_search.route('/moment', methods=['POST'])
def search_services_enable_in_this_date():
    """ search matching with text_ in table medias """

    country_locate = request.headers.get('Country', None)
    if not country_locate:
        return custom_response('country may not be null in headers', 400)

    data, error = validate_data(search_service_schema, request)
    if error:
        return custom_response(data, 400)

    all_data = []
    if not data.get("country"):
        data["country"] = country_locate
    options = [{"match": {"country": data["country"]}}]

    if not data.get("city", None) and not data.get("thematics", None) and not data.get("event", None):
        all_data = suggest_service_by_country(data["country"], True)

    elif data.get("thematics"):
        indexation_with_thematics(data, options, all_data)
    else:
        if data.get("city"):
            all_data = indexed_filter(indexation_with_city(options, data.get("city"), data['event_date']), all_data)
        if data.get("event"):
            all_data = indexed_filter(indexation_with_event(options, data.get("event"), data['event_date']), all_data)

    return custom_response(add_others_information_to_list_of_service(all_data), 200)


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
    for thematics_genre in all_genre_of_different_artist[thematic]:
        indexed_data = es.search(
            index="services",
            body={"from": 0, "size": 50,
                  "query": {"bool": {"filter": {"query_string": {"fields": ["thematics"], "query": thematics_genre}}}}}
        )
        all_indexed_data += [indexed_data]

    all_indexed_data = indexed_filter(all_indexed_data, [])

    return custom_response(add_others_information_to_list_of_service(all_indexed_data), 200)
