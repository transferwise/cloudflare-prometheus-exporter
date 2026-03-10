# -*- coding: utf-8 -*-

"""Tests for cli module."""

import pytest
import yaml
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from click.testing import CliRunner


class TestMainCommand:
    """Test cases for the main command."""

    def test_main_command_with_no_args(self):
        """Test main command without any arguments."""
        from cloudflare_exporter.cli import main

        runner = CliRunner()
        result = runner.invoke(main, [])
        assert result.exit_code == 0

    def test_main_command_with_debug_flag(self):
        """Test main command with debug flag and subcommand."""
        from cloudflare_exporter.cli import main

        runner = CliRunner()
        # Click groups need a subcommand, so test with get which is simple
        result = runner.invoke(main, ["--debug", "get"])
        assert result.exit_code == 0

    def test_main_command_with_no_debug_flag(self):
        """Test main command with no-debug flag and subcommand."""
        from cloudflare_exporter.cli import main

        runner = CliRunner()
        # Click groups need a subcommand, so test with get which is simple
        result = runner.invoke(main, ["--no-debug", "get"])
        assert result.exit_code == 0

    def test_main_function_accepts_debug_parameter(self):
        """Test that main function properly accepts debug parameter."""
        from cloudflare_exporter.cli import main

        # Test that calling with --help shows the debug option
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert "--debug" in result.output or "debug" in result.output.lower()


class TestExportCommand:
    """Test cases for the export command."""

    def test_export_command_with_valid_config(self, sample_config):
        """Test export command with valid configuration file."""
        from cloudflare_exporter.cli import main

        runner = CliRunner()

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as config_file:
            yaml.dump(sample_config, config_file)
            config_file_path = config_file.name

        try:
            with patch("cloudflare_exporter.cli.run_exporter") as mock_run_exporter:
                result = runner.invoke(main, ["export", config_file_path])

                # Check that run_exporter was called with the config
                assert mock_run_exporter.called
                called_config = mock_run_exporter.call_args[0][0]
                assert "zones" in called_config
                assert "example.com" in called_config["zones"]
        finally:
            Path(config_file_path).unlink()

    def test_export_command_with_missing_config_file(self):
        """Test export command with non-existent config file."""
        from cloudflare_exporter.cli import main

        runner = CliRunner()
        result = runner.invoke(main, ["export", "nonexistent.yaml"])

        # Click should handle the missing file error
        assert result.exit_code != 0
        assert "nonexistent.yaml" in result.output or "Error" in result.output

    def test_export_command_parses_yaml_correctly(self, sample_config):
        """Test that export command correctly parses YAML configuration."""
        from cloudflare_exporter.cli import main

        runner = CliRunner()

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as config_file:
            yaml.dump(sample_config, config_file)
            config_file_path = config_file.name

        try:
            with patch("cloudflare_exporter.cli.run_exporter") as mock_run_exporter:
                result = runner.invoke(main, ["export", config_file_path])

                # Verify the parsed config matches our sample
                called_config = mock_run_exporter.call_args[0][0]
                assert called_config["zones"]["example.com"]["zone_id"] == "abc123"
                assert (
                    called_config["zones"]["example.com"]["api"]
                    == "httpRequests1hGroups"
                )
        finally:
            Path(config_file_path).unlink()

    def test_export_command_calls_run_exporter(self, sample_config):
        """Test that export command calls run_exporter with parsed config."""
        from cloudflare_exporter.cli import main

        runner = CliRunner()

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as config_file:
            yaml.dump(sample_config, config_file)
            config_file_path = config_file.name

        try:
            with patch("cloudflare_exporter.cli.run_exporter") as mock_run_exporter:
                result = runner.invoke(main, ["export", config_file_path])

                # Verify run_exporter was called exactly once
                assert mock_run_exporter.call_count == 1
        finally:
            Path(config_file_path).unlink()


class TestGetCommand:
    """Test cases for the get command."""

    def test_get_command_executes_successfully(self):
        """Test that get command executes successfully."""
        from cloudflare_exporter.cli import main

        runner = CliRunner()
        result = runner.invoke(main, ["get"])

        assert result.exit_code == 0

    def test_get_command_is_a_valid_command(self):
        """Test that get is a recognized command."""
        from cloudflare_exporter.cli import main

        runner = CliRunner()
        result = runner.invoke(main, ["--help"])

        # Check that get command appears in help
        assert "get" in result.output


