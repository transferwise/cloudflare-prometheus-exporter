# -*- coding: utf-8 -*-

"""Tests for logging module."""

import pytest
import logging
from datetime import datetime
from unittest.mock import patch, MagicMock
from cloudflare_exporter.logging import CustomJsonFormatter


class TestCustomJsonFormatter:
    """Test cases for CustomJsonFormatter class."""

    def test_formatter_inherits_from_json_formatter(self):
        """Test that CustomJsonFormatter inherits from JsonFormatter."""
        from pythonjsonlogger import jsonlogger

        formatter = CustomJsonFormatter()
        assert isinstance(formatter, jsonlogger.JsonFormatter)

    def test_add_fields_adds_timestamp(self):
        """Test that add_fields adds @timestamp field."""
        formatter = CustomJsonFormatter()
        log_record = {}
        record = MagicMock()
        record.levelname = "INFO"
        message_dict = {}

        with patch("cloudflare_exporter.logging.datetime") as mock_datetime:
            mock_now = MagicMock()
            mock_now.strftime.return_value = "2026-03-09T12:00:00.000000Z"
            mock_datetime.utcnow.return_value = mock_now

            formatter.add_fields(log_record, record, message_dict)

            assert "@timestamp" in log_record
            assert log_record["@timestamp"] == "2026-03-09T12:00:00.000000Z"
            mock_datetime.utcnow.assert_called_once()
            mock_now.strftime.assert_called_once_with("%Y-%m-%dT%H:%M:%S.%fZ")

    def test_add_fields_adds_logger_name(self):
        """Test that add_fields adds logger_name field."""
        formatter = CustomJsonFormatter()
        log_record = {}
        record = MagicMock()
        record.levelname = "INFO"
        message_dict = {}

        formatter.add_fields(log_record, record, message_dict)

        assert "logger_name" in log_record
        # The logger should be retrieved using __name__ from the logging module
        assert isinstance(log_record["logger_name"], logging.Logger)

    def test_add_fields_sets_level_from_record_when_not_present(self):
        """Test that level is set from record.levelname when not in log_record."""
        formatter = CustomJsonFormatter()
        log_record = {}
        record = MagicMock()
        record.levelname = "WARNING"
        message_dict = {}

        formatter.add_fields(log_record, record, message_dict)

        assert "level" in log_record
        assert log_record["level"] == "WARNING"

    def test_add_fields_uppercases_level_when_present(self):
        """Test that level is uppercased when already present in log_record."""
        formatter = CustomJsonFormatter()
        log_record = {"level": "debug"}
        record = MagicMock()
        record.levelname = "DEBUG"
        message_dict = {}

        formatter.add_fields(log_record, record, message_dict)

        assert "level" in log_record
        assert log_record["level"] == "DEBUG"

    def test_add_fields_calls_super(self):
        """Test that add_fields calls parent class add_fields."""
        formatter = CustomJsonFormatter()
        log_record = {}
        record = MagicMock()
        record.levelname = "INFO"
        message_dict = {}

        with patch(
            "pythonjsonlogger.jsonlogger.JsonFormatter.add_fields"
        ) as mock_super:
            formatter.add_fields(log_record, record, message_dict)

            mock_super.assert_called_once_with(log_record, record, message_dict)

    def test_timestamp_format_is_iso8601(self):
        """Test that timestamp follows ISO 8601 format."""
        formatter = CustomJsonFormatter()
        log_record = {}
        record = MagicMock()
        record.levelname = "INFO"
        message_dict = {}

        formatter.add_fields(log_record, record, message_dict)

        timestamp = log_record["@timestamp"]
        # Check format: YYYY-MM-DDTHH:MM:SS.ffffffZ
        assert len(timestamp) == 27
        assert timestamp[10] == "T"
        assert timestamp[-1] == "Z"
        assert timestamp.count("-") >= 2
        assert timestamp.count(":") == 2

    def test_add_fields_with_multiple_levels(self):
        """Test add_fields with various log levels."""
        formatter = CustomJsonFormatter()

        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

        for level in levels:
            log_record = {}
            record = MagicMock()
            record.levelname = level
            message_dict = {}

            formatter.add_fields(log_record, record, message_dict)

            assert log_record["level"] == level

    def test_add_fields_preserves_existing_fields(self):
        """Test that add_fields preserves existing fields in log_record."""
        formatter = CustomJsonFormatter()
        log_record = {"existing_field": "existing_value", "another": 123}
        record = MagicMock()
        record.levelname = "INFO"
        message_dict = {}

        formatter.add_fields(log_record, record, message_dict)

        # Existing fields should still be there
        assert log_record["existing_field"] == "existing_value"
        assert log_record["another"] == 123
        # New fields should be added
        assert "@timestamp" in log_record
        assert "logger_name" in log_record
        assert "level" in log_record

    def test_add_fields_with_lowercase_level_in_record(self):
        """Test add_fields when log_record already has lowercase level."""
        formatter = CustomJsonFormatter()
        log_record = {"level": "info"}
        record = MagicMock()
        record.levelname = "INFO"
        message_dict = {}

        formatter.add_fields(log_record, record, message_dict)

        # Level should be uppercased
        assert log_record["level"] == "INFO"

    def test_add_fields_with_mixed_case_level(self):
        """Test add_fields when log_record has mixed case level."""
        formatter = CustomJsonFormatter()
        log_record = {"level": "WaRnInG"}
        record = MagicMock()
        record.levelname = "WARNING"
        message_dict = {}

        formatter.add_fields(log_record, record, message_dict)

        # Level should be uppercased
        assert log_record["level"] == "WARNING"


class TestCustomJsonFormatterIntegration:
    """Integration tests for CustomJsonFormatter."""

    def test_formatter_with_real_logger(self):
        """Test formatter with a real logging setup."""
        import logging
        import json
        from io import StringIO

        # Create a string stream to capture log output
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(CustomJsonFormatter())

        logger = logging.getLogger("test_logger")
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

        # Log a message
        logger.info("Test message", extra={"custom_field": "custom_value"})

        # Get the logged output
        log_output = stream.getvalue()

        # Parse as JSON
        log_dict = json.loads(log_output.strip())

        # Verify expected fields are present
        assert "@timestamp" in log_dict
        assert "logger_name" in log_dict
        assert "level" in log_dict
        assert log_dict["message"] == "Test message"
        assert log_dict["custom_field"] == "custom_value"

        # Clean up
        logger.removeHandler(handler)

    def test_formatter_handles_empty_message_dict(self):
        """Test that formatter handles empty message_dict."""
        formatter = CustomJsonFormatter()
        log_record = {}
        record = MagicMock()
        record.levelname = "INFO"
        message_dict = {}

        # Should not raise any exception
        formatter.add_fields(log_record, record, message_dict)

        assert "@timestamp" in log_record
        assert "logger_name" in log_record
        assert "level" in log_record
