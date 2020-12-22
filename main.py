import os
import click
from threading import Thread
from client import Client
from server import Server
import time


@click.command()
@click.option('--client', '-c', type=click.Path(exists=True), help="Launch in Client mode")
@click.option('--server', '-s', type=click.Path(exists=True), help="Launch in Server mode")
def launch(client, server):
    client_dir = os.path.abspath(client)  # Convert relative paths to absolute path
    server_dir = os.path.abspath(server)

    if client:
        print("Starting Client, synchronising directory:", client_dir)
        client = Client.DropnotClient(client_dir)
        client.daemon = True
        client.start()

    if server:
        print("Starting Server, synchronising files to:", server_dir)
        server = Thread(target=Server.start, args=server_dir)
        server.daemon = True
        server.start()

    while True:
        time.sleep(1)


if __name__ == '__main__':
    launch()