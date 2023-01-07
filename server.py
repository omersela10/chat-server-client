import time
from socket import socket, AF_INET, SOCK_STREAM
import threading
import re
import mysql.connector
import pymysql




class User():
    def __init__(self, client_name,client_socket, client_address,mail_address=None,password=None):
        self.name = client_name
        self.client_socket = client_socket
        self.client_address = client_address
        self.mail_address=mail_address
        self.password=password


# Define the server
HOST = '127.0.0.1'  # Standard  IP address (localhost)
PORT = 5000  # Port to listen 
FORMAT = 'utf-8'  # Encoding format of messages from client-server
ADDR = (HOST, PORT)  # Creating a tuple of IP+PORT
server_socket = socket(AF_INET, SOCK_STREAM)  # Creating a socket object

group_list = {"0": "123456"}#list of groups and their passwords {stirng:string}
groups_to_users = {"0":{}}#dictionary of group to socket   {string:{User:bool}}
users_list={"admin@gmail.com":"123456"} #dictionary of e-mail to password {string:string}
cout_drade=[0]
#colum in tables DB:
groupchatTable={'id':0,'name':1,'password':2}
usersTable={'id':0,'name':1,'email':2,'password':3}
flagUseDB=[False]
flagUseGroupList=[False] 
flagUseUsersTable=[False]

def connect_DB():
    try:
        while(flagUseDB[0]==True):
            continue
        flagUseDB[0]=True
        cnx = mysql.connector.connect(user='root', password='123456',host='127.0.0.1',database='mydatabase',port=3306)
        cursor = cnx.cursor()
        
        
        operator=cursor.execute("SELECT * FROM groupchat")
        for i in cursor:
            group_list[i[groupchatTable["name"]]]=i[groupchatTable["password"]]
            groups_to_users[i[1]]={}
            
        operator=cursor.execute("SELECT * FROM users")
        for i in cursor:
            users_list[i[usersTable["email"]]]=i[usersTable["password"]]
        print("update data from DB")
        print(group_list)
        print(users_list)
        flagUseDB[0]=False
        return True
    except:
        print("can't connect to DB")
        return False

def add_user_to_db(user1):
    print("add_user_to_db()")
    while (flagUseDB[0]==True):
        continue
    flagUseDB[0]=True
    cnx = mysql.connector.connect(user='root', password='123456',host='127.0.0.1',database='mydatabase',port=3306)
    cursor = cnx.cursor()
    sql='INSERT INTO users (name, email, password) VALUES (%s,%s,%s);'
    val=(str(user1.name),str(user1.mail_address),str(user1.password))
    cursor.execute(sql,val)
    cnx.commit()
    flagUseDB[0]=False

    print("end add_user_to_db()")
def add_group_to_db(group_id,group_password):
    print("add_group_to_db()")
    while (flagUseDB[0]==True):
        continue
    flagUseDB[0]=True
    cnx = mysql.connector.connect(user='root', password='123456',host='127.0.0.1',database='mydatabase',port=3306)
    cursor = cnx.cursor()
    sql = "INSERT INTO groupchat (name, password) VALUES (%s,%s)"
    val = (str(group_id),str(group_password))
    cursor.execute(sql,val)
    cnx.commit()
    flagUseDB[0]=False

def create_group_DB(client_socket, client_address,group_password):
    print("create_group_DB()")
    maxID=0
    while flagUseGroupList[0]==True:
        continue
    flagUseGroupList[0]=True
    for i in group_list.keys():
        if int(i)>maxID:
            maxID=int(i)
    count_group=maxID+1

    group_list[str(count_group)] = group_password
    flagUseGroupList[0]=False
    add_group_to_db(str(count_group),group_password)
    return str(count_group)

def create_group(client_socket, client_address,user1):
    print("create_group()")
    client_socket.send("Enter group password:".encode(FORMAT))
    group_password = client_socket.recv(1024).decode(FORMAT)
    group_id=create_group_DB(client_socket, client_address,group_password)
    print("create_group id:",group_id)
    groups_to_users[group_id]={}
    groups_to_users[group_id][user1]=True
    massage="hey "+user1.name +", group created, group id:"+str(group_id)
    client_socket.send(massage.encode(FORMAT))
    return group_id,user1


def disconnect_server(client_socket, client_address):
    print("disconnect_server()")
    print("<",str(client_address),"> disconnect_server")
    client_socket.send("exit server!".encode(FORMAT))
    client_socket.close()

