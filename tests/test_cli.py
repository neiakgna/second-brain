"""Smoke tests for the CLI."""

from typer.testing import CliRunner

from second_brain.cli import app

runner = CliRunner()


def test_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Local-first" in result.output


def test_search_without_database() -> None:
    result = runner.invoke(app, ["search", "hello", "--db", "no_such_index.db"])
    assert result.exit_code == 0
    assert "No database" in result.output


def test_stats_without_database() -> None:
    result = runner.invoke(app, ["stats", "--db", "no_such_index.db"])
    assert result.exit_code == 0
    assert "No database" in result.output
