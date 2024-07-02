import socket
import threading

server_adress = ("localhost", 4221)

def handling_responses(client_socket, request):
    
    # decoding request and spliting based on the \r\n
    status_line,*args = request.decode().split("\r\n")
    
    print(status_line)
    try:
        method, path, protocol = status_line.split(" ")
    except Exception as e:
        client_socket.send("HTTP/1.1 400 Bad Request\r\n\r\n".encode("utf-8"))
        return
    
    
    if path == "/user-agent":
        user_agent=args[1]
        string_from_request = user_agent.split(" ")[-1]
        response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(string_from_request)}\r\n\r\n{string_from_request}"
        client_socket.send(response.encode("utf-8"))
    
    
    
    if path.startswith("/echo/"): # /echo/{str} endpoint
        string_from_request = path.split("/")[-1]
        response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(string_from_request)}\r\n\r\n{string_from_request}"
        client_socket.send(response.encode("utf-8"))
    
    
    elif path == "/": #validating url path =="/"
        client_socket.send("HTTP/1.1 200 OK\r\n\r\n".encode("utf-8"))
        
        
    else: # executing 404 not found if path is not set to "/"
        client_socket.send("HTTP/1.1 404 Not Found\r\n\r\n".encode("utf-8"))
        

def client_thread(connection):
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
            threading.Thread(target=client_thread,args=(connection,)).start()
            
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()
