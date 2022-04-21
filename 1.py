# -*- coding: utf-8 -*-
# tcp mapping created by hutaow(hutaow.com) at 2014-08-31
import socket
import threading
import multiprocessing

# 端口映射配置信息

# 接收数据缓存大小
PKT_BUFF_SIZE = 2048


# 调试日志封装

def send_log(content):
    print(content)
    return


# 单向流数据传递
def tcp_mapping_worker(conn_receiver, conn_sender):
    while True:
        try:
            data = conn_receiver.recv(PKT_BUFF_SIZE)
        except Exception:
            send_log('Event: Connection closed.')
            break

        if not data:
            send_log('Info: No more data is received.')
            break
        try:
            conn_sender.sendall(data)
            # send_log('Info: Mapping data > %s ' % repr(data))
            send_log('Info: Mapping >%s->%s>%dbytes.' % (conn_receiver.getpeername(), conn_sender.getpeername(), len(data)))
        except Exception:
            send_log('Error: Failed sending data.')
            break


    conn_receiver.close()
    conn_sender.close()
    return


# 端口映射请求处理
def tcp_mapping_request(local_conn, remote_ip, remote_port):
    remote_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        remote_conn.connect((remote_ip, remote_port))
    except Exception:
        local_conn.close()
        send_log('\tUnable to connect to the remote server.')
        return

    threading.Thread(target=tcp_mapping_worker, args=(local_conn, remote_conn)).start()
    threading.Thread(target=tcp_mapping_worker, args=(remote_conn, local_conn)).start()
    return


# 端口映射函数
def tcp_mapping(remote_ip, remote_port, local_ip, local_port):
    local_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    local_server.bind((local_ip, local_port))
    local_server.listen(5)
    send_log('Event: Starting mapping service on ' + local_ip + ':' + str(local_port) + ' ...')
    while True:
        try:
            (local_conn, local_addr) = local_server.accept()

            threading.Thread(target=tcp_mapping_request, args=(local_conn, remote_ip, remote_port)).start()
            send_log('\tReceive mapping request from%s:%d.' % local_addr)
        except Exception:
            local_server.close()
            send_log('\tStop mapping service.')
            break

    return

# 单向流数据传递
def udp_mapping_worker(conn_receiver, conn_sender):
    while True:
        try:
            data = conn_receiver.recv(PKT_BUFF_SIZE)
        except Exception:
            send_log('Event: Connection closed.')
            break

        if not data:
            send_log('Info: No more data is received.')
            break
        try:
            conn_sender.sendall(data)
            # send_log('Info: Mapping data > %s ' % repr(data))
            send_log('Info: Mapping >%s->%s>%dbytes.' % (conn_receiver.getpeername(), conn_sender.getpeername(), len(data)))
        except Exception:
            send_log('Error: Failed sending data.')
            break


    conn_receiver.close()
    conn_sender.close()
    return


# 端口映射请求处理
def udp_mapping_request(local_conn, remote_ip, remote_port):
    remote_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        remote_conn.connect((remote_ip, remote_port))
    except Exception:
        local_conn.close()
        send_log('\tUnable to connect to the remote server.')
        return

    threading.Thread(target=tcp_mapping_worker, args=(local_conn, remote_conn)).start()
    threading.Thread(target=tcp_mapping_worker, args=(remote_conn, local_conn)).start()
    return


# 端口映射函数
def udp_mapping(remote_ip, remote_port, local_ip, local_port):


    UdpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    UdpSocket.bind((local_ip, local_port))
    while True:
        TempData = UdpSocket.recvfrom(PKT_BUFF_SIZE)




# 主函数
if __name__ == '__main__':
    pool = multiprocessing.Pool(processes=5)

    pool.apply_async(tcp_mapping, ('192.168.Test.202', 22, '172.19.132.15', 12345))
    pool.apply_async(tcp_mapping, ('192.168.Test.202', 3306, '172.19.132.15', 3306))
    pool.apply_async(tcp_mapping, ('192.168.Test.202', 10013, '172.19.132.15', 10013))
    pool.apply_async(tcp_mapping, ('192.168.Test.202', 7001, '172.19.132.15', 7001))



    pool.close()
    pool.join()
