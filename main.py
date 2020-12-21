import os
import click
from client import Client
from server import Server


@click.command()
@click.option('--client', '-c', is_flag=True, help="Launch in Client mode")
@click.option('--server', '-s', is_flag=True, help="Launch in Server mode")
@click.argument('sync_dir', required=True, type=click.Path(exists=True))
def launch(client, server, sync_dir):
    sync_dir = os.path.abspath(sync_dir)  # Convert relative paths to absolute path
    if client:
        print("Starting Client, synchronising directory:", sync_dir)
        Client.DropnotClient(sync_dir)
    if server:
        print("Starting Server, synchronising files to:", sync_dir)
        Server.DropnotServer(sync_dir)


if __name__ == '__main__':
    launch()