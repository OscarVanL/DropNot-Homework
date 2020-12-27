import os
import click
from threading import Thread
from client import Client
from server import Server
import time


@click.command()
@click.option('--client', '-c', type=click.Path(exists=True), help="Launch in Client mode")
@click.option('--target', '-t', type=str, help="DropNot server domain")
@click.option('--server', '-s', type=click.Path(exists=True), help="Launch in Server mode")
@click.option('--port', '-p', default=5000, type=int, help="Port for DropNot Server")
def launch(client, target, server, port):
    print("Launching with client:", client, "targeting", target)
    print("Launching with server:", server)

    if client:
        client_dir = os.path.abspath(client)  # Convert relative paths to absolute path
        print("Starting Client, synchronising directory:", client_dir)
        client = Client.DropNotClient(client_dir, target, port)
        client.daemon = True
        client.start()

    if server:
        server_dir = os.path.abspath(server)  # Convert relative paths to absolute path
        print("Starting Server, synchronising files to:", server_dir)
        server = Server.initialise(server_dir)
        server = Thread(target=server.run, kwargs={'host': '0.0.0.0', 'port': port})
        server.daemon = True
        server.start()

    while True:
        time.sleep(1)


if __name__ == '__main__':
    launch()
