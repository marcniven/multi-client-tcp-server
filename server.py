from socket import *
import time
import threading
import os

port = 2222  #port number for server to listen on
max_clients = 3  #maximum number of concurrent clients allowed

servSocket = socket(AF_INET, SOCK_STREAM)  #create a TCP socket

servSocket.bind(('', port))  #bind socket to port, '' empty string means it will accept any incoming connection from the IP address on our machine

servSocket.listen(max_clients)  # wait and listen, upto 3 clients
print('The server is ready to receive.') # now the server is set up and waiting, we go to the client side to configure

available = [f"Client0{i+1}" for i in range(max_clients)]  #initialize the active clients list
activeClients = []  #list of active clients
clientCache = []  # the cache where client info will be saved
lock = threading.Lock()  # Lock shared resources so only 1 client can access at a time

def handle_client(connectionSocket, addr):
    with lock: #aquire the lock for shared resources
        if not available: #available list is empty
            connectionSocket.send("Server full".encode())
            connectionSocket.close() 
            return

        #assign the new name to each client
        sendName = available.pop(0) #retrieve available client name and remove that name from available list
        connectionSocket.send(sendName.encode()) #send the client their unique name

        #get a response from the client
        clientResponse = connectionSocket.recv(1024).decode() #client name
        print(f"{clientResponse} has joined the server.")

        #update the client cache with the new client info
        client_info = {
            "name": sendName,
            "connected_at": time.ctime(),
            "disconnected_at": None
        }
        clientCache.append(client_info)
        activeClients.append(sendName) #add the client name to the active list

    #another infinite loop but this time to recieve message from client and send it back according to what they sent
    while True:
        try: #recv() function could raise ConnectionResetError if client crashes/disconnects
            sentence = connectionSocket.recv(1024).decode() #receive the sentence from the client

            if sentence.lower() == "exit": #if the client sends exit, close the connection and remove from active and update disconnect time
                with lock: #aquire the lock for shared resources
                    client_info["disconnected_at"] = time.ctime()
                    activeClients.remove(sendName) # remove client from active list
                    available.append(sendName) #add the name back to available list
                    available.sort() #keep available list sorted
                print(f"{sendName} left server")
                break #exit while loop to close connection

            elif sentence.lower() == "status": #if the client sends status then send back the cache data
                with lock: #aquire the lock for shared resources
                    status_message = "\n".join([f"{c['name']}\n----------\nConnected: {c['connected_at']}\nDisconnected: {c['disconnected_at']}\n" for c in clientCache])
                connectionSocket.send(status_message.encode()) # Send cache data back to client

            elif sentence.lower() == "list":   #reply with the list of files
                file_string = "\n"
                path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"repo") #path to repo dynamically
                if not os.path.exists(path): #if the path does not exist, create it
                    os.makedirs(path)
                file_list = os.listdir(path)
                if len(file_list)<1: #no files in repo
                    connectionSocket.send("Repository empty.".encode())
                else:
                    for file in file_list:
                        file_string += file + "\n"
                    connectionSocket.send(file_string.encode())
                    target = connectionSocket.recv(1024).decode() #file wanted
                    if target in file_list:
                        with open(os.path.join(path, target), "r") as file:
                            contents = file.read()
                        connectionSocket.send(contents.encode())
                    else:
                        connectionSocket.send("File does not exist.".encode())
                
            else:
                ACKappend = sentence + "ACK" #append "ACK" to the sentence
                connectionSocket.send(ACKappend.encode()) #send the modified sentence back to the client

        except ConnectionResetError:
            print(f"{sendName} disconnected.")
            break #exit while loop to close connection
    
    #disconnect client and update active and available client lists
    connectionSocket.close() #close the connection
    with lock: 
        if sendName in activeClients:
            activeClients.remove(sendName)
        if sendName not in available:
            available.append(sendName)
        available.sort()

# Main server loop
while True:
    connectionSocket, addr = servSocket.accept()
    #create a new thread, target is the function to run, args is the arguments
    client_thread = threading.Thread(target=handle_client, args=(connectionSocket, addr)) 
    client_thread.start() #start the thread