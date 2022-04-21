# -* -coding: UTF-8 -* -
'''
python3.8.10
Created on 2022-4-1
@author: lws
'''
import time, socket, threading, os, shutil


def log(strLog):
    strs = time.strftime("%H:%M:%S")  # %Y-%m-%d %H:%M:%S
    print(strs + "->" + strLog)
    return strs.replace(':','_')

def writefile(file_path,data):
    with open(file_path, 'wb')as f:
        f.write(data)


class pipethread(threading.Thread):
    '''
    classdocs
    '''

    def __init__(self, source, sink, model='T', path=None):
        '''
        Constructor
        '''
        threading.Thread.__init__(self)
        self.source = source
        self.sink = sink
        self.model = model
        self.path = path
        self.buildTime = os.path.basename(self.path)
        if self.model == 'R':
            # model == 'R' : 回
            log(f"创建新的管道:{self.sink.getpeername()} <<<< {self.source.getpeername()}")
        else:
            # model == 'T': 去
            log(f"创建新的管道:{self.source.getpeername()} >>>> {self.sink.getpeername()}")

    def run(self):
        while True:
            try:
                data = self.source.recv(8192)
                if not data:
                    raise Exception
                self.sink.send(data)
                if not self.path is None:
                    writefile(fr"{self.path}\{time.time():.8f}{self.model}",data)
            except Exception as ex:
                if self.model == 'R':
                    log(f"被动断开{self.buildTime}:" + str(ex))
                else:
                    log(f"主动断开{self.buildTime}:" + str(ex))
                writefile(fr"{self.path}\{time.time():.8f}{self.model}B", b'')
                break
        self.source.close()
        self.sink.close()


class portmap(threading.Thread):
    # 线程对象：TCP端口映射
    def __init__(self, local, newhost):
        # 初始化
        threading.Thread.__init__(self)  # 线程初始化
        self.new_ip, self.new_port = newhost  # 远映射IP：121.40.224.81# 远映射Port：80
        self.local_ip, self.local_port = local  # 近映射IP：192.168.200.Test# 近映射Port：80

        self.sock = None  # self.sock 近服务sock
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.local_ip, self.local_port))
        self.sock.listen(5)
        log(f"开始{'TCP'}端口映射: -->> {(self.local_ip,self.local_port)} <<-->> {(self.new_ip, self.new_port)}")


        self.temp_dir = os.path.abspath(fr"TCP\{(self.local_ip,self.local_port)}-{(self.new_ip, self.new_port)}")
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)


    def run(self):
        while True:
            fwd = None
            newsock = None
            newsock, address = self.sock.accept()  # 有客户端连接近服务sock
            log(f"新TCP连接->:,{address} -->> {(self.local_ip,self.local_port)}")

            fwd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 创建一个中间客户端
            try:
                fwd.connect((self.new_ip, self.new_port))  # 中间客户端去连接远服务器
            except Exception as ex:
                log("为‘新连接’连接远服务器错误:" + str(ex))
                break
            # 建立记录文件夹
            data_dir = os.path.abspath(fr"{self.temp_dir}\{time.time():.8f}")
            os.makedirs(data_dir)
            # 创建两个线程来进行全双工通信
            T = pipethread(newsock, fwd, model='T', path=data_dir)  # 从newsock接收，转发给fwd T去
            T.start()
            R = pipethread(fwd, newsock, model='R', path=data_dir)  # 从fwd接收，转发给newsock R回
            R.start()


class pipethreadUDP(threading.Thread):
    def __init__(self, connection, connectionTable, table_lock):
        threading.Thread.__init__(self)
        self.connection = connection
        self.connectionTable = connectionTable
        self.table_lock = table_lock
        log('new thread for new connction')

    def run(self):
        while True:
            try:
                data, addr = self.connection['socket'].recvfrom(4096)
                # log('recv from addr"%s' % str(addr))
            except Exception as ex:
                log("recvfrom error:" + str(ex))
                break
            try:
                self.connection['lock'].acquire()
                self.connection['Serversocket'].sendto(data, self.connection['address'])
                # log('sendto address:%s' % str(self.connection['address']))
            except Exception as ex:
                log("sendto error:" + str(ex))
                break
            finally:
                self.connection['lock'].release()
            self.connection['time'] = time.time()
        self.connection['socket'].close()
        log("thread exit for: %s" % str(self.connection['address']))
        self.table_lock.acquire()
        self.connectionTable.pop(self.connection['address'])
        self.table_lock.release()
        log('Release udp connection for timeout:%s' % str(self.connection['address']))


class portmapUDP(threading.Thread):
    def __init__(self, port, newhost, newport, local_ip=''):
        threading.Thread.__init__(self)
        self.newhost = newhost
        self.newport = newport
        self.port = port
        self.local_ip = local_ip
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.local_ip, port))
        self.connetcTable = {}
        self.port_lock = threading.Lock()
        self.table_lock = threading.Lock()
        self.timeout = 300
        # ScanUDP(self.connetcTable,self.table_lock).start()
        log('udp local_port redirect run->local_ip:%s,local_port:%d,remote_ip:%s,remote_port:%d' % (
        local_ip, port, newhost, newport))

    def run(self):
        while True:
            data, addr = self.sock.recvfrom(4096)
            connection = None
            newsock = None
            self.table_lock.acquire()
            connection = self.connetcTable.get(addr)
            newconn = False
            if connection is None:
                connection = {}
                connection['address'] = addr
                newsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                newsock.settimeout(self.timeout)
                connection['socket'] = newsock
                connection['lock'] = self.port_lock
                connection['Serversocket'] = self.sock
                connection['time'] = time.time()
                newconn = True
                log('new connection:%s' % str(addr))
            self.table_lock.release()
            try:
                connection['socket'].sendto(data, (self.newhost, self.newport))
            except Exception as ex:
                log("sendto error:" + str(ex))
                break
            if newconn:
                self.connetcTable[addr] = connection
                t1 = pipethreadUDP(connection, self.connetcTable, self.table_lock)
                t1.start()
        log('main thread exit')
        for key in self.connetcTable.keys():
            self.connetcTable[key]['socket'].close()


if __name__ == '__main__':
    # myp = portmapUDP(2311, '192.168.Test.200', 2311, local_ip='172.24.177.87')
    # myp.start()

    myp = portmap(('192.168.200.Test', 443), ('211.87.178.171', 443))
    myp.start()
    # myp = portmap(('192.168.200.Test', 80), ('211.87.178.171', 80))
    # myp.start()
    # myp.__stop()
