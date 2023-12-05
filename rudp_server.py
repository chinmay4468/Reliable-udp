import socket
import os
import time
import hashlib

def receive_metadata(client_socket):
    try:
        file_name = client_socket.recv(1024).decode()
        file_size = int(client_socket.recv(1024).decode())
        return file_name, file_size
    except Exception as e:
        print(f"Error receiving metadata: {e}")
        raise

def validate_checksum(data, received_checksum):
    md5 = hashlib.md5()
    md5.update(data)
    calculated_checksum = md5.hexdigest()
    return calculated_checksum == received_checksum

def receive_file(client_socket, file_name, file_size):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(('0.0.0.0', 8888))

    received_size = 0
    last_acknowledged = 0

    try:
        with open(file_name, 'wb') as file:
            while received_size < file_size:
                data, _ = udp_socket.recvfrom(4096)
                received_sequence = int(data[:4].decode())
                received_checksum = data[-32:].decode()
                data = data[4:-32] 
                
                if received_sequence == last_acknowledged + 1 and validate_checksum(data, received_checksum):
                    file.write(data)
                    received_size += len(data)
                    last_acknowledged = received_sequence
                    client_socket.send(f"{last_acknowledged},{received_checksum}".encode())
                    print(f"Acknowledgment sent for packet {last_acknowledged}")
                else:
                    print(f"Received duplicate, out-of-order, or corrupted packet {received_sequence}. Ignoring...")
    except Exception as e:
        print(f"Error receiving file: {e}")
        raise
    finally:
        udp_socket.close()

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 9999))
    server_socket.listen(1)

    print("Waiting for a connection...")
    try:
        client_socket, client_address = server_socket.accept()
        print(f"Connection established with {client_address}")

        file_name, file_size = receive_metadata(client_socket)
        start_time = time.time()
        receive_file(client_socket, 'received_file.txt', file_size)
        end_time = time.time()
        transfer_time = end_time - start_time
        transfer_speed = file_size / (1024 * transfer_time)

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
