"""Smoke tests for the CLI."""

from typer.testing import CliRunner

from second_brain.cli import app

runner = CliRunner()


def test_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Local-first" in result.output


def test_search_placeholder() -> None:
    result = runner.invoke(app, ["search", "hello"])
    assert result.exit_code == 0
    assert "hello" in result.output
