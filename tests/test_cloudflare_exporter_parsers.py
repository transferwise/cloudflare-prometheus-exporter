#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for cloudflare_exporter parser functions."""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from cloudflare_exporter.cloudflare_exporter import (
    parse_responseStatusMap,
    parse_countryMap,
    parse_maps,
    parser_httpRequests1hGroups,
)


class TestParseResponseStatusMap:
    """Test parse_responseStatusMap function."""

    def test_parse_empty_response_status_map(self):
        """Test parsing empty response status map."""
        result = parse_responseStatusMap([])
        assert result == {}

    def test_parse_single_status_code(self):
        """Test parsing single status code."""
        data = [{"edgeResponseStatus": 200, "requests": 100}]
        result = parse_responseStatusMap(data)
        assert result == {200: 100}

    def test_parse_multiple_status_codes(self):
        """Test parsing multiple different status codes."""
        data = [
            {"edgeResponseStatus": 200, "requests": 100},
            {"edgeResponseStatus": 404, "requests": 50},
            {"edgeResponseStatus": 500, "requests": 10},
        ]
        result = parse_responseStatusMap(data)
        assert result == {200: 100, 404: 50, 500: 10}

    def test_parse_duplicate_status_codes(self):
        """Test parsing duplicate status codes aggregates correctly."""
        data = [
            {"edgeResponseStatus": 200, "requests": 100},
            {"edgeResponseStatus": 200, "requests": 50},
            {"edgeResponseStatus": 200, "requests": 25},
        ]
        result = parse_responseStatusMap(data)
        assert result == {200: 175}

    def test_parse_mixed_status_codes(self):
        """Test parsing mixed status codes with duplicates."""
        data = [
            {"edgeResponseStatus": 200, "requests": 100},
            {"edgeResponseStatus": 404, "requests": 50},
            {"edgeResponseStatus": 200, "requests": 50},
            {"edgeResponseStatus": 500, "requests": 10},
            {"edgeResponseStatus": 404, "requests": 25},
        ]
        result = parse_responseStatusMap(data)
        assert result == {200: 150, 404: 75, 500: 10}


class TestParseCountryMap:
    """Test parse_countryMap function."""

    def test_parse_empty_country_map(self):
        """Test parsing empty country map."""
        result = parse_countryMap([])
        assert result == {}

    def test_parse_single_country(self):
        """Test parsing single country."""
        data = [
            {
                "clientCountryName": "US",
                "bytes": 1000,
                "requests": 100,
                "threats": 5,
            }
        ]
        result = parse_countryMap(data)
        assert result == {"US": {"bytes": 1000, "requests": 100, "threats": 5}}

    def test_parse_multiple_countries(self):
        """Test parsing multiple different countries."""
        data = [
            {
                "clientCountryName": "US",
                "bytes": 1000,
                "requests": 100,
                "threats": 5,
            },
            {
                "clientCountryName": "UK",
                "bytes": 2000,
                "requests": 200,
                "threats": 10,
            },
            {
                "clientCountryName": "DE",
                "bytes": 1500,
                "requests": 150,
                "threats": 7,
            },
        ]
        result = parse_countryMap(data)
        assert result == {
            "US": {"bytes": 1000, "requests": 100, "threats": 5},
            "UK": {"bytes": 2000, "requests": 200, "threats": 10},
            "DE": {"bytes": 1500, "requests": 150, "threats": 7},
        }

    def test_parse_duplicate_countries(self):
        """Test parsing duplicate countries aggregates correctly."""
        data = [
            {
                "clientCountryName": "US",
                "bytes": 1000,
                "requests": 100,
                "threats": 5,
            },
            {
                "clientCountryName": "US",
                "bytes": 500,
                "requests": 50,
                "threats": 2,
            },
            {
                "clientCountryName": "US",
                "bytes": 250,
                "requests": 25,
                "threats": 1,
            },
        ]
        result = parse_countryMap(data)
        assert result == {"US": {"bytes": 1750, "requests": 175, "threats": 8}}

    def test_parse_mixed_countries(self):
        """Test parsing mixed countries with duplicates."""
        data = [
            {
                "clientCountryName": "US",
                "bytes": 1000,
                "requests": 100,
                "threats": 5,
            },
            {
                "clientCountryName": "UK",
                "bytes": 2000,
                "requests": 200,
                "threats": 10,
            },
            {
                "clientCountryName": "US",
                "bytes": 500,
                "requests": 50,
                "threats": 2,
            },
        ]
        result = parse_countryMap(data)
        assert result == {
            "US": {"bytes": 1500, "requests": 150, "threats": 7},
            "UK": {"bytes": 2000, "requests": 200, "threats": 10},
        }


