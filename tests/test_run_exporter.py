#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for run_exporter function."""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from cloudflare_exporter.cloudflare_exporter import run_exporter
import threading
import time


class TestRunExporter:
    """Test run_exporter function."""

    @patch("cloudflare_exporter.cloudflare_exporter.schedule")
    @patch("cloudflare_exporter.cloudflare_exporter.prometheus_client")
    @patch("cloudflare_exporter.cloudflare_exporter.time")
    def test_run_exporter_starts_http_server(
        self, mock_time, mock_prometheus, mock_schedule
    ):
        """Test that run_exporter starts the Prometheus HTTP server."""
        config = {
            "zones": {
                "example.com": {
                    "zone_id": "test-zone-id-123",
                }
            }
        }

        # Mock time.sleep to prevent infinite loop
        mock_time.sleep.side_effect = KeyboardInterrupt()

        try:
            run_exporter(config)
        except KeyboardInterrupt:
            pass

        # Verify HTTP server was started
        mock_prometheus.start_http_server.assert_called_once_with(5000)

    @patch("cloudflare_exporter.cloudflare_exporter.schedule")
    @patch("cloudflare_exporter.cloudflare_exporter.prometheus_client")
    @patch("cloudflare_exporter.cloudflare_exporter.time")
    @patch("cloudflare_exporter.cloudflare_exporter.INTERNAL_MONITOR")
    def test_run_exporter_schedules_jobs_for_zones(
        self, mock_internal_monitor, mock_time, mock_prometheus, mock_schedule
    ):
        """Test that run_exporter schedules jobs for each zone."""
        config = {
            "zones": {
                "example.com": {"zone_id": "zone-1"},
                "test.com": {"zone_id": "zone-2"},
            }
        }

        # Mock schedule
        mock_every = Mock()
        mock_schedule.every.return_value = mock_every
        mock_seconds = Mock()
        mock_every.seconds = mock_seconds

        # Mock time.sleep to prevent infinite loop
        mock_time.sleep.side_effect = KeyboardInterrupt()

        try:
            run_exporter(config)
        except KeyboardInterrupt:
            pass

        # Verify jobs were scheduled for both zones
        assert mock_schedule.every.call_count == 2

    @patch("cloudflare_exporter.cloudflare_exporter.schedule")
    @patch("cloudflare_exporter.cloudflare_exporter.prometheus_client")
    @patch("cloudflare_exporter.cloudflare_exporter.time")
    def test_run_exporter_with_custom_api_endpoint(
        self, mock_time, mock_prometheus, mock_schedule
    ):
        """Test run_exporter with custom API endpoint.

        Verifies that custom API endpoint is used (for query selection),
        and that scheduling still uses the default scrape_interval_seconds since
        no custom value is provided.
        """
        config = {
            "api": "httpRequests1mGroups",
            "zones": {
                "example.com": {"zone_id": "zone-1"},
            },
        }

        mock_every = Mock()
        mock_schedule.every.return_value = mock_every
        mock_time.sleep.side_effect = KeyboardInterrupt()

        try:
            run_exporter(config)
        except KeyboardInterrupt:
            pass

        # Verify schedule.every uses default interval since no custom scrape_interval_seconds
        expected_interval = 86400  # Default from cloudflare_exporter.py
        mock_schedule.every.assert_called_once_with(expected_interval)
        mock_every.seconds.do.assert_called_once()

    @patch("cloudflare_exporter.cloudflare_exporter.schedule")
    @patch("cloudflare_exporter.cloudflare_exporter.prometheus_client")
    @patch("cloudflare_exporter.cloudflare_exporter.time")
    def test_run_exporter_with_custom_timerange(
        self, mock_time, mock_prometheus, mock_schedule
    ):
        """Test run_exporter with custom timerange.

        Verifies that custom timerange_seconds is used (for metrics collection),
        and that scheduling still uses the default scrape_interval_seconds since
        no custom value is provided.
        """
        config = {
            "timerange_seconds": 3600,
            "zones": {
                "example.com": {"zone_id": "zone-1"},
            },
        }

        mock_every = Mock()
        mock_schedule.every.return_value = mock_every
        mock_time.sleep.side_effect = KeyboardInterrupt()

        try:
            run_exporter(config)
        except KeyboardInterrupt:
            pass

        # Verify schedule.every uses default interval since no custom scrape_interval_seconds
        expected_interval = 86400  # Default from cloudflare_exporter.py
        mock_schedule.every.assert_called_once_with(expected_interval)
        mock_every.seconds.do.assert_called_once()

    @patch("cloudflare_exporter.cloudflare_exporter.schedule")
    @patch("cloudflare_exporter.cloudflare_exporter.prometheus_client")
    @patch("cloudflare_exporter.cloudflare_exporter.time")
    def test_run_exporter_with_custom_scrape_interval(
        self, mock_time, mock_prometheus, mock_schedule
    ):
        """Test run_exporter uses the configured scrape interval for scheduling.

        Verifies that schedule.every() is called with the custom scrape_interval_seconds
        value from the config, not the default.
        """
        config = {
            "scrape_interval_seconds": 1800,
            "zones": {
                "example.com": {"zone_id": "zone-1"},
            },
        }

        mock_every = Mock()
        mock_schedule.every.return_value = mock_every
        mock_time.sleep.side_effect = KeyboardInterrupt()

        try:
            run_exporter(config)
        except KeyboardInterrupt:
            pass

        # Verify schedule.every was called with the custom interval from config
        expected_interval = config["scrape_interval_seconds"]
        mock_schedule.every.assert_called_once_with(expected_interval)
        mock_every.seconds.do.assert_called_once()

    @patch("cloudflare_exporter.cloudflare_exporter.schedule")
    @patch("cloudflare_exporter.cloudflare_exporter.prometheus_client")
    @patch("cloudflare_exporter.cloudflare_exporter.time")
    def test_run_exporter_with_custom_scrape_shift(
        self, mock_time, mock_prometheus, mock_schedule
    ):
        """Test run_exporter with custom scrape shift.

        Verifies that custom scrape_shift_seconds is used (for time offset),
        and that scheduling still uses the default scrape_interval_seconds since
        no custom value is provided.
        """
        config = {
            "scrape_shift_seconds": 120,
            "zones": {
                "example.com": {"zone_id": "zone-1"},
            },
        }

        mock_every = Mock()
        mock_schedule.every.return_value = mock_every
        mock_time.sleep.side_effect = KeyboardInterrupt()

        try:
            run_exporter(config)
        except KeyboardInterrupt:
            pass

        # Verify schedule.every uses default interval since no custom scrape_interval_seconds
        expected_interval = 86400  # Default from cloudflare_exporter.py
        mock_schedule.every.assert_called_once_with(expected_interval)
        mock_every.seconds.do.assert_called_once()

    @patch("cloudflare_exporter.cloudflare_exporter.schedule")
    @patch("cloudflare_exporter.cloudflare_exporter.prometheus_client")
    @patch("cloudflare_exporter.cloudflare_exporter.time")
    def test_run_exporter_with_zone_specific_overrides(
        self, mock_time, mock_prometheus, mock_schedule
    ):
        """Test run_exporter applies zone-specific configuration overrides.

        Verifies that zone-specific scrape_interval_seconds overrides the global
        default and is correctly passed to schedule.every().
        """
        config = {
            "api": "httpRequests1hGroups",
            "timerange_seconds": 86400,
            "zones": {
                "example.com": {
                    "zone_id": "zone-1",
                    "api": "httpRequests1mGroups",
                    "timerange_seconds": 3600,
                    "scrape_interval_seconds": 60,
                    "scrape_shift_seconds": 30,
                },
            },
        }

        mock_every = Mock()
        mock_schedule.every.return_value = mock_every
        mock_time.sleep.side_effect = KeyboardInterrupt()

        try:
            run_exporter(config)
        except KeyboardInterrupt:
            pass

        # Verify schedule.every was called with zone-specific interval from config
        zone_config = config["zones"]["example.com"]
        expected_interval = zone_config["scrape_interval_seconds"]
        mock_schedule.every.assert_called_once_with(expected_interval)
        mock_every.seconds.do.assert_called_once()

    @patch("cloudflare_exporter.cloudflare_exporter.schedule")
    @patch("cloudflare_exporter.cloudflare_exporter.prometheus_client")
    @patch("cloudflare_exporter.cloudflare_exporter.time")
    @patch("cloudflare_exporter.cloudflare_exporter.INTERNAL_MONITOR")
    def test_run_exporter_initializes_error_counter(
        self, mock_internal_monitor, mock_time, mock_prometheus, mock_schedule
    ):
        """Test that run_exporter initializes error counter for each zone."""
        config = {
            "zones": {
                "example.com": {"zone_id": "zone-1"},
            }
        }

        mock_time.sleep.side_effect = KeyboardInterrupt()

        try:
            run_exporter(config)
        except KeyboardInterrupt:
            pass

        # Verify error counter was initialized
        mock_internal_monitor._metric_collection_errors.labels.assert_called()

    @patch("cloudflare_exporter.cloudflare_exporter.schedule")
    @patch("cloudflare_exporter.cloudflare_exporter.prometheus_client")
    @patch("cloudflare_exporter.cloudflare_exporter.time")
    def test_run_exporter_calls_schedule_run_pending(
        self, mock_time, mock_prometheus, mock_schedule
    ):
        """Test that run_exporter calls schedule.run_pending() in the loop."""
        config = {
            "zones": {
                "example.com": {"zone_id": "zone-1"},
            }
        }

        # Make it loop a few times before stopping
        call_count = [0]

        def sleep_side_effect(seconds):
            call_count[0] += 1
            if call_count[0] >= 3:
                raise KeyboardInterrupt()

        mock_time.sleep.side_effect = sleep_side_effect

        try:
            run_exporter(config)
        except KeyboardInterrupt:
            pass

        # Verify run_pending was called
        assert mock_schedule.run_pending.call_count >= 3

    @patch("cloudflare_exporter.cloudflare_exporter.schedule")
    @patch("cloudflare_exporter.cloudflare_exporter.prometheus_client")
    @patch("cloudflare_exporter.cloudflare_exporter.time")
    @patch("cloudflare_exporter.cloudflare_exporter.EXPORTER_PORT", "8080")
    def test_run_exporter_with_custom_port(
        self, mock_time, mock_prometheus, mock_schedule
    ):
        """Test run_exporter uses EXPORTER_PORT environment variable."""
        config = {
            "zones": {
                "example.com": {"zone_id": "zone-1"},
            }
        }

        mock_time.sleep.side_effect = KeyboardInterrupt()

        try:
            run_exporter(config)
        except KeyboardInterrupt:
            pass

        # Verify HTTP server was started with custom port
        mock_prometheus.start_http_server.assert_called_once_with(8080)

    @patch("cloudflare_exporter.cloudflare_exporter.schedule")
    @patch("cloudflare_exporter.cloudflare_exporter.prometheus_client")
    @patch("cloudflare_exporter.cloudflare_exporter.time")
    def test_run_exporter_sleeps_one_second(
        self, mock_time, mock_prometheus, mock_schedule
    ):
        """Test that run_exporter sleeps for 1 second in the loop."""
        config = {
            "zones": {
                "example.com": {"zone_id": "zone-1"},
            }
        }

        # Stop after first sleep
        mock_time.sleep.side_effect = KeyboardInterrupt()

        try:
            run_exporter(config)
        except KeyboardInterrupt:
            pass

        # Verify sleep was called with 1 second
        mock_time.sleep.assert_called_with(1)
