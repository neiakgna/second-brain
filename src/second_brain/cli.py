"""Command-line interface for second-brain."""

from pathlib import Path

import typer

from second_brain.ingest import ingest_directory

app = typer.Typer(
    name="sb",
    help="Local-first personal knowledge system.",
    no_args_is_help=True,
)


@app.command()
def ingest(path: Path = typer.Argument(..., help="Directory of markdown files")) -> None:
    """Ingest markdown files from a directory."""
    if not path.exists():
        typer.echo(f"Error: path does not exist: {path}", err=True)
        raise typer.Exit(code=1)

    chunks = ingest_directory(path)
    if not chunks:
        typer.echo(f"No markdown files found under: {path}")
        return

    file_count = len({chunk.source for chunk in chunks})
    typer.echo(f"Ingested {file_count} file(s) into {len(chunks)} chunk(s).")


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
