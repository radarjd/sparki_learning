# Sync two or more machines using inet sockets
#
# Created: November 19, 2012 by Jeremy Eglen
# Last Modified: April 30, 2016
#
# included with the sparki_learning library, though that is not required
#
# This module defines functions to synchronize two or more machines using sockets
# One machine is defined by the programmer to be the server. The rest of the machines
# are defined as clients. The programmer would call start_sync_client(SERVER_IP) on each of the client
# machines. All client machines would then return from that function at nearly the same
# time.
#
# For example, to make several computers beep at approximately the same time, write on
# each client:
# start_sync_client(SERVER_IP, SERVER_PORT)
# beep()
#
# The server listens for all of the clients to connect and gives each one the start time. Once the 
# start time passes, the server resumes executing its own program.  Note that you may have to open 
# the firewall on the server for PORT
#
# To have the server join the beeping above, you'd write:
# start_sync_server(wait_time)
# beep()
from __future__ import print_function

from socket import *
from time import *

PORT = 32216
BUFSIZE = 4096
START_NOW = -1


def _sync_client(server_ip, server_port):
    # Connects to the server
    # Upon connection, the server immediately sends its current time (using the time() function) to the client
    # The client sends back the offset between what time the client's real time clock shows and the server's time
    # The server then sends the time to start the event and both server and client close the socket
    # If the start_time sent by the server is less than 0, this function returns START_NOW
    # Else this function returns the number of seconds between right now and the time that the event is to occur

    # receive server's time, return offset, receive start time
    port = int(server_port)

    client = socket(AF_INET, SOCK_STREAM)
    print("attempting to connect to " + str(server_ip))

    client.connect((server_ip, server_port))
    print("connected")

    server_time = float((client.recv(BUFSIZE)).decode())
    client_time = time()
    print("server time is " + str(server_time) + "; client time is " + str(client_time))

    offset = server_time - client_time
    print("sending offset of " + str(offset))

    client.send((str(offset)).encode())
    start_time = float((client.recv(BUFSIZE)).decode())
    print("start time is " + str(start_time))

    client.close()
    print("connection to " + str(server_ip) + " closed")

    if start_time < 0:
        return START_NOW
    else:
        return (start_time - offset) - time()


def _sync_server(start_time=START_NOW, port=PORT):
    # Listens on a socket for the clients to connect
    # Upon connection, the server immediately sends its current time (using the time() function) to the client
    # The client sends back the offset between what time the client's real time clock shows and the server's time
    # The server then sends the time to start the event and both server and client close the socket
    # If the start_time sent by the server is less than 0, this function returns START_NOW
    # Else this function returns the number of seconds between right now and the time that the event is to occur
    # start_time is the unix epoch time that you want all of the clients to sync on
    # returns nothing
    while start_time > time():
        server = socket(AF_INET, SOCK_STREAM)
        host = gethostname()
        host_ip_list = gethostbyname_ex(host)[2]  # the machine may have more than 1 IP address

        if len(host_ip_list) > 1:
            print("Server has multiple ips: " + str(host_ip_list))
            print("You probably want the one beginning 192.168. or 10.")
            host_ip = input("Which ip do you wish to use? ") or host_ip_list[0]
        else:
            host_ip = host_ip_list[0]

        server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)  # to eliminate an error likely to occur on Windows
        server.bind((host, port))

        timeout = start_time - time()
        server.settimeout(timeout)

        server.listen(1)
        print("listening on " + host_ip + ", port " + str(port))
        print("tell the clients to connect to that address and port")

        conn, client_addr = server.accept()
        print("connection from " + str(client_addr))

        # send the server's time, receive the offset, send the start time
        print("sending current time " + str(time()))
        conn.send(str(time()).encode())
        print("offset is " + (conn.recv(BUFSIZE)).decode())

        print("sending starting time " + str(start_time))
        conn.send((str(start_time)).encode())
        conn.close()
        print(str(client_addr) + " closed")


def start_sync_client(server_ip=None, server_port=PORT):
    """ Waits for a time specified by a server to return -- specifically:
        1) connects to a server
        2) gets a time at which this function should return
        3) waits until that time, and then returns

        arguments:
        server_ip - string IPv4 address for the program running the server
                    if none is given to the function, will ask for input
        server_port - int port to which to connect
                      if none is given to the function, defaults to 32216

        returns:
        nothing
    """
    if server_ip is None:
        server_ip = input("What is the server's IP? ")

    wait_time = _sync_client(server_ip, server_port)

    if wait_time > 0:
        print("waiting " + str(wait_time) + " seconds")
        sleep(wait_time)

    print("client go")


def start_sync_server(wait_time=15, port=PORT):
    """ Tells clients when to return (and waits itself) -- specifically:
        1) listens on a local socket for connections from clients
        2) on a client connect, sends the UTC time at which the client function
        should return
        3) after the wait_time, returns

        arguments:
        wait_time - float number of seconds to wait to return; must be less than
                    twenty four hours

        returns:
        nothing
    """
    max_wait_time = 24 * 60 * 60  # 60 seconds * 60 minutes * 24 hours = number of seconds in a day

    if wait_time > max_wait_time:  # can't wait more than 24 hours
        raise RuntimeError("wait time given was more than 24 hours")

    start_time = time()
    print("start time is " + str(start_time) + "; wait time is " + str(wait_time) + " seconds")

    try:
        _sync_server(start_time + wait_time, port)
    except:
        print("timeout, socket error, or (probably) GO TIME")

    print("server go")


def main():
    server = input("Is this the server? (input y if it is) ")

    if server == "y":
        start_sync_server(float(input("How many seconds in the future do you wish to begin? ")))
    else:
        start_sync_client()

    print("done")


if __name__ == "__main__":
    main()
