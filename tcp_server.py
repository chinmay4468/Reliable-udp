import socket
import time
import os

def receive_file(client_socket, file_name):
    try:
        with open(file_name, 'wb') as file:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                file.write(data)
    except Exception as e:
        print(f"Error receiving file: {e}")
        raise

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 9999))
    server_socket.listen(1)

    print("Waiting for a connection...")
    try:
        client_socket, client_address = server_socket.accept()
        print(f"Connection established with {client_address}")

        start_time = time.time()
        receive_file(client_socket, 'received_file.txt')
        end_time = time.time()

        transfer_time = end_time - start_time
        transfer_speed = os.path.getsize('received_file.txt') / (1024 * transfer_time)

        print("File transfer completed.")
        print(f"Transfer time: {transfer_time:.2f} seconds")
        print(f"Transfer speed: {transfer_speed:.2f} KB/s")

    except Exception as e:
        print(f"Error during file transfer: {e}")
    finally:
        client_socket.close()
        server_socket.close()

if __name__ == "__main__":
    main()
