from __future__ import annotations
from typing import Union, List

import json
from elasticsearch import helpers
from elasticsearch.exceptions import NotFoundError

from app.utils.base  import merge, prid, listify, chunks
from app.utils.jstruct import JStruct
from app.utils.logging import log


class BaseQueryBuilder(object):
    def __init__(self, index: BaseElasticIndex, q: dict = None):
        self.index = index
        self.q = q or {}
        self._hard_offset = None
        self._results = None

    def update(self, q: dict) -> BaseQueryBuilder:
        self.q = merge(self.q, q)
        return self

    def pql_filter(self, filters, filter_field_mapping_name: callable = None):
        PQLInterpreter().apply_filters(
            self,
            filters,
            inverse=False,
            filter_field_mapping_name=filter_field_mapping_name
                                      or (lambda filter: self.index.get_field_mapping_name(filter)),
        )
        return self

    def offset(self, offset):
        self._hard_offset = offset
        self.q = merge(self.q, {"from": offset})
        return self

    def no_source(self):
        return self.update({"_source": False})

    def limit(self, limit):
        self.q = merge(self.q, {"size": limit})
        return self

    def terms(self, **kwargs) -> BaseQueryBuilder:
        self.filter({"terms": kwargs})
        return self

    def not_terms(self, **kwargs) -> BaseQueryBuilder:
        self.filter({"not": {"terms": kwargs}})
        return self

    def term(self, **kwargs) -> BaseQueryBuilder:
        self.filter({"term": kwargs})
        return self

    def aggregation(self, aggregations: dict) -> BaseQueryBuilder:
        self.update({"aggregations": aggregations})
        return self

    def wildcard(self, field: str, value: str) -> BaseQueryBuilder:
        self.update({"query": {field: {"value": value}}})
        return self

    def filter(self, q: Union[dict, List], inverse=False) -> BaseQueryBuilder:
        if inverse:
            return self.filter_not(q)

        self.q = merge(
            self.q,
            {
                "query": {
                    "bool": {
                        "must": self.q.get("query", {}).get("bool", {}).get("must", [])
                                + listify(q)
                    }
                }
            },
        )
        return self

    def filter_not(self, q: dict) -> BaseQueryBuilder:
        self.q = merge(self.q, {"query": {"bool": {"must_not": [q]}}})
        return self

    def filter_terms(self, filters: dict) -> BaseQueryBuilder:
        for k, v in filters.items():
            if not v:
                continue
            self.terms(**{k: listify(v)})
        return self

    def pprint(self):
        prid(self.q)

    def sort(self, field, desc=False, asc=True) -> BaseQueryBuilder:
        """
        The sorting of the results
        :return: The sorting
        """
        if isinstance(field, dict) or isinstance(field, list):
            self.q = merge(self.q, {"sort": field})
        else:
            self.q = merge(
                self.q,
                {"sort": {field: {"order": (desc and "desc") or (asc and "asc")}}},
            )

        return self

    def yield_per(self, size=1000, with_total=False, full_docs=False):
        offset = self._hard_offset or 0
        while True:
            self.offset(offset)
            self.limit(size)
            self.execute()

            if full_docs:
                items = self.results.get("hits", {}).get("hits", [])
            else:
                items = [
                    i.get("_id") for i in self.results.get("hits", {}).get("hits", [])
                ]
            if not items:
                break

            for item in items:
                if with_total:
                    yield item, self.results.get("hits").get("total").get("value")
                else:
                    yield item

            offset += size

    def execute(self, routing=None):
        es = get_elastic()

        result = ElasticSearchResult(
            es.search(
                body=self.q,
                index=self.index.index_name,
                routing=routing,
            )
        )
        prid(message="executing es query on index {}".format(self.index.index_name), d=self.q)
        prid(message="es result", d=result.body)

        return result

    @property
    def results(self) -> ElasticSearchResult:
        if self._results:
            return self._results
        self._results = self.execute()
        return self._results


