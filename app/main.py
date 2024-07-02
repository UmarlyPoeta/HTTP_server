# Uncomment this to pass the first stage
import socket

server_adress = ("localhost", 4221)

def main():

    server_socket = socket.create_server(server_adress, reuse_port=True)
    
    # Listen for incoming connections
    server_socket.listen(1)
    
    try:
        connection, client_address = server_socket.accept() # wait for client
        while True:
            request = connection.recv(1024)
            request_string = request.decode().split(" ")
            print("request received")
            
            
            if request_string[1] == "/":
                connection.send("HTTP/1.1 200 OK\r\n\r\n".encode("utf-8"))
            else:
                connection.send("HTTP/1.1 404 Not Found\r\n\r\n".encode("utf-8"))
        
    finally:
        connection.close()

if __name__ == "__main__":
    main()