def connect_group(client_socket, client_address,user1):
    print("connect_group()")
    while True:
        client_socket.send("Enter group id:".encode(FORMAT))
        group_id = client_socket.recv(1024).decode(FORMAT)
        client_socket.send("Enter group password:".encode(FORMAT))
        group_password = client_socket.recv(1024).decode(FORMAT)
        if group_id in group_list.keys() and group_list[group_id] == group_password:
            break
        else:
            client_socket.send("Wrong group id or password please try again...".encode(FORMAT))

    groups_to_users[str(group_id)][user1]=True
    print("connect user "+user1.name +" to group id:",group_id)
    return group_id,user1

def PriveteChat(data,massage,client_socket, client_address,group_id,user1):
    bol=False
    print("PriveteChat()")
    if re.match(r"/[.+]:[.+]", massage)==False:
        return False
    massage=massage[1:]
    massage=massage.split(":")
    userNameRecive=massage[0]
    massagetosend="(Private massage)"+user1.name+":"
    for i in range(1,len(massage)):
        massagetosend+=massage[i]
    massagetosend+="\n"
    for user in groups_to_users[str(group_id)].keys():
        if user.name==userNameRecive:
            user.client_socket.send(massagetosend.encode(FORMAT))
            bol=True
    return bol



def chat(client_socket, client_address,group_id,user1):
    print("chat()")
    message="Welcome to the chat room number "+str(group_id)+" !"+"\n (type 'exit chat!' to exit)"
    client_socket.send(message.encode(FORMAT))

    message="user "+user1.name+" join the chat!"
    for user in groups_to_users[str(group_id)].keys():
        if user.client_socket!=user1.client_socket:
            user.client_socket.send(message.encode(FORMAT))

    while True:
        massage=client_socket.recv(1024).decode(FORMAT)
        data =user1.name +": " + massage
        if data == user1.name +": "+"exit chat!":
            client_socket.send("exit chat!".encode(FORMAT))
            for user in groups_to_users[str(group_id)].keys():
                if user.client_socket!=user1.client_socket:
                    message="user "+user1.name+" disconnect!"
                    user.client_socket.send(message.encode(FORMAT))
            user_disconnect(client_socket, client_address,user1)
            client_socket.send("return to menu...".encode(FORMAT))
            menu(client_socket, client_address,user1)
        elif data == user1.name +": "+"exit server!":
            client_socket.send("exit server!".encode(FORMAT))
            for user in groups_to_users[str(group_id)].keys():
                if user.client_socket!=user1.client_socket:
                    message="user "+user1.name+" disconnect!"
                    user.client_socket.send(message.encode(FORMAT))
            user_disconnect(client_socket, client_address,user1)
            disconnect_server(client_socket, client_address)
            return -1
        elif data == user1.name +": "+"/chat members":
            message="chat member:"
            for user in groups_to_users[str(group_id)].keys():
                message+="\n"+user.name
            client_socket.send(message.encode(FORMAT))
            continue
        elif PriveteChat(data,massage,client_socket, client_address,group_id,user1):
            continue
        for user in groups_to_users[str(group_id)].keys():
            if user.client_socket!=user1.client_socket:
                user.client_socket.send(data.encode(FORMAT))

def user_disconnect(client_socket, client_address,user1):
    print("user_disconnect()")
    for i in groups_to_users.keys():
        if user1 in groups_to_users[i].keys():
            groups_to_users[i].pop(user1)
            break

def menu(client_socket, client_address,user1):
    print("menu()")
    try:
        str1="Welcome to the server menu! \n 1 . create group \n 2. connect group \n 3. disconnect server"
        client_socket.send(str1.encode(FORMAT))
        while True:
            data = client_socket.recv(1024).decode(FORMAT)
            #create new group:
            if data == "1":
                groupID,user1=create_group(client_socket, client_address,user1)
            #connect to exist group:
            elif data == "2":
                groupID,user1=connect_group(client_socket, client_address,user1)
            #disconnect server:
            elif data == "3":
                client_socket.send("type 'exit server!' to exit".encode(FORMAT))
                disconnect_server(client_socket, client_address)
                break
            elif data == "exit server!":
                client_socket.send("exit server!".encode(FORMAT))
                user_disconnect(client_socket, client_address,user1)
                disconnect_server(client_socket, client_address)
                break
            else:
                client_socket.send("Wrong input".encode(FORMAT))
            #Server listens to messages from the client in chat(group ID):
            if data == "1" or data == "2":
                ans=chat(client_socket, client_address,groupID,user1)
                if ans==-1:
                    break
    except Exception as e:
        print("An exception occurred: " ,{e})
        for i in groups_to_users.keys():
            for j in groups_to_users[i].keys():
                if j.client_socket == client_socket:
                    groups_to_users[i].pop(j)
                    break
        client_socket.close()


