# -*- coding: utf-8 -*-
import pytest
import json
import yaml
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


# Additional test data fixtures
@pytest.fixture
def zones_empty_histogram(scope="session"):
    """Empty response histogram test data."""
    with open("tests/data/zones/empty_histogram.json") as data:
        return json.load(data)


@pytest.fixture
def zones_aggregated_metrics(scope="session"):
    """Aggregated metrics from multiple time buckets."""
    with open("tests/data/zones/aggregated_metrics.json") as data:
        return json.load(data)


@pytest.fixture
def zones_multiple_keys(scope="session"):
    """Zone object with multiple keys (warning case)."""
    with open("tests/data/zones/multiple_keys_zone.json") as data:
        return json.load(data)


@pytest.fixture
def sample_config(scope="session"):
    """Sample configuration for CLI testing."""
    with open("tests/data/config/valid_config.yaml") as data:
        return yaml.safe_load(data)
