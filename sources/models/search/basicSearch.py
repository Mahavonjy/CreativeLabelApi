#!/usr/bin/env python3
""" shebang """

from sources.models import es
from marshmallow import fields
from sources.models.schemaValidators.validates import ValidateSchema


class ServiceSearchSchema(ValidateSchema):
    """ Profile Schema """

    country = fields.Str(required=True)
    city = fields.Str(nullable=True)
    event_date = fields.DateTime(required=True)
    event = fields.Str(nullable=True)
    thematics = fields.List(fields.Str(), required=True)


def add_new_doc(data, schema, index, doc_type):
    """
    Function to add a document by providing index_name,
    document type, document contents as doc and document id.
    @param data: all information contents
    @param schema: function to dump data
    @param index: index for elasticSearch
    @param doc_type: type of data ex: songs, option ot materials
    """
    es.index(index=index, doc_type=doc_type, body=schema.dump(data))


def update_doc(data, schema, index, doc_type):
    """
        Function to edit a document either updating existing fields or adding a new field.
    """

    sch, second_ = schema.dump(data), {}
    first_ = {"id": sch['id']}
    if doc_type == "songs":
        second_ = {"storage_name": sch['storage_name']}
    elif doc_type == "albums":
        second_ = {"keys": sch['keys']}
    elif doc_type == "prestations":
        second_ = {"title": sch['title']}
    elif doc_type == "material":
        second_ = {"technical_sheet": sch['technical_sheet']}
    elif doc_type == "option":
        second_ = {"name": sch['name']}

    r = document_delete(index, doc_type, first_, second_, True)
    if not r['hits']['hits']:
        es.index(index=index, doc_type=doc_type, body=sch)
        return
    es.index(index=index, doc_type=doc_type, id=r['hits']['hits'][0]['_id'], body=sch)


def document_delete(index, doc_type, first_=None, second_=None, ref=False):
    """
        Function to delete a specific document.
    """

    all_option_for_search = [{"match": first_}]
    if second_[list(second_)[0]]:
        all_option_for_search.append({"match": second_})

    resp_fetched = es.search(index=index, body={"query": {"bool": {"must": all_option_for_search}}})
    if ref:
        return resp_fetched
    es.delete(index=index, doc_type=doc_type, id=resp_fetched['hits']['hits'][0]['_id'])