class BaseElasticIndex(object):
    QueryBuilder = BaseQueryBuilder

    _index_exists = None

    def get_es(self):
        return get_elastic()

    @property
    def index_name(self) -> str:
        raise NotImplemented

    @property
    def settings(self) -> dict:
        return {"number_of_shards": 1, "number_of_replicas": 0}

    def query(self):
        return self.QueryBuilder(self)

    def get_field_mapping_name(self, alias: str):
        return alias

    @property
    def mappings(self) -> dict:
        return {}

    def create_index(self):
        es = get_elastic()

        es.indices.create(
            index=self.index_name,
            body={
                "settings": self.settings,
                "mappings": self.mappings,
            },
        )

        log("warning", "created index: {}".format(self.index_name))

    def delete_index(self, confirm=False) -> None:
        es = get_elastic()

        if confirm:
            es.indices.delete(index=self.index_name, ignore=[400, 404])

    def delete_document(self, id: str):
        try:
            get_elastic().delete(index=self.index_name, id=id)
        except NotFoundError as ex:
            log("error", "Failed to delete event {}".format(id))
            return False
        return True

    def index_exists(self) -> bool:
        if self._index_exists:
            return self._index_exists
        es = get_elastic()
        self._index_exists = es.indices.exists(index=self.index_name)
        return self._index_exists

    def create_index_if_not_exists(self):
        if self.index_exists():
            return
        self.create_index()

    def fill_missing_fields_before_index(self, document):
        pass

    def index(self, doc: dict, doc_id=None, routing=None, refresh=None) -> any:
        self.fill_missing_fields_before_index(doc)

        self.index_many([{"id": doc_id, "doc": doc}], routing=routing, refresh=refresh)

    def index_many(self, docs, routing=None, refresh=None, bulk_size=1000, index=None) -> any:
        if not self.index_exists():
            self.create_index()

        """
        docs=[
            {
                "id":123423,
                "doc":{...}
            }
        ]
        """

        for chunk in chunks(docs, bulk_size):
            chunk = [
                {
                    "_index": index or self.index_name,
                    "_id": doc.get("id"),
                    "_routing": str(routing) if routing else None,
                    "_source": doc.get("doc"),
                }
                for doc in chunk
            ]

            log("debug", "indexing {} docs".format(len(chunk)))
            prid(chunk)

            helpers.bulk(self.get_es(), chunk, refresh=refresh)


class ElasticSearchResult(object):
    def __init__(self, body: dict):
        self.body = body

    @property
    def ids(self):
        return [i.get("_id") for i in self.body.get("hits", {}).get("hits", {})]

    @property
    def aggregations(self):
        return JStruct(self.body.get("aggregations", {}))

    @property
    def rows_source(self):
        return [i.get("_source") for i in self.body.get("hits", {}).get("hits", {})]

    def map_docs_to_objects(self, getter: callable, mapper=lambda id: id):
        return getter(list(map(mapper, self.ids)))

    def count(self) -> int:
        return self.body.get("hits", {}).get("total", {}).get("value")

    def get(self, key, default=None):
        return self.body.get(key, default)

    def __repr__(self):
        return json.dumps(self.body, indent=2)


class PQLInterpreter(object):
    def apply_filters(
            self,
            query_builder,
            filters,
            inverse=False,
            filter_field_mapping_name: callable = None,
    ):
        for filter, value in filters.items():
            if value is None:
                continue

            if filter == "not":
                if isinstance(value, dict):
                    self.apply_filters(query_builder, value, inverse=True)
                else:
                    raise PQLInterpreterError(
                        "Value of not filter must be a filter dict"
                    )
            else:
                if filter_field_mapping_name:
                    filter = filter_field_mapping_name(filter)

                if isinstance(value, dict):
                    print(value)
                    for operator, value in value.items():
                        valid_numeric_operators = ["gt", "gte", "lt", "lte", "eq"]
                        if operator in valid_numeric_operators:
                            if operator != "eq":
                                query_builder.filter(
                                    {
                                        "range": {
                                            "%s.number" % filter: {operator: value}
                                        }
                                    },
                                    inverse=inverse,
                                )
                            else:
                                query_builder.filter(
                                    {"term": {filter: value}}, inverse=inverse
                                )
                        else:
                            raise PQLInterpreterError(
                                "The operator needs to be one of %s, given is <%s>"
                                % (valid_numeric_operators, operator)
                            )
                else:
                    """If the value is not a dict then the query is a terms query"""
                    query_builder.filter(
                        {"terms": {filter: listify(value)}}, inverse=inverse
                    )


class PQLInterpreterError(Exception):
    pass
