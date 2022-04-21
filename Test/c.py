import socket

client = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
client.connect(('192.168.200.Test', 80))
client.setblocking(False)
# r = client.recv(1024).decode('utf-8')
# print(r)
client.sendall(b"123456")
client.sendall("000".encode('utf-8'))