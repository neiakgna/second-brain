"""Command-line interface for second-brain."""

from pathlib import Path

import typer

from second_brain.embed import Embedder
from second_brain.ingest import ingest_directory
from second_brain.store import Store

DEFAULT_DB = Path("second_brain.db")

app = typer.Typer(
    name="sb",
    help="Local-first personal knowledge system.",
    no_args_is_help=True,
)


@app.command()
def ingest(
    path: Path = typer.Argument(..., help="Directory of markdown files"),
    db: Path = typer.Option(DEFAULT_DB, help="Database file path"),
) -> None:
    """Ingest markdown files: chunk, embed, and store them."""
    if not path.exists():
        typer.echo(f"Error: path does not exist: {path}", err=True)
        raise typer.Exit(code=1)

    chunks = ingest_directory(path)
    if not chunks:
        typer.echo(f"No markdown files found under: {path}")
        return

    typer.echo(f"Found {len(chunks)} chunk(s). Embedding (first run downloads the model)...")
    embedder = Embedder()
    embedded = embedder.embed_chunks(chunks)

    store = Store(db)
    added = store.add(embedded)
    store.close()

    file_count = len({item.chunk.source for item in embedded})
    typer.echo(f"Stored {added} chunk(s) from {file_count} file(s) in {db}.")


@app.command()
def search(query: str = typer.Argument(..., help="Search query")) -> None:
    """Search the knowledge base."""
    typer.echo(f"Would search for: {query!r} (not implemented yet)")


@app.command()
def stats(db: Path = typer.Option(DEFAULT_DB, help="Database file path")) -> None:
    """Show how many chunks are stored."""
    if not db.exists():
        typer.echo(f"No database at {db}. Run 'sb ingest <folder>' first.")
        return
    store = Store(db)
    typer.echo(f"{store.count()} chunk(s) stored in {db}.")
    store.close()


if __name__ == "__main__":
    app()
