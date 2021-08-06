# -*- coding: utf-8 -*-
import pytest
import json
from pathlib import Path


@pytest.fixture
def accounts_httpRequests1hGroupsFixture(scope="session"):
    with open("tests/data/accounts/httpRequests1hGroups.json") as data:
        res = json.load(data)
    return res


@pytest.fixture
def zones_httpRequests1hGroupsFixture(scope="session"):
    with open("tests/data/zones/httpRequests1hGroups.json") as data:
        res = json.load(data)
    return res


@pytest.fixture
def test_fixture(scope="session"):
    with open("cloudflare_exporter/gql/accounts.httpRequests1hGroups.graphql") as data:
        # query = data.read()
        query = "".join(line.rstrip().lstrip() for line in data)
    return query
