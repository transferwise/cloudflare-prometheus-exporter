#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for CloudflareExporter class."""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock, call
from cloudflare_exporter.cloudflare_exporter import (
    CloudflareExporter,
    job,
    run_threaded,
)
import datetime


class TestCloudflareExporter:
    """Test CloudflareExporter class."""

    @patch("cloudflare_exporter.cloudflare_exporter.requests")
    def test_get_metrics_success(self, mock_requests):
        """Test get_metrics with successful response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_requests.post.return_value = mock_response

        exporter = CloudflareExporter()
        query = "test query"
        variables = {"test": "var"}
        result = exporter.get_metrics(query, variables)

        assert result.status_code == 200
        mock_requests.post.assert_called_once()

    @patch("cloudflare_exporter.cloudflare_exporter.requests")
    @patch("cloudflare_exporter.cloudflare_exporter.LOGGER")
    def test_get_metrics_bad_status_code(self, mock_logger, mock_requests):
        """Test get_metrics with bad status code."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_requests.post.return_value = mock_response

        exporter = CloudflareExporter()
        query = "test query"
        variables = {"test": "var"}
        result = exporter.get_metrics(query, variables)

        assert result.status_code == 401
        mock_logger.warning.assert_called_once()

    @patch("cloudflare_exporter.cloudflare_exporter.requests")
    def test_get_metrics_with_various_status_codes(self, mock_requests):
        """Test get_metrics with various HTTP status codes."""
        status_codes = [200, 400, 401, 403, 404, 500, 502, 503]

        for status_code in status_codes:
            mock_response = Mock()
            mock_response.status_code = status_code
            mock_requests.post.return_value = mock_response

            exporter = CloudflareExporter()
            result = exporter.get_metrics("query", {})
            assert result.status_code == status_code

    @patch("cloudflare_exporter.cloudflare_exporter.MONITOR")
    def test_set_metric_values_basic(self, mock_monitor):
        """Test set_metric_values with basic metrics."""
        exporter = CloudflareExporter()
        metrics = {
            "requests": 100,
            "cachedBytes": 1000,
            "cachedRequests": 50,
            "bytes": 2000,
            "encryptedBytes": 1500,
            "encryptedRequests": 75,
            "pageViews": 20,
            "threats": 5,
            "countryMap": {
                "US": {"requests": 100, "bytes": 2000, "threats": 5}
            },
            "responseStatusMap": {200: 100, 404: 10},
        }
        zone = "example.com"
        timerange = 3600

        exporter.set_metric_values(metrics, zone, timerange)

        # Verify all gauge metrics were set
        mock_monitor._requests.labels.assert_called_with(zone, timerange)
        mock_monitor._cachedBytes.labels.assert_called_with(zone, timerange)
        mock_monitor._bytes.labels.assert_called_with(zone, timerange)

    @patch("cloudflare_exporter.cloudflare_exporter.MONITOR")
    def test_set_metric_values_with_multiple_countries(self, mock_monitor):
        """Test set_metric_values with multiple countries."""
        exporter = CloudflareExporter()
        metrics = {
            "requests": 100,
            "cachedBytes": 1000,
            "cachedRequests": 50,
            "bytes": 2000,
            "encryptedBytes": 1500,
            "encryptedRequests": 75,
            "pageViews": 20,
            "threats": 5,
            "countryMap": {
                "US": {"requests": 50, "bytes": 1000, "threats": 2},
                "UK": {"requests": 30, "bytes": 600, "threats": 1},
                "DE": {"requests": 20, "bytes": 400, "threats": 2},
            },
            "responseStatusMap": {200: 100},
        }
        zone = "example.com"
        timerange = 3600

        exporter.set_metric_values(metrics, zone, timerange)

        # Verify country metrics were set for all countries
        assert mock_monitor._requests_new.labels.call_count == 3
        assert mock_monitor._bytes_new.labels.call_count == 3
        assert mock_monitor._threats_new.labels.call_count == 3

    @patch("cloudflare_exporter.cloudflare_exporter.MONITOR")
    def test_set_metric_values_with_multiple_status_codes(self, mock_monitor):
        """Test set_metric_values with multiple status codes."""
        exporter = CloudflareExporter()
        metrics = {
            "requests": 100,
            "cachedBytes": 1000,
            "cachedRequests": 50,
            "bytes": 2000,
            "encryptedBytes": 1500,
            "encryptedRequests": 75,
            "pageViews": 20,
            "threats": 5,
            "countryMap": {},
            "responseStatusMap": {200: 80, 404: 10, 500: 5, 502: 3, 503: 2},
        }
        zone = "example.com"
        timerange = 3600

        exporter.set_metric_values(metrics, zone, timerange)

        # Verify status code metrics were set for all codes
        assert mock_monitor._responseCodes.labels.call_count == 5

    @patch("cloudflare_exporter.cloudflare_exporter.MONITOR")
    def test_set_metric_values_with_empty_maps(self, mock_monitor):
        """Test set_metric_values with empty country and status maps."""
        exporter = CloudflareExporter()
        metrics = {
            "requests": 100,
            "cachedBytes": 1000,
            "cachedRequests": 50,
            "bytes": 2000,
            "encryptedBytes": 1500,
            "encryptedRequests": 75,
            "pageViews": 20,
            "threats": 5,
            "countryMap": {},
            "responseStatusMap": {},
        }
        zone = "example.com"
        timerange = 3600

        exporter.set_metric_values(metrics, zone, timerange)

        # Verify basic metrics were still set
        mock_monitor._requests.labels.assert_called_with(zone, timerange)


