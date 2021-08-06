# -*- coding: utf-8 -*-

"""Top-level package for Prometheus Cloudflare Exporter."""

__author__ = """Observability :: TransfewrWise"""
__email__ = "observability@transferwise.com"
__version__ = "0.1.12"


class CloudflareGQLQuery:
    def __init__(self):
        self.accounts = {
            "httpRequests1hGroups": read_gql_query(
                "accounts.httpRequests1hGroups.graphql"
            ),
        }
        self.zones = {
            "httpRequests1hGroups": read_gql_query(
                "zones.httpRequests1hGroups.graphql"
            ),
            "httpRequests1mGroups": read_gql_query(
                "zones.httpRequests1mGroups.graphql"
            ),
        }


def read_gql_query(query_file):
    query_path = "cloudflare_exporter/gql/"
    query_file = query_path + query_file
    with open(query_file) as data:
        query = "".join(line.rstrip().lstrip() for line in data)
    return query


query = CloudflareGQLQuery()
