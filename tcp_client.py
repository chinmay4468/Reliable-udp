import socket
import os
import time

def send_file(server_socket, file_name):
    try:
        with open(file_name, 'rb') as file:
            start_time = time.time()
            while True:
                data = file.read(1024)
                if not data:
                    break
                server_socket.send(data)
            end_time = time.time()

            transfer_time = end_time - start_time
            transfer_speed = os.path.getsize(file_name) / (1024 * transfer_time)

            print(f"File '{file_name}' sent successfully.")
            print(f"Transfer time: {transfer_time:.2f} seconds")
            print(f"Transfer speed: {transfer_speed:.2f} KB/s")

    except Exception as e:
        print(f"Error sending file: {e}")
        raise

def main():
    server_address = ('localhost', 9999)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server_socket.connect(server_address)
        file_name = input("Enter the file name: ")
        send_file(server_socket, file_name)

    except Exception as e:
        print(f"Error during file transfer: {e}")
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()
