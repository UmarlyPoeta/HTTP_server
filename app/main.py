import socket
import threading
import os
import sys
import gzip
import re

server_address = ("localhost", 4221)

def handle_responses(client_socket, request):
    try:
        # Decode the request and split based on \r\n
        status_line, *args = request.decode().split("\r\n")
        
        # Check if status line is divided into method, path, and protocol
        method, path, protocol = status_line.split(" ")
        
        if path.startswith("/files/"):  # Handling file returning and posting
            command_line_arguments = sys.argv[1:]  # Getting --directory command line dir path
            if "--directory" in command_line_arguments:
                path_directory_index = command_line_arguments.index("--directory") + 1
            else:
                raise Exception("Directory argument not found")
            
            string_from_path = path.split("/")[-1]  # Getting file name
            file_path = os.path.join(command_line_arguments[path_directory_index], string_from_path)
            
            if method == "GET":
                if os.path.isfile(file_path):  # Check if path is valid and exists
                    with open(file_path, "rb") as file:
                        content = file.read()
                    response = (
                        f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\n"
                        f"Content-Length: {len(content)}\r\n\r\n"
                    ).encode("utf-8") + content
                    client_socket.send(response)
                else:
                    client_socket.send("HTTP/1.1 404 Not Found\r\n\r\n".encode("utf-8"))
            elif method == "POST":
                if os.path.isdir(command_line_arguments[path_directory_index]):  # Check if path is valid and directory exists
                    body_request = args[-1]  # Getting body content that will be written into the file
                    with open(file_path, "w") as file:  # Creating file and writing content in it
                        file.write(body_request)
                    client_socket.send("HTTP/1.1 201 Created\r\n\r\n".encode("utf-8"))
                else:
                    client_socket.send("HTTP/1.1 404 Not Found\r\n\r\n".encode("utf-8"))
            else:
                client_socket.send("HTTP/1.1 400 Bad Request\r\n\r\n".encode("utf-8"))
        elif path == "/user-agent":
            user_agent = args[1]
            string_from_request = user_agent.split(" ")[-1]
            if "Accept-Encoding: " in request.decode("utf-8") and "gzip" in request.decode("utf-8"):
                compressed_string_from_request = gzip.compress(string_from_request.encode())
                response = (
                    f"HTTP/1.1 200 OK\r\nContent-Encoding: gzip\r\nContent-Type: text/plain\r\n"
                    f"Content-Length: {len(compressed_string_from_request)}\r\n\r\n"
                ).encode("utf-8") + compressed_string_from_request
            else:
                response = (
                    f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(string_from_request)}\r\n\r\n"
                    f"{string_from_request}"
                ).encode("utf-8")
            client_socket.send(response)
        elif path.startswith("/echo/"):  # /echo/{str} endpoint
            string_from_request = path.split("/")[-1]
            if "Accept-Encoding: " in request.decode("utf-8") and "gzip" in request.decode("utf-8"):
                compressed_string_from_request = gzip.compress(string_from_request.encode())
                response = (
                    f"HTTP/1.1 200 OK\r\nContent-Encoding: gzip\r\nContent-Type: text/plain\r\n"
                    f"Content-Length: {len(compressed_string_from_request)}\r\n\r\n"
                ).encode("utf-8") + compressed_string_from_request
            else:
                response = (
                    f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(string_from_request)}\r\n\r\n"
                    f"{string_from_request}"
                ).encode("utf-8")
            client_socket.send(response)
        elif path == "/":  # validating url path =="/"
            client_socket.send("HTTP/1.1 200 OK\r\n\r\n".encode("utf-8"))
        else:  # executing 404 not found if path is not set to "/"
            client_socket.send("HTTP/1.1 404 Not Found\r\n\r\n".encode("utf-8"))
    except Exception as e:
        # Sending response informing that the request syntax is invalid
        client_socket.send("HTTP/1.1 400 Bad Request\r\n\r\n".encode("utf-8"))

def client_thread(connection, client_address):
    try:
        while True:
            # getting client request
            request = connection.recv(1024)
            if not request:  # if request is not given connection is being closed
                break
            
            print("request received")
            # executing function that sends an appropriate response
            handle_responses(connection, request)
    finally:
        connection.close()

def main():
    # Creating server on port 4221
    server_socket = socket.create_server(server_address, reuse_port=True)
    
    # Allowing max 5 connections simultaneously
    server_socket.listen(5)

    try:
        while True:
            connection, client_address = server_socket.accept()  # wait for client
            
            # Creating a thread that operates one connection
            threading.Thread(target=client_thread, args=(connection, client_address)).start()
    finally:
        # closing server socket
        server_socket.close()

if __name__ == "__main__":
    main()
