import socket

server_adress = ("localhost", 4221)

def handling_responses(client_socket,request_status_line):
    
    method, path, protocol = request_status_line.split(" ")
    
    if path.startswith("/echo/"): # /echo/{str} endpoint
        string_from_request = path.split("/")[-1]
        client_socket.send(f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(string_from_request)}\r\n\r\n{string_from_request}".encode("utf-8"))
    
    
    elif path == "/": #validating url path =="/"
        client_socket.send("HTTP/1.1 200 OK\r\n\r\n".encode("utf-8"))
        
        
    else: # executing 404 not found if path is not set to "/"
        client_socket.send("HTTP/1.1 404 Not Found\r\n\r\n".encode("utf-8"))
        



def main():
    server_socket = socket.create_server(server_adress, reuse_port=True)
    
    # Listen for incoming connections
    server_socket.listen(1)
    
    
    try:
        
        connection, client_address = server_socket.accept() # wait for client
        
        while True:
            #Getting request
            request: bytes = connection.recv(1024)
            
            print("request received")
            
            # decoding request and spliting based on the whitespaces 
            status_line, headers, body,*args = request.decode().split("\r\n")
            
            #extract_url_path(connection,status_line)
            handling_responses(connection,status_line)
            
            
        
    finally:
        connection.close()

if __name__ == "__main__":
    main()
