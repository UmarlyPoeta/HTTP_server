import socket
import threading
import os
import sys
import gzip
import re


server_adress = ("localhost", 4221)

def handling_responses(client_socket, request):
    
    # decoding request and spliting based on the \r\n
    status_line,*args = request.decode().split("\r\n")
    
    
    # Checking if status line is divided to method, path and protocol
    try:
        method, path, protocol = status_line.split(" ")
    except Exception as e:
        # Sending response informing that the request syntax is invalid
        client_socket.send("HTTP/1.1 400 Bad Request\r\n\r\n".encode("utf-8"))
        return
    
    
    if path.startswith("/files/"): #handling file returning and posting
        try:
            command_line_arguments = sys.argv[1:] #Getting --directory command line dir path

            if "--directory" not in command_line_arguments: #Checking if --directory is not in cmd args
                raise Exception
            else: # getting index with dir path to get it from command line arguments
                path_directory_index = command_line_arguments.index("--directory")+1
        except:
             # Sending response informing that the request syntax is invalid
            client_socket.send("HTTP/1.1 400 Bad Request\r\n\r\n".encode("utf-8"))
            return

        string_from_path = path.split("/")[-1] #getting file name

        file_path = f"{command_line_arguments[path_directory_index]}{string_from_path}"
        
        match method:
            case "GET":
                if os.path.isfile(file_path): #checkinh if path is valid and exists
                    file = open(file_path,"rb")
                    content = file.read().decode("utf-8") #reading file content and decoding it to string
            
                    response = f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {len(content)}\r\n\r\n{content}"
                    client_socket.send(response.encode("utf-8"))
                else:
                    client_socket.send("HTTP/1.1 404 Not Found\r\n\r\n".encode("utf-8"))
                
            case "POST":
                if os.path.isdir(command_line_arguments[path_directory_index]): #checkinh if path is valid and directory exist
                    body_request = args[-1] #getting body content that will be written into the file
                    with open(file_path,"w") as file: #creating file and writing content in it
                        file.write(body_request)
                    client_socket.send("HTTP/1.1 201 Created\r\n\r\n".encode("utf-8"))
                else:
                    client_socket.send("HTTP/1.1 404 Not Found\r\n\r\n".encode("utf-8"))   
                    
            case _: # if method is not get or post its sending bad request response
                client_socket.send("HTTP/1.1 400 Bad Request\r\n\r\n".encode("utf-8"))
                return
        
        
    elif path == "/user-agent":
        user_agent=args[1]
        
        string_from_request = user_agent.split(" ")[-1]
        if "Accept-Encoding: gzip\r\n" in request.decode() and "gzip" in request.decode("utf-8"):
            response = f"HTTP/1.1 200 OK\r\nContent-Encoding: gzip\r\nContent-Type: text/plain\r\nContent-Length: {len(string_from_request)}\r\n\r\n{gzip.compress(string_from_request.encode("utf-8"))}"
        else:
            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(string_from_request)}\r\n\r\n{string_from_request}"
        client_socket.send(response.encode("utf-8"))
    
    
    
    elif path.startswith("/echo/"): # /echo/{str} endpoint
        string_from_request = path.split("/")[-1]
        
        
        if "Accept-Encoding: " in request.decode() and "gzip" in request.decode("utf-8"):
            response = f"HTTP/1.1 200 OK\r\nContent-Encoding: gzip\r\nContent-Type: text/plain\r\nContent-Length: {len(string_from_request)}\r\n\r\n{gzip.compress(string_from_request.encode("utf-8"))}"
        else:
            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(string_from_request)}\r\n\r\n{string_from_request}"

        client_socket.send(response.encode("utf-8"))
    
    
    elif path == "/": # validating url path =="/"
        client_socket.send("HTTP/1.1 200 OK\r\n\r\n".encode("utf-8"))
        
        
    else: # executing 404 not found if path is not set to "/"
        client_socket.send("HTTP/1.1 404 Not Found\r\n\r\n".encode("utf-8"))
        

def client_thread(connection,client_address):
    try:
        while True:
            # getting client request
            request = connection.recv(1024)
            if not request: #if request is not given connection is being closed
                break
            
            print("request received")
            # executing function that sends an appropriate response
            handling_responses(connection,request)
    finally:
        connection.close()      


def main():
    # Creating server on port 4221
    server_socket = socket.create_server(server_adress, reuse_port=True)
    
    # Allowing to max 5 connections simultaneously
    server_socket.listen(5)

    try:
        while True:
            connection, client_address = server_socket.accept() # wait for client
            
            # Creating a thread that operates one connection
            threading.Thread(target=client_thread,args=(connection,client_address)).start()
    finally:
        #closing server socket
        server_socket.close()

if __name__ == "__main__":
    main()
