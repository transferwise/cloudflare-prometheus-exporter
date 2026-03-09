#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for error scenarios using test data files."""

import pytest
import json
from unittest.mock import Mock, patch
from cloudflare_exporter.cloudflare_exporter import (
    parser_httpRequests1hGroups,
    job,
)


class TestErrorScenarios:
    """Test error scenarios using existing test data."""

    def test_not_authorized_error(self):
        """Test handling of not authorized error."""
        with open("tests/data/errors/notAuthorized.json") as f:
            raw_data = json.load(f)

        result = parser_httpRequests1hGroups(
            raw_data, endpoint="zones", zone="test-zone", query_key="httpRequests1hGroups"
        )
        assert result is None

    def test_rate_limiting_error(self):
        """Test handling of rate limiting error."""
        with open("tests/data/errors/rateLimiting.json") as f:
            raw_data = json.load(f)

        result = parser_httpRequests1hGroups(
            raw_data, endpoint="zones", zone="test-zone", query_key="httpRequests1hGroups"
        )
        assert result is None

    def test_time_range_too_large_error(self):
        """Test handling of time range too large error."""
        with open("tests/data/errors/timeRangeTooLarge.json") as f:
            raw_data = json.load(f)

        result = parser_httpRequests1hGroups(
            raw_data, endpoint="zones", zone="test-zone", query_key="httpRequests1hGroups"
        )
        assert result is None

    def test_missing_auth_headers_error(self):
        """Test handling of missing auth headers error."""
        with open("tests/data/errors/missingAuthHeaders.json") as f:
            raw_data = json.load(f)

        result = parser_httpRequests1hGroups(
            raw_data, endpoint="zones", zone="test-zone", query_key="httpRequests1hGroups"
        )
        assert result is None

    def test_auth_error(self):
        """Test handling of authentication error."""
        with open("tests/data/errors/authError.json") as f:
            raw_data = json.load(f)

        result = parser_httpRequests1hGroups(
            raw_data, endpoint="zones", zone="test-zone", query_key="httpRequests1hGroups"
        )
        assert result is None

    def test_zone_not_authorized_error(self):
        """Test handling of zone not authorized error."""
        with open("tests/data/errors/zoneNotAuthorized.json") as f:
            raw_data = json.load(f)

        result = parser_httpRequests1hGroups(
            raw_data, endpoint="zones", zone="test-zone", query_key="httpRequests1hGroups"
        )
        assert result is None

    def test_empty_accounts_data(self):
        """Test handling of empty accounts data."""
        with open("tests/data/accounts/empty.httpRequests1hGroups.json") as f:
            raw_data = json.load(f)

        result = parser_httpRequests1hGroups(
            raw_data,
            endpoint="accounts",
            zone="test-account",
            query_key="httpRequests1hGroups",
        )
        assert result == []

    @patch("cloudflare_exporter.cloudflare_exporter.LOGGER")
    def test_parser_logs_error_on_missing_data(self, mock_logger):
        """Test that parser logs error when data is missing."""
        raw_data = {"errors": ["some error"]}
        result = parser_httpRequests1hGroups(
            raw_data, endpoint="zones", zone="test-zone", query_key="httpRequests1hGroups"
        )
        mock_logger.error.assert_called()
        assert result is None

    @patch("cloudflare_exporter.cloudflare_exporter.EXPORTER")
    @patch("cloudflare_exporter.cloudflare_exporter.gql")
    @patch("cloudflare_exporter.cloudflare_exporter.LOGGER")
    def test_job_logs_errors_from_api(self, mock_logger, mock_gql, mock_exporter):
        """Test that job function logs errors from API response."""
        mock_gql.query.zones.get.return_value = "test query"

        with open("tests/data/errors/notAuthorized.json") as f:
            error_response = json.load(f)

        mock_response = Mock()
        mock_response.json.return_value = error_response
        mock_exporter.get_metrics.return_value = mock_response

        job(
            gql_api="httpRequests1hGroups",
            zone="example.com",
            zone_id="test-zone-id",
            timerange=3600,
        )

        # Verify error was logged
        mock_logger.error.assert_called()

    @patch("cloudflare_exporter.cloudflare_exporter.EXPORTER")
    @patch("cloudflare_exporter.cloudflare_exporter.gql")
    @patch("cloudflare_exporter.cloudflare_exporter.LOGGER")
    def test_job_with_rate_limiting_error(
        self, mock_logger, mock_gql, mock_exporter
    ):
        """Test job function with rate limiting error."""
        mock_gql.query.zones.get.return_value = "test query"

        with open("tests/data/errors/rateLimiting.json") as f:
            error_response = json.load(f)

        mock_response = Mock()
        mock_response.json.return_value = error_response
        mock_exporter.get_metrics.return_value = mock_response

        job(
            gql_api="httpRequests1hGroups",
            zone="example.com",
            zone_id="test-zone-id",
            timerange=3600,
        )

        mock_logger.error.assert_called()

    @patch("cloudflare_exporter.cloudflare_exporter.EXPORTER")
    @patch("cloudflare_exporter.cloudflare_exporter.gql")
    @patch("cloudflare_exporter.cloudflare_exporter.LOGGER")
    def test_job_with_time_range_too_large_error(
        self, mock_logger, mock_gql, mock_exporter
    ):
        """Test job function with time range too large error."""
        mock_gql.query.zones.get.return_value = "test query"

        with open("tests/data/errors/timeRangeTooLarge.json") as f:
            error_response = json.load(f)

        mock_response = Mock()
        mock_response.json.return_value = error_response
        mock_exporter.get_metrics.return_value = mock_response

        job(
            gql_api="httpRequests1hGroups",
            zone="example.com",
            zone_id="test-zone-id",
            timerange=3600,
        )

        mock_logger.error.assert_called()


class TestAccountsData:
    """Test with accounts endpoint data."""

    def test_parser_with_valid_accounts_data(self):
        """Test parser with valid accounts data."""
        with open("tests/data/accounts/httpRequests1hGroups.json") as f:
            raw_data = json.load(f)

        result = parser_httpRequests1hGroups(
            raw_data,
            endpoint="accounts",
            zone="test-account",
            query_key="httpRequests1hGroups",
        )
        # Result should be valid or empty list
        assert result is not None or result == []

    def test_parser_accounts_empty_histogram(self):
        """Test parser with empty accounts histogram."""
        with open("tests/data/accounts/empty.httpRequests1hGroups.json") as f:
            raw_data = json.load(f)

        result = parser_httpRequests1hGroups(
            raw_data,
            endpoint="accounts",
            zone="test-account",
            query_key="httpRequests1hGroups",
            timerange=86400,
        )
        assert result == []
