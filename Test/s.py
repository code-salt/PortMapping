import socket

sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
# sock.setblocking(False)
sock.bind(("192.168.200.131", 3306))  # 绑定端口
sock.listen()
connect, address = sock.accept()
r = connect.recv(1024).decode('utf-8')
print(r)
connect.send(r.encode('utf-8'))