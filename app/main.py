# Uncomment this to pass the first stage
import socket

server_adress = ("localhost", 4221)

def main():

    server_socket = socket.create_server(server_adress, reuse_port=True)
    
    # Listen for incoming connections
    server_socket.listen(1)
    
    while True:
        connection, client_address = server_socket.accept() # wait for client
        try:
            request = connection.recv(1024)
            
            print("request received")
            
            
            connection.send("HTTP/1.1 200 OK\r\n\r\n".encode("utf-8"))
        
        
        
        finally:
            connection.close()

if __name__ == "__main__":
    main()
