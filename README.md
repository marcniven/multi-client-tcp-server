# Multi-Client TCP Server System

A multi-threaded TCP server capable of handling multiple clients, tracking client sessions, and streaming files from a shared repository.

## Features

- Multi-client TCP server using Python sockets
- Concurrent client handling with threading
- Thread-safe shared resource management using locks
- Dynamic client assignment with unique client IDs
- Client status tracking for connection and disconnection times
- Repository file listing and file content streaming
- Simple ACK response system for client-server communication