class TestJobFunction:
    """Test job function."""

    @patch("cloudflare_exporter.cloudflare_exporter.EXPORTER")
    @patch("cloudflare_exporter.cloudflare_exporter.gql")
    @patch("cloudflare_exporter.cloudflare_exporter.LOGGER")
    def test_job_successful_execution(self, mock_logger, mock_gql, mock_exporter):
        """Test job function with successful execution."""
        mock_gql.query.zones.get.return_value = "test query"
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "viewer": {
                    "zones": [
                        {
                            "httpRequests1hGroups": [
                                {
                                    "sum": {
                                        "requests": 100,
                                        "bytes": 1000,
                                        "cachedBytes": 500,
                                        "cachedRequests": 50,
                                        "encryptedBytes": 800,
                                        "encryptedRequests": 80,
                                        "pageViews": 20,
                                        "threats": 2,
                                        "clientHTTPVersionMap": [],
                                        "responseStatusMap": [
                                            {"edgeResponseStatus": 200, "requests": 100}
                                        ],
                                        "threatPathingMap": [],
                                        "contentTypeMap": [],
                                        "ipClassMap": [],
                                        "countryMap": [
                                            {
                                                "clientCountryName": "US",
                                                "bytes": 1000,
                                                "requests": 100,
                                                "threats": 2,
                                            }
                                        ],
                                        "browserMap": [],
                                    }
                                }
                            ]
                        }
                    ]
                }
            }
        }
        mock_exporter.get_metrics.return_value = mock_response

        job(
            gql_api="httpRequests1hGroups",
            zone="example.com",
            zone_id="test-zone-id",
            timerange=3600,
            scrape_shift_seconds=60,
        )

        mock_exporter.get_metrics.assert_called_once()
        mock_exporter.set_metric_values.assert_called_once()

    @patch("cloudflare_exporter.cloudflare_exporter.EXPORTER")
    @patch("cloudflare_exporter.cloudflare_exporter.gql")
    @patch("cloudflare_exporter.cloudflare_exporter.LOGGER")
    def test_job_with_api_errors(self, mock_logger, mock_gql, mock_exporter):
        """Test job function with API errors."""
        mock_gql.query.zones.get.return_value = "test query"
        mock_response = Mock()
        mock_response.json.return_value = {
            "errors": [{"message": "not authorized"}],
            "data": None,
        }
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
    def test_job_with_no_metrics(self, mock_logger, mock_gql, mock_exporter):
        """Test job function when no metrics are returned."""
        mock_gql.query.zones.get.return_value = "test query"
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {"viewer": {"zones": [{"httpRequests1hGroups": []}]}}
        }
        mock_exporter.get_metrics.return_value = mock_response

        job(
            gql_api="httpRequests1hGroups",
            zone="example.com",
            zone_id="test-zone-id",
            timerange=3600,
        )

        mock_logger.info.assert_called()

    @patch("cloudflare_exporter.cloudflare_exporter.EXPORTER")
    @patch("cloudflare_exporter.cloudflare_exporter.gql")
    def test_job_with_custom_timerange(self, mock_gql, mock_exporter):
        """Test job function with custom timerange."""
        mock_gql.query.zones.get.return_value = "test query"
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {"viewer": {"zones": [{"httpRequests1hGroups": []}]}}
        }
        mock_exporter.get_metrics.return_value = mock_response

        job(
            gql_api="httpRequests1hGroups",
            zone="example.com",
            zone_id="test-zone-id",
            timerange=7200,  # 2 hours
            scrape_shift_seconds=120,
        )

        # Verify get_metrics was called with correct variables
        call_args = mock_exporter.get_metrics.call_args
        variables = call_args[0][1]
        assert "zoneTag" in variables
        assert "datetime_gt" in variables
        assert "datetime_lt" in variables


class TestRunThreaded:
    """Test run_threaded function."""

    @patch("cloudflare_exporter.cloudflare_exporter.threading.Thread")
    def test_run_threaded_starts_thread(self, mock_thread):
        """Test that run_threaded starts a new thread with correct parameters.

        Verifies that:
        1. Thread receives the job function as target (not its return value)
        2. Thread receives kwargs via kwargs parameter
        3. Job function is not executed on the calling thread
        """
        mock_job = Mock(return_value=None)
        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance

        run_threaded(mock_job, test_kwarg="value")

        # Verify Thread was called with the function reference, not its result
        mock_thread.assert_called_once_with(
            target=mock_job,
            kwargs={"test_kwarg": "value"}
        )
        mock_thread_instance.start.assert_called_once()

        # Verify the job was NOT executed on the calling thread
        # (it should only run when the thread starts)
        mock_job.assert_not_called()

    @patch("cloudflare_exporter.cloudflare_exporter.threading.Thread")
    def test_run_threaded_with_multiple_kwargs(self, mock_thread):
        """Test run_threaded passes multiple kwargs correctly to Thread."""
        mock_job = Mock(return_value=None)
        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance

        run_threaded(
            mock_job, zone="example.com", zone_id="test-id", timerange=3600
        )

        # Verify Thread receives all kwargs
        mock_thread.assert_called_once_with(
            target=mock_job,
            kwargs={"zone": "example.com", "zone_id": "test-id", "timerange": 3600}
        )
        mock_thread_instance.start.assert_called_once()

        # Verify job not executed eagerly
        mock_job.assert_not_called()
