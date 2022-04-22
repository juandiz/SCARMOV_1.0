import socket
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('127.0.0.1',3000))

while True:
    try:
        data,addr = sock.recvfrom(1024)
        print(data)
    except:
        time.sleep(1)