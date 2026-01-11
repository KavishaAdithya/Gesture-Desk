import socket
import struct
import cv2
import numpy as np

HOST = "0.0.0.0"
PORT = 8000

server_Socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server_Socket.bind((HOST,PORT))
server_Socket.listen(1)
print(f"Litsening on {HOST}:{PORT}")


while True:
    connct,address = server_Socket.accept()
    print(f"Connected by {address}")
    size_data = connct.recv(4)
    if not size_data:
        continue
    img_size = struct.unpack("<I",size_data)[0]

    img_data = b''
    while len(img_data)<img_size:
        packet = connct.recv(4096)
        if not packet:
            break
        img_data += packet
    
    np_arr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if img is not None:
        cv2.imshow('Received Image', img)
        cv2.waitKey(1)