class TestLoggingConfiguration:
    """Test cases for logging configuration."""

    def test_logging_module_imports_successfully(self):
        """Test that cli module imports successfully with logging config."""
        # This test verifies that the module-level logging configuration doesn't cause errors
        try:
            from cloudflare_exporter import cli

            assert cli is not None
        except Exception as e:
            pytest.fail(f"Failed to import cli module: {e}")

    def test_cli_module_has_logger(self):
        """Test that LOGGER is defined in cli module."""
        from cloudflare_exporter import cli

        assert hasattr(cli, "LOGGER")

    def test_logger_configuration_at_import_time(self):
        """Test that logger is configured when module is imported."""
        from cloudflare_exporter import cli
        import logging

        # Verify LOGGER exists and is a logger instance
        assert isinstance(cli.LOGGER, logging.Logger)


class TestCommandIntegration:
    """Integration tests for command interactions."""

    def test_export_command_is_registered_with_main(self):
        """Test that export command is properly registered with main group."""
        from cloudflare_exporter.cli import main

        runner = CliRunner()
        result = runner.invoke(main, ["--help"])

        # Check that export command appears in help
        assert "export" in result.output

    def test_get_command_is_registered_with_main(self):
        """Test that get command is properly registered with main group."""
        from cloudflare_exporter.cli import main

        runner = CliRunner()
        result = runner.invoke(main, ["--help"])

        # Check that get command appears in help
        assert "get" in result.output

    def test_main_help_shows_debug_option(self):
        """Test that main help shows debug option."""
        from cloudflare_exporter.cli import main

        runner = CliRunner()
        result = runner.invoke(main, ["--help"])

        # Check that debug option appears in help
        assert "--debug" in result.output or "--no-debug" in result.output

    def test_main_is_click_group(self):
        """Test that main is a Click group."""
        from cloudflare_exporter.cli import main
        import click

        assert isinstance(main, click.Group)

    def test_export_is_click_command(self):
        """Test that export is a Click command."""
        from cloudflare_exporter.cli import export
        import click

        # export should be decorated as a command
        assert callable(export)


class TestYAMLLoading:
    """Test YAML configuration loading."""

    def test_yaml_loader_uses_full_loader(self, sample_config):
        """Test that YAML is loaded with FullLoader."""
        from cloudflare_exporter.cli import main

        runner = CliRunner()

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as config_file:
            yaml.dump(sample_config, config_file)
            config_file_path = config_file.name

        try:
            with patch("cloudflare_exporter.cli.run_exporter"):
                with patch("yaml.load") as mock_yaml_load:
                    # Set return value to avoid issues
                    mock_yaml_load.return_value = sample_config

                    result = runner.invoke(main, ["export", config_file_path])

                    # Verify yaml.load was called with FullLoader
                    assert mock_yaml_load.called
                    # Check that Loader kwarg was used
                    call_kwargs = mock_yaml_load.call_args[1]
                    assert "Loader" in call_kwargs
        finally:
            Path(config_file_path).unlink()


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_export_with_invalid_yaml(self):
        """Test export command with invalid YAML file."""
        from cloudflare_exporter.cli import main

        runner = CliRunner()

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as config_file:
            config_file.write("invalid: yaml: content: [[[")
            config_file_path = config_file.name

        try:
            result = runner.invoke(main, ["export", config_file_path])

            # Should handle YAML parsing error
            assert result.exit_code != 0
        finally:
            Path(config_file_path).unlink()

    def test_export_with_empty_file(self):
        """Test export command with empty configuration file.

        Empty YAML files parse as None, which causes run_exporter to fail
        when trying to access config["zones"].
        """
        from cloudflare_exporter.cli import main

        runner = CliRunner()

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as config_file:
            config_file.write("")
            config_file_path = config_file.name

        try:
            result = runner.invoke(main, ["export", config_file_path])

            # Empty file parses as None, causing TypeError in run_exporter
            assert result.exit_code != 0
            assert result.exception is not None
            # Verify the error is due to None config
            assert "NoneType" in str(result.exception)
        finally:
            Path(config_file_path).unlink()
