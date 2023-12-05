import socket
import os
import time
import hashlib

def send_metadata(server_socket, file_name, file_size):
    try:
        server_socket.send(file_name.encode())
        server_socket.send(str(file_size).encode())
    except Exception as e:
        print(f"Error sending metadata: {e}")
        raise

def calculate_checksum(data):
    md5 = hashlib.md5()
    md5.update(data)
    return md5.hexdigest()

def send_file(server_socket, file_name, file_size):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        with open(file_name, 'rb') as file:
            chunk_size = 1020  
            sequence_number = 1
            max_retransmissions = 3
            last_acknowledged = 0
            start_time = time.time()

            while True:
                data = file.read(chunk_size)
                if not data:
                    break  

                checksum = calculate_checksum(data)
                packet = f"{sequence_number:04d}".encode() + data + checksum.encode()
                udp_socket.sendto(packet, ('localhost', 8888))
                
                try:
                    acknowledgment = server_socket.recv(1024).decode()
                    received_sequence, received_checksum = acknowledgment.split(',')
                    received_sequence = int(received_sequence)

                    if received_sequence == sequence_number and received_checksum == checksum:
                        print(f"Acknowledgment received for packet {received_sequence}")
                        last_acknowledged = received_sequence
                        sequence_number += 1
                    else:
                        print(f"Received acknowledgment for old, out-of-order, or corrupted packet {received_sequence}. Retransmitting...")
                except socket.timeout:
                    print(f"Timeout! Retransmitting packet {sequence_number}")

            end_time = time.time()

            transfer_time = end_time - start_time
            transfer_speed = file_size / (1024 * transfer_time)
            print(f"Transfer time: {transfer_time:.2f} seconds")
            print(f"Transfer speed: {transfer_speed:.2f} KB/s")
            print("File sent successfully.")
                
    except Exception as e:
        print(f"Error sending file: {e}")
        raise
    finally:
        udp_socket.close()

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server_socket.connect(('localhost', 9999))
        server_socket.settimeout(1.0)

        file_name = input("Enter the file name: ")
        file_size = os.path.getsize(file_name)

        send_metadata(server_socket, file_name, file_size)
        send_file(server_socket, file_name,file_size)

        print("File transfer completed.")
    except Exception as e:
        print(f"Error during file transfer: {e}")
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()
