from socket import *
import sys
serverName = 'localhost'
serverPort = 2222

#create TCP socket
clientSocket = socket(AF_INET, SOCK_STREAM)

#connect to the server and recieve our unique name
clientSocket.connect((serverName,serverPort))

myName = clientSocket.recv(1024).decode()

if myName == "Server full": #if server is full, connection has already been terminated, so quit the program
    print(myName, ". Exiting program.")
    quit() #exit program

print ("Our unique name is: ", myName) #server not full, recieve name and proceed

clientSocket.send(myName.encode())


while True: 
    #prompt user for an input to be modified by server and send it to server
    print("\nMenu:")
    print("1. Enter a sentence to append 'ACK'")
    print("2. To view client statuses (type 'status')")
    print("3. To list repository files for viewing (type 'list')")
    print("4. To exit (type 'exit')")
    sentence = input("\nSelect an option or enter your sentence: ")

    if sentence.lower() == "exit":
        print("Exiting program, goodbye.")
        clientSocket.send(sentence.encode())
        clientSocket.close()
        break

    elif sentence.lower() == "status":
        clientSocket.send(sentence.encode()) #send 'status' to server
        cliCache = clientSocket.recv(1024).decode() #recieve status
        print("Active clients: \n", cliCache)

    elif sentence.lower() == "list":
        clientSocket.send(sentence.encode()) #send 'list' to server
        list = clientSocket.recv(1024).decode() #recieve list of files
        print ('File List:', list)
        if list == 'Repository empty.':
            continue
        choice = input('Type the name of the file to stream (including the file extension): ')
        clientSocket.send(choice.encode()) #send the file name to server
        chosen = clientSocket.recv(1024).decode() #recieve contents of the selected file
        print('---------------------------------\n', chosen)

    else:
        clientSocket.send(sentence.encode())
        modifiedSentence = clientSocket.recv(1024) #recieve upto 1024 bytes
        print ('From Server:', modifiedSentence.decode()) #print modified sentence


