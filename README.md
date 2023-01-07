# Chat
 
# Server

This is a server that uses sockets to communicate with clients. It has functionality for creating and managing user accounts, creating and managing groups, and handling messages between clients. It is implemented in Python and uses various libraries such as `socket`, `threading`, and `mysql.connector`.

## Features

- User account management: Users can create accounts and log in with their email and password.
- Group management: Users can create and join groups, and send messages to all members of a group.
- MySQL database integration: The server can connect to a MySQL database to store and retrieve data about groups, users, and messages.

## Setup

To run the server, you will need to have Python 3 and the required libraries installed. You will also need to set up a MySQL database and provide the necessary connection details in the code.

## Usage

To start the server, run `python server.py`. The server will listen on `127.0.0.1:5000` for incoming connections. Clients can connect to the server using a socket library in their own program and send requests according to the specified protocol.

## Protocol

The server uses a simple text-based protocol for communication with clients. Each message is a single line of text, with the command and any arguments separated by spaces. Here are the available commands:

- `login email password`: Log in with the specified email and password.
- `register name email password`: Create a new user account with the specified name, email, and password.
- `create-group group_id password`: Create a new group with the specified ID and password.
- `join-group group_id password`: Join the group with the specified ID and password.
- `send-to-group group_id message`: Send the specified message to all members of the group.


# Client

This is a simple client-server program that uses sockets to send and receive messages between a client and a server. The client connects to the server using the IP address `127.0.0.1` and the port number `5000`, and it sends and receives messages using the encoding format `utf-8`.

## Features

- Concurrent message sending and receiving: The program has two threads, one for sending messages and one for receiving messages, which allows the client to send and receive messages concurrently.

## Usage

To run the client, simply run `python client.py`. The client will connect to the server and you will be able to send and receive messages by typing them in the terminal. To stop the client, send the message "exit server!".

## Note

Make sure that the server is running before starting the client. The client will not be able to connect to the server if it is not running.
