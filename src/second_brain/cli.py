"""Command-line interface for second-brain."""

from pathlib import Path

import typer

app = typer.Typer(
    name="sb",
    help="Local-first personal knowledge system.",
    no_args_is_help=True,
)


@app.command()
def ingest(path: Path = typer.Argument(..., help="Directory of markdown files")) -> None:
    """Ingest markdown files from a directory."""
    typer.echo(f"Would ingest from: {path} (not implemented yet)")


@app.command()
def search(query: str = typer.Argument(..., help="Search query")) -> None:
    """Search the knowledge base."""
    typer.echo(f"Would search for: {query!r} (not implemented yet)")


@app.command()
def stats() -> None:
    """Show indexing statistics."""
    typer.echo("Would show stats (not implemented yet)")


if __name__ == "__main__":
    app()