class TestParseMaps:
    """Test parse_maps function."""

    def test_parse_maps_with_empty_data(self):
        """Test parse_maps with empty maps."""
        profile = {"responseStatusMap": [], "countryMap": []}
        result = parse_maps(profile)
        assert result["responseStatusMap"] == {}
        assert result["countryMap"] == {}

    def test_parse_maps_with_valid_data(self):
        """Test parse_maps with valid data."""
        profile = {
            "responseStatusMap": [
                {"edgeResponseStatus": 200, "requests": 100},
                {"edgeResponseStatus": 404, "requests": 50},
            ],
            "countryMap": [
                {
                    "clientCountryName": "US",
                    "bytes": 1000,
                    "requests": 100,
                    "threats": 5,
                },
                {
                    "clientCountryName": "UK",
                    "bytes": 2000,
                    "requests": 200,
                    "threats": 10,
                },
            ],
        }
        result = parse_maps(profile)
        assert result["responseStatusMap"] == {200: 100, 404: 50}
        assert result["countryMap"] == {
            "US": {"bytes": 1000, "requests": 100, "threats": 5},
            "UK": {"bytes": 2000, "requests": 200, "threats": 10},
        }

    def test_parse_maps_preserves_other_fields(self):
        """Test that parse_maps preserves other fields in profile."""
        profile = {
            "responseStatusMap": [{"edgeResponseStatus": 200, "requests": 100}],
            "countryMap": [
                {
                    "clientCountryName": "US",
                    "bytes": 1000,
                    "requests": 100,
                    "threats": 5,
                }
            ],
            "otherField": "preserved",
            "anotherField": 123,
        }
        result = parse_maps(profile)
        assert "otherField" in result
        assert result["otherField"] == "preserved"
        assert "anotherField" in result
        assert result["anotherField"] == 123


class TestParserHttpRequests1hGroups:
    """Test parser_httpRequests1hGroups function."""

    def test_parser_with_empty_data(self):
        """Test parser with empty response."""
        with open("tests/data/accounts/empty.httpRequests1hGroups.json") as f:
            raw_data = json.load(f)
        result = parser_httpRequests1hGroups(
            raw_data, endpoint="accounts", query_key="httpRequests1hGroups"
        )
        assert result == []

    def test_parser_with_valid_zones_data(self):
        """Test parser with valid zones data."""
        with open("tests/data/zones/httpRequests1hGroups.json") as f:
            raw_data = json.load(f)
        result = parser_httpRequests1hGroups(
            raw_data,
            endpoint="zones",
            zone="test-zone",
            query_key="httpRequests1hGroups",
        )
        assert result is not None
        assert isinstance(result, dict)
        assert "requests" in result
        assert "bytes" in result
        assert "countryMap" in result
        assert "responseStatusMap" in result

    def test_parser_with_missing_data_key(self):
        """Test parser with missing data key."""
        raw_data = {"errors": ["some error"]}
        result = parser_httpRequests1hGroups(
            raw_data,
            endpoint="zones",
            zone="test-zone",
            query_key="httpRequests1hGroups",
        )
        assert result is None

    def test_parser_with_error_response(self):
        """Test parser with error response."""
        with open("tests/data/errors/notAuthorized.json") as f:
            raw_data = json.load(f)
        result = parser_httpRequests1hGroups(
            raw_data,
            endpoint="zones",
            zone="test-zone",
            query_key="httpRequests1hGroups",
        )
        assert result is None

    def test_parser_with_empty_response_histogram(self, zones_empty_histogram):
        """Test parser when response histogram is empty."""
        result = parser_httpRequests1hGroups(
            zones_empty_histogram,
            endpoint="zones",
            zone="test-zone",
            query_key="httpRequests1hGroups",
            timerange=3600,
        )
        assert result == []

    def test_parser_with_accounts_endpoint(self):
        """Test parser with accounts endpoint."""
        with open("tests/data/accounts/httpRequests1hGroups.json") as f:
            raw_data = json.load(f)
        result = parser_httpRequests1hGroups(
            raw_data,
            endpoint="accounts",
            zone="test-account",
            query_key="httpRequests1hGroups",
        )
        assert result is not None or result == []

    def test_parser_aggregates_metrics_correctly(self, zones_aggregated_metrics):
        """Test that parser aggregates metrics from multiple time buckets."""
        result = parser_httpRequests1hGroups(
            zones_aggregated_metrics,
            endpoint="zones",
            zone="test-zone",
            query_key="httpRequests1hGroups",
        )
        assert result["requests"] == 300
        assert result["bytes"] == 3000
        assert result["cachedBytes"] == 1500
        assert result["cachedRequests"] == 150
        assert result["responseStatusMap"] == {200: 300}
        assert result["countryMap"]["US"]["requests"] == 300
        assert result["countryMap"]["US"]["bytes"] == 3000

    def test_parser_with_multiple_keys_in_zone_object(self, zones_multiple_keys):
        """Test parser when zone object has multiple keys (warning case)."""
        # Should log warning when zone object has more than 1 key
        result = parser_httpRequests1hGroups(
            zones_multiple_keys,
            endpoint="zones",
            zone="test-zone",
            query_key="httpRequests1hGroups",
            timerange=3600,
        )

        # Should still process the data correctly
        assert result is not None
        assert result["requests"] == 100
        assert result["bytes"] == 1000
        assert result["countryMap"]["US"]["requests"] == 100