def log_in(client_socket, client_address):
    print("log_in()")
    while True:
        client_socket.send("Enter your e-mail:".encode(FORMAT))
        client_mail = client_socket.recv(1024).decode(FORMAT)
        client_socket.send("Enter your password:".encode(FORMAT))
        client_password = client_socket.recv(1024).decode(FORMAT)
        if client_mail in users_list.keys() and users_list[client_mail] == client_password:
            client_socket.send("log in successfully.".encode(FORMAT))
            client_socket.send("Enter your name:".encode(FORMAT))
            client_name = client_socket.recv(1024).decode(FORMAT)
            user1=User(client_name,client_socket,client_address,client_mail,client_password)
            return user1
        else:
            client_socket.send("Wrong name or password, please try again...".encode(FORMAT))

def is_valid_email(email):
    print("is_valid_email()")
    if re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
        return True
    return False

def sign_in(client_socket, client_address):
    print("Signing_in()")
    while True:
        client_socket.send("Enter your e-mail:".encode(FORMAT))
        client_mail = client_socket.recv(1024).decode(FORMAT)
        while True:
            if is_valid_email(client_mail):
                break
            client_socket.send("Illegal e-mail, please try again...".encode(FORMAT))
            client_socket.send("Enter your e-mail:".encode(FORMAT))
            client_mail = client_socket.recv(1024).decode(FORMAT)
        
        client_socket.send("Enter your password:".encode(FORMAT))
        client_password = client_socket.recv(1024).decode(FORMAT)
        while True:
            if len(client_password) >= 6:
                break
            client_socket.send("Illegal password, please try again...".encode(FORMAT))
            client_socket.send("Enter your password:".encode(FORMAT))
            client_password = client_socket.recv(1024).decode(FORMAT)

        while flagUseUsersTable[0]==True:
            continue
        flagUseUsersTable[0]=True
        if client_mail not in users_list.keys():
            users_list[client_mail]=client_password
            flagUseUsersTable[0]=False
            client_socket.send("signed up successfully.".encode(FORMAT))
            client_socket.send("Enter your name:".encode(FORMAT))
            client_name = client_socket.recv(1024).decode(FORMAT)
            user1=User(client_name,client_socket,client_address,client_mail,client_password)
            print("test!!!!!!!")
            add_user_to_db(user1)
            return user1
            
        else:
            flagUseUsersTable[0]=False
            client_socket.send("This e-mail is already exist, please try again...".encode(FORMAT))

def client_handler(client_socket, client_address):
    print("Client_handler()")
    try:
        print("Client handler",)
        client_socket.send("Welcome to the server!\n 1.log in \n 2.sign up\n 3.disconect server".encode(FORMAT))
        while True:
            data = client_socket.recv(1024).decode(FORMAT)
            
            #log in:
            if data == "1":
                user1=log_in(client_socket, client_address)
            #sign in:
            elif data == "2":
                user1=sign_in(client_socket, client_address)
            #disconnect server:
            elif data == "3":
                client_socket.send("type 'exit server!' to exit".encode(FORMAT))
                disconnect_server(client_socket, client_address)
                break
            elif data == "exit server!":
                client_socket.send("exit server!".encode(FORMAT))
                user_disconnect(client_socket, client_address)
                disconnect_server(client_socket, client_address)
                break
            else:
                client_socket.send("Wrong input".encode(FORMAT))

            if data == "1" or data == "2":
                menu(client_socket, client_address,user1)
                break
    except Exception as e:
        for i in groups_to_users.keys():
            for j in groups_to_users[i].keys():
                if j.client_socket == client_socket:
                    groups_to_users[i].pop(j)
                    break
        client_socket.close()

def server():
    print("Server()")
    # Bind the socket to a host and port
    server_socket.bind(ADDR)
    print("server is listening...")
    server_socket.listen()
    while True:
        # Accept an incoming connection
        client_socket, client_address = server_socket.accept()
        print("client connected ip:< " + str(client_address) + " >")
        # crate a thread for each client
        client_thread = threading.Thread(target=client_handler, args=(client_socket, client_address))
        client_thread.start()

def main():
    print("Main(), Omer Sela Server")
    connect_DB()
    server()

if __name__ == "__main__":
    main()
