import click
import sys

@click.group()
def cli():
    """Una herramienta CLI simple"""
    pass

@cli.command()
def version():
    """Muestra la versión actual de Python"""
    version = sys.version.split()[0]
    click.echo(f"Python versión: {version}")

if __name__ == '__main__':
    cli()
