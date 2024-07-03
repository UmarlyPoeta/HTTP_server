import socket
import threading
import os
import sys
import gzip


server_adress = ("localhost", 4221)

def handling_responses(client_socket, request):
    
    # decoding request and spliting based on the \r\n
    status_line,*args = request.decode().split("\r\n")
    
    try:
        method, path, protocol = status_line.split(" ")
    except Exception as e:
        client_socket.send("HTTP/1.1 400 Bad Request\r\n\r\n".encode("utf-8"))
        return
    
    
    if path.startswith("/files/"):
        try:
            command_line_arguments = sys.argv[1:]

            if "--directory" not in command_line_arguments:
                raise Exception
            else:
                path_directory_index = command_line_arguments.index("--directory")+1
        except:
            client_socket.send("HTTP/1.1 400 Bad Request\r\n\r\n".encode("utf-8"))
            return

        string_from_path = path.split("/")[-1]

        file_path = f"{command_line_arguments[path_directory_index]}{string_from_path}"
        
        match method:
            case "GET":
                if os.path.isfile(file_path):
                    file = open(file_path,"rb")
                    content = file.read().decode("utf-8")

                    response = f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {len(content)}\r\n\r\n{content}"
                    client_socket.send(response.encode("utf-8"))
                else:
                    client_socket.send("HTTP/1.1 404 Not Found\r\n\r\n".encode("utf-8"))
                
            case "POST":
                if os.path.isdir(command_line_arguments[path_directory_index]):
                    body_request = args[-1]
                    with open(file_path,"w") as file:
                        file.write(body_request)
                    client_socket.send("HTTP/1.1 201 Created\r\n\r\n".encode("utf-8"))
                else:
                    client_socket.send("HTTP/1.1 404 Not Found\r\n\r\n".encode("utf-8"))   
                    
            case _:
                client_socket.send("HTTP/1.1 400 Bad Request\r\n\r\n".encode("utf-8"))
                return
        
        
    elif path == "/user-agent":
        user_agent=args[1]
        string_from_request = user_agent.split(" ")[-1]
        response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(string_from_request)}\r\n\r\n{string_from_request}"
        client_socket.send(response.encode("utf-8"))
    
    
    
    elif path.startswith("/echo/"): # /echo/{str} endpoint
        string_from_request = path.split("/")[-1]
        response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(string_from_request)}\r\n\r\n{string_from_request}"
        client_socket.send(response.encode("utf-8"))
    
    
    elif path == "/": #validating url path =="/"
        client_socket.send("HTTP/1.1 200 OK\r\n\r\n".encode("utf-8"))
        
        
    else: # executing 404 not found if path is not set to "/"
        client_socket.send("HTTP/1.1 404 Not Found\r\n\r\n".encode("utf-8"))
        

def client_thread(connection,client_address):
    try:
        while True:
            request = connection.recv(1024)
            if not request:
                break
            
            print("request received")
            handling_responses(connection,request)
    finally:
        connection.close()      


def main():
    server_socket = socket.create_server(server_adress, reuse_port=True)
    server_socket.listen(5)

    try:
        while True:
            connection, client_address = server_socket.accept() # wait for client
            threading.Thread(target=client_thread,args=(connection,client_address)).start()
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()
