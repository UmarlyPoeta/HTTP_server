import socket

server_adress = ("localhost", 4221)


def main():
    server_socket = socket.create_server(server_adress, reuse_port=True)
    
    # Listen for incoming connections
    server_socket.listen(1)
    
    
    try:
        
        connection, client_address = server_socket.accept() # wait for client
        
        while True:
            #Getting request
            request = connection.recv(1024)
            
            print("request received")
            
            # decoding request and spliting based on the whitespaces 
            request_string = request.decode().split(" ")
            
            # Sending status 200 if path = "/" in other scenarios status 404
            if request_string[1] == "/":
                connection.send("HTTP/1.1 200 OK\r\n\r\n".encode("utf-8"))
            else:
                connection.send("HTTP/1.1 404 Not Found\r\n\r\n".encode("utf-8"))
        
    finally:
        connection.close()

if __name__ == "__main__":
    main()
