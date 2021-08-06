#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `cloudflare_exporter` package."""

from pprint import pprint as pp
from cloudflare_exporter import parser_httpRequests1hGroups
import datetime
import os

# accounts
# query httpRequests1hGroups($accountTag: ACCOUNTTAG!, $datetime_gt: DATETIMEGT!, $datetime_lt: DATETIMELT!)

# zones
# query httpRequests1hGroups($zoneTag: ZONETAG!, $datetime_gt: DATETIMEGT!, $datetime_lt: DATETIMELT!)


def test_run_exporter(zones_httpRequests1hGroupsFixture):
    # pp(zones_httpRequests1hGroupsFixture)
    assert isinstance(zones_httpRequests1hGroupsFixture, dict)
    parser_httpRequests1hGroups(zones_httpRequests1hGroupsFixture)


def test_query():
    from cloudflare_exporter import gql

    r = gql.query.zones["httpRequests1hGroups"]
    print(r)
