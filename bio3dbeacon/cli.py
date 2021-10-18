import typer
from .solr import Solr, get_solr

app = typer.Typer()


@typer.command()
def solr():
    pass


if __name__ == "__main__":
    app()
