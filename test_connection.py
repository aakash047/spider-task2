import socket
import sys

def test_connection(host, port):
    try:
        sock = socket.create_connection((host, port), timeout=5)
        sock.close()
        print(f"Successfully connected to {host}:{port}")
    except Exception as e:
        print(f"Failed to connect to {host}:{port}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python test_connection.py <host> <port>")
        sys.exit(1)
    
    host = sys.argv[1]
    port = int(sys.argv[2])
    test_connection(host, port)