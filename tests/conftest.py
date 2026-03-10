# -*- coding: utf-8 -*-
import pytest
import json
import yaml
from pathlib import Path


@pytest.fixture(scope="session")
def accounts_httpRequests1hGroupsFixture():
    with open("tests/data/accounts/httpRequests1hGroups.json") as data:
        res = json.load(data)
    return res


@pytest.fixture(scope="session")
def zones_httpRequests1hGroupsFixture():
    with open("tests/data/zones/httpRequests1hGroups.json") as data:
        res = json.load(data)
    return res


@pytest.fixture(scope="session")
def test_fixture():
    with open("cloudflare_exporter/gql/accounts.httpRequests1hGroups.graphql") as data:
        # query = data.read()
        query = "".join(line.rstrip().lstrip() for line in data)
    return query


# Additional test data fixtures
@pytest.fixture(scope="session")
def zones_empty_histogram():
    """Empty response histogram test data."""
    with open("tests/data/zones/empty_histogram.json") as data:
        return json.load(data)


@pytest.fixture(scope="session")
def zones_aggregated_metrics():
    """Aggregated metrics from multiple time buckets."""
    with open("tests/data/zones/aggregated_metrics.json") as data:
        return json.load(data)


@pytest.fixture(scope="session")
def zones_multiple_keys():
    """Zone object with multiple keys (warning case)."""
    with open("tests/data/zones/multiple_keys_zone.json") as data:
        return json.load(data)


@pytest.fixture(scope="session")
def sample_config():
    """Sample configuration for CLI testing."""
    with open("tests/data/config/valid_config.yaml") as data:
        return yaml.safe_load(data)
