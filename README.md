[![progress-banner](https://backend.codecrafters.io/progress/http-server/4c3fd9b4-6785-4d24-81ee-6ad6e29fc06e)](https://app.codecrafters.io/users/codecrafters-bot?r=2qF)

This is a starting point for Python solutions to the
["Build Your Own HTTP server" Challenge](https://app.codecrafters.io/courses/http-server/overview).

[HTTP](https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol) is the
protocol that powers the web. In this challenge, you'll build a HTTP/1.1 server
that is capable of serving multiple clients.

Along the way you'll learn about TCP servers,
[HTTP request syntax](https://www.w3.org/Protocols/rfc2616/rfc2616-sec5.html),
and more.

**Note**: If you're viewing this repo on GitHub, head over to
[codecrafters.io](https://codecrafters.io) to try the challenge.

# Simple Python HTTP Server

This project is a simple HTTP server implemented in Python. It handles basic HTTP methods such as GET and POST, and provides endpoints for file handling, user-agent information, and echo functionality. The server supports multithreading to handle multiple client connections simultaneously.

## Features

1. **File Handling**:
   - **GET**: Retrieve files from a specified directory.
   - **POST**: Upload files to a specified directory.
2. **User-Agent Endpoint**:
   - Responds with the client's User-Agent string, optionally compressed using gzip if requested.
3. **Echo Endpoint**:
   - Echoes back a string provided in the URL path, with optional gzip compression.
4. **Root Endpoint**:
   - Returns a simple 200 OK status for the root path.

## Requirements

- Python 3.x
- `socket`, `threading`, `os`, `sys`, `gzip`, `re` modules (all are part of the Python standard library)

## Usage

### Running the Server

To run the server, use the following command:

```bash
python server.py --directory /path/to/your/directory
```

Replace `/path/to/your/directory` with the path to the directory where you want to handle file operations.

### Endpoints

1. **File Handling**

   - **GET /files/{filename}**
     - Retrieves the specified file from the directory.
     - Example: `GET /files/example.txt`
   
   - **POST /files/{filename}**
     - Uploads content to the specified file in the directory.
     - Example: `POST /files/example.txt` with body content.

2. **User-Agent**

   - **GET /user-agent**
     - Returns the client's User-Agent string.
     - Supports gzip compression if requested.
     - Example: `GET /user-agent`

3. **Echo**

   - **GET /echo/{string}**
     - Echoes back the string provided in the URL path.
     - Supports gzip compression if requested.
     - Example: `GET /echo/hello`

4. **Root**

   - **GET /**
     - Returns a simple 200 OK status.
     - Example: `GET /`

## Code Overview

### Server Initialization

The server is initialized to listen on `localhost` at port `4221`:

```python
server_address = ("localhost", 4221)
```

### Handling Client Requests

Client requests are handled by the `handle_responses` function, which decodes the request, processes it based on the method and path, and sends the appropriate response:

```python
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
```

### Multithreading

The server uses threading to handle multiple client connections concurrently:

```python
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
```

### Main Function

The main function sets up the server and listens for incoming connections:

```python
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
```

## Contributions

Contributions are welcome! Please fork the repository and submit a pull request for any features or improvements you would like to add.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
1. Run `./your_server.sh` to run your program, which is implemented in
   `app/main.py`.
1. Commit your changes and run `git push origin master` to submit your solution
   to CodeCrafters. Test output will be streamed to your terminal.
