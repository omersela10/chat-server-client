import socket
import threading

HOST = '127.0.0.1'  # Standard loopback IP address (localhost)
PORT = 5000  # Port to listen on (non-privileged ports are > 1023)
FORMAT = 'utf-8'  # Define the encoding format of messages from client-server
ADDR = (HOST, PORT)  # Creating a tuple of IP+PORT

def send(server,client_socket):
    while True:
        try:
            message = input()
            server.send(message.encode(FORMAT))
        except:
            print("server connection lost")
            break
        if message == "exit server!":
           break
def receive(server,client_socket):
    while True:
        try:
            message = server.recv(1024).decode(FORMAT)
            if message == "exit server!":
                break
            else:
                print(message)
        except:
            print("server connection lost \n please enter any key to exit")
            break
        if message == "exit server!":
           break
def clients():
    try:

        # Create the client socket
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Creating a socket
        print("Started running...")
        server.connect(ADDR)  # Connecting to the server
        print("connecting to chat server...")


        receive_thread = threading.Thread(target=receive,args=(server,server))
        receive_thread.start()

        send_thread = threading.Thread(target=send,args=(server,server))
        send_thread.start()
    except:
        print("the connection to chat server lost!")
    




#!!!!!!!!!!!!!!!main!!!!!!!!!!!!!!!!!!
def main():
    clients()
if __name__ == '__main__':
    main()
