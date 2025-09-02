import socket
import threading
import select
import sys
import time
import getopt

# Configuration
LISTENING_ADDR = '127.0.0.1'
LISTENING_PORT = 700
PASS = ''
BUFLEN = 4096 * 4
TIMEOUT = 60
DEFAULT_HOST = '127.0.0.1:111'
RESPONSE = 'HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Accept: foo\r\n\r\n'

SOCKS_VERSION = 5

class Server(threading.Thread):
    def __init__(self, host, port):
        super().__init__()
        self.running = False
        self.host = host
        self.port = port
        self.threads = []
        self.threadsLock = threading.Lock()
        self.logLock = threading.Lock()

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
            soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            soc.settimeout(2)
            soc.bind((self.host, int(self.port)))
            soc.listen(5)
            self.running = True

            while self.running:
                try:
                    client_socket, addr = soc.accept()
                    client_socket.setblocking(1)
                    conn = ConnectionHandler(client_socket, self, addr)
                    conn.start()
                    self.addConn(conn)
                except socket.timeout:
                    continue
                except Exception as e:
                    self.printLog(f"Server error: {e}")

    def printLog(self, log):
        with self.logLock:
            print(log)

    def addConn(self, conn):
        with self.threadsLock:
            if self.running:
                self.threads.append(conn)

    def removeConn(self, conn):
        with self.threadsLock:
            self.threads.remove(conn)

    def close(self):
        self.running = False
        with self.threadsLock:
            for conn in list(self.threads):
                conn.close()

class ConnectionHandler(threading.Thread):
    def __init__(self, socClient, server, addr):
        super().__init__()
        self.clientClosed = False
        self.targetClosed = True
        self.client = socClient
        self.client_buffer = b''
        self.server = server
        self.log = f'Connection: {addr}'

    def close(self):
        if not self.clientClosed:
            try:
                self.client.shutdown(socket.SHUT_RDWR)
                self.client.close()
            except Exception as e:
                self.server.printLog(f"Error closing client: {e}")
            finally:
                self.clientClosed = True

        if not self.targetClosed:
            try:
                self.target.shutdown(socket.SHUT_RDWR)
                self.target.close()
            except Exception as e:
                self.server.printLog(f"Error closing target: {e}")
            finally:
                self.targetClosed = True

    def run(self):
        try:
            self.client_buffer = self.client.recv(BUFLEN)
            
            if self.client_buffer[0] == SOCKS_VERSION:
                self.handle_socks5()
            else:
                self.handle_http()
        except Exception as e:
            self.log += f' - error: {e}'
            self.server.printLog(self.log)
        finally:
            self.close()
            self.server.removeConn(self)

    def handle_http(self):
        self.client_buffer = self.client_buffer.decode('utf-8')
        hostPort = self.findHeader(self.client_buffer, 'X-Real-Host')

        if not hostPort:
            hostPort = DEFAULT_HOST

        split = self.findHeader(self.client_buffer, 'X-Split')

        if split:
            self.client.recv(BUFLEN)

        passwd = self.findHeader(self.client_buffer, 'X-Pass')

        if len(PASS) != 0 and passwd != PASS:
            self.client.sendall(b'HTTP/1.1 400 WrongPass!\r\n\r\n')
        elif len(PASS) != 0 or hostPort.startswith('127.0.0.1') or hostPort.startswith('localhost'):
            self.method_CONNECT(hostPort)
        else:
            self.client.sendall(b'HTTP/1.1 403 Forbidden!\r\n\r\n')

    def handle_socks5(self):
        # SOCKS5 handshake
        self.client.sendall(b"\x05\x00")  # Version 5, No Authentication Required

        # Request details
        version, cmd, _, address_type = self.client.recv(4)
        if cmd != 1:  # Only CONNECT command is supported
            self.close()
            return

        # Parse address and port based on address type
        if address_type == 1:  # IPv4
            address = socket.inet_ntoa(self.client.recv(4))
        elif address_type == 3:  # Domain name
            domain_length = self.client.recv(1)[0]
            address = self.client.recv(domain_length).decode('utf-8')
        else:
            self.close()
            return
        port = int.from_bytes(self.client.recv(2), 'big')

        self.log += f' - SOCKS5 CONNECT {address}:{port}'
        self.connect_target(f"{address}:{port}")
        self.client.sendall(b"\x05\x00\x00\x01\x00\x00\x00\x00\x00\x00")  # SOCKS5 response
        self.client_buffer = b''
        self.server.printLog(self.log)
        self.doCONNECT()

    def findHeader(self, headers, header_name):
        headers = headers.split('\r\n')
        for header in headers:
            if header.startswith(header_name + ': '):
                return header[len(header_name) + 2:]
        return ''

    def connect_target(self, host):
        try:
            host, port = (host.split(':') + [443])[:2]
            port = int(port)
            addr_info = socket.getaddrinfo(host, port)[0]
            self.target = socket.socket(addr_info[0], addr_info[1], addr_info[2])
            self.target.connect(addr_info[4])
            self.targetClosed = False
        except Exception as e:
            self.server.printLog(f"Error connecting to target {host}:{port} - {e}")
            self.client.sendall(b'HTTP/1.1 502 Bad Gateway\r\n\r\n')
            self.close()

    def method_CONNECT(self, path):
        self.log += f' - CONNECT {path}'
        self.connect_target(path)
        self.client.sendall(RESPONSE.encode('utf-8'))
        self.client_buffer = b''
        self.server.printLog(self.log)
        self.doCONNECT()

    def doCONNECT(self):
        socs = [self.client, self.target]
        count = 0
        while True:
            count += 1
            recv, _, err = select.select(socs, [], socs, 3)
            if err:
                break
            if recv:
                for s in recv:
                    try:
                        data = s.recv(BUFLEN)
                        if not data:
                            break
                        if s is self.target:
                            self.client.send(data)
                        else:
                            while data:
                                sent = self.target.send(data)
                                data = data[sent:]
                        count = 0
                    except Exception as e:
                        self.server.printLog(f"Data transfer error: {e}")
                        break
            if count >= TIMEOUT:
                break

def print_usage():
    print('Usage: proxy.py -p <port>')
    print('       proxy.py -b <bindAddr> -p <port>')
    print('       proxy.py -b 0.0.0.0 -p 80')

def parse_args(argv):
    global LISTENING_ADDR, LISTENING_PORT
    try:
        opts, _ = getopt.getopt(argv, "hb:p:", ["bind=", "port="])
    except getopt.GetoptError:
        print_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print_usage()
            sys.exit()
        elif opt in ("-b", "--bind"):
            LISTENING_ADDR = arg
        elif opt in ("-p", "--port"):
            LISTENING_PORT = int(arg)

def main():
    print("\n:-------PythonProxy-------:\n")
    print(f"Listening addr: {LISTENING_ADDR}")
    print(f"Listening port: {LISTENING_PORT}\n")
    print(":-------------------------:\n")
    server = Server(LISTENING_ADDR, LISTENING_PORT)
    server.start()
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        print('Stopping...')
        server.close()

if __name__ == '__main__':
    parse_args(sys.argv[1:])
    main()            while self.running:
                try:
                    client_socket, addr = soc.accept()
                    client_socket.setblocking(1)
                    conn = ConnectionHandler(client_socket, self, addr)
                    conn.start()
                    self.addConn(conn)
                except socket.timeout:
                    continue
                except Exception as e:
                    self.printLog(f"Server error: {e}")

    def printLog(self, log):
        with self.logLock:
            print(log)

    def addConn(self, conn):
        with self.threadsLock:
            if self.running:
                self.threads.append(conn)

    def removeConn(self, conn):
        with self.threadsLock:
            self.threads.remove(conn)

    def close(self):
        self.running = False
        with self.threadsLock:
            for conn in list(self.threads):
                conn.close()

class ConnectionHandler(threading.Thread):
    def __init__(self, socClient, server, addr):
        super().__init__()
        self.clientClosed = False
        self.targetClosed = True
        self.client = socClient
        self.client_buffer = b''
        self.server = server
        self.log = f'Connection: {addr}'

    def close(self):
        if not self.clientClosed:
            try:
                self.client.shutdown(socket.SHUT_RDWR)
                self.client.close()
            except Exception as e:
                self.server.printLog(f"Error closing client: {e}")
            finally:
                self.clientClosed = True

        if not self.targetClosed:
            try:
                self.target.shutdown(socket.SHUT_RDWR)
                self.target.close()
            except Exception as e:
                self.server.printLog(f"Error closing target: {e}")
            finally:
                self.targetClosed = True

    def run(self):
        try:
            self.client_buffer = self.client.recv(BUFLEN)
            
            if self.client_buffer[0] == SOCKS_VERSION:
                self.handle_socks5()
            else:
                self.handle_http()
        except Exception as e:
            self.log += f' - error: {e}'
            self.server.printLog(self.log)
        finally:
            self.close()
            self.server.removeConn(self)

    def handle_http(self):
        self.client_buffer = self.client_buffer.decode('utf-8')
        hostPort = self.findHeader(self.client_buffer, 'X-Real-Host')

        if not hostPort:
            hostPort = DEFAULT_HOST

        split = self.findHeader(self.client_buffer, 'X-Split')

        if split:
            self.client.recv(BUFLEN)

        passwd = self.findHeader(self.client_buffer, 'X-Pass')

        if len(PASS) != 0 and passwd != PASS:
            self.client.sendall(b'HTTP/1.1 400 WrongPass!\r\n\r\n')
        elif len(PASS) != 0 or hostPort.startswith('127.0.0.1') or hostPort.startswith('localhost'):
            self.method_CONNECT(hostPort)
        else:
            self.client.sendall(b'HTTP/1.1 403 Forbidden!\r\n\r\n')

    def handle_socks5(self):
        # SOCKS5 handshake
        self.client.sendall(b"\x05\x00")  # Version 5, No Authentication Required

        # Request details
        version, cmd, _, address_type = self.client.recv(4)
        if cmd != 1:  # Only CONNECT command is supported
            self.close()
            return

        # Parse address and port based on address type
        if address_type == 1:  # IPv4
            address = socket.inet_ntoa(self.client.recv(4))
        elif address_type == 3:  # Domain name
            domain_length = self.client.recv(1)[0]
            address = self.client.recv(domain_length).decode('utf-8')
        else:
            self.close()
            return
        port = int.from_bytes(self.client.recv(2), 'big')

        self.log += f' - SOCKS5 CONNECT {address}:{port}'
        self.connect_target(f"{address}:{port}")
        self.client.sendall(b"\x05\x00\x00\x01\x00\x00\x00\x00\x00\x00")  # SOCKS5 response
        self.client_buffer = b''
        self.server.printLog(self.log)
        self.doCONNECT()

    def findHeader(self, headers, header_name):
        headers = headers.split('\r\n')
        for header in headers:
            if header.startswith(header_name + ': '):
                return header[len(header_name) + 2:]
        return ''

    def connect_target(self, host):
        try:
            host, port = (host.split(':') + [443])[:2]
            port = int(port)
            addr_info = socket.getaddrinfo(host, port)[0]
            self.target = socket.socket(addr_info[0], addr_info[1], addr_info[2])
            self.target.connect(addr_info[4])
            self.targetClosed = False
        except Exception as e:
            self.server.printLog(f"Error connecting to target {host}:{port} - {e}")
            self.client.sendall(b'HTTP/1.1 502 Bad Gateway\r\n\r\n')
            self.close()

    def method_CONNECT(self, path):
        self.log += f' - CONNECT {path}'
        self.connect_target(path)
        self.client.sendall(RESPONSE.encode('utf-8'))
        self.client_buffer = b''
        self.server.printLog(self.log)
        self.doCONNECT()

    def doCONNECT(self):
        socs = [self.client, self.target]
        count = 0
        while True:
            count += 1
            recv, _, err = select.select(socs, [], socs, 3)
            if err:
                break
            if recv:
                for s in recv:
                    try:
                        data = s.recv(BUFLEN)
                        if not data:
                            break
                        if s is self.target:
                            self.client.send(data)
                        else:
                            while data:
                                sent = self.target.send(data)
                                data = data[sent:]
                        count = 0
                    except Exception as e:
                        self.server.printLog(f"Data transfer error: {e}")
                        break
            if count >= TIMEOUT:
                break

def print_usage():
    print('Usage: proxy.py -p <port>')
    print('       proxy.py -b <bindAddr> -p <port>')
    print('       proxy.py -b 0.0.0.0 -p 80')

def parse_args(argv):
    global LISTENING_ADDR, LISTENING_PORT
    try:
        opts, _ = getopt.getopt(argv, "hb:p:", ["bind=", "port="])
    except getopt.GetoptError:
        print_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print_usage()
            sys.exit()
        elif opt in ("-b", "--bind"):
            LISTENING_ADDR = arg
        elif opt in ("-p", "--port"):
            LISTENING_PORT = int(arg)

def main():
    print("\n:-------PythonProxy-------:\n")
    print(f"Listening addr: {LISTENING_ADDR}")
    print(f"Listening port: {LISTENING_PORT}\n")
    print(":-------------------------:\n")
    server = Server(LISTENING_ADDR, LISTENING_PORT)
    server.start()
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        print('Stopping...')
        server.close()

if __name__ == '__main__':
    parse_args(sys.argv[1:])
    main()            while self.running:
                try:
                    client_socket, addr = soc.accept()
                    client_socket.setblocking(1)
                    conn = ConnectionHandler(client_socket, self, addr)
                    conn.start()
                    self.addConn(conn)
                except socket.timeout:
                    continue
                except Exception as e:
                    self.printLog(f"Server error: {e}")

    def printLog(self, log):
        with self.logLock:
            print(log)

    def addConn(self, conn):
        with self.threadsLock:
            if self.running:
                self.threads.append(conn)

    def removeConn(self, conn):
        with self.threadsLock:
            self.threads.remove(conn)

    def close(self):
        self.running = False
        with self.threadsLock:
            for conn in list(self.threads):
                conn.close()

class ConnectionHandler(threading.Thread):
    def __init__(self, socClient, server, addr):
        super().__init__()
        self.clientClosed = False
        self.targetClosed = True
        self.client = socClient
        self.client_buffer = b''
        self.server = server
        self.log = f'Connection: {addr}'
        self.udp_assoc_socket = None
        self.udp_client_addr = None

    def close(self):
        if not self.clientClosed:
            try:
                self.client.shutdown(socket.SHUT_RDWR)
                self.client.close()
            except Exception as e:
                self.server.printLog(f"Error closing client: {e}")
            finally:
                self.clientClosed = True

        if not self.targetClosed:
            try:
                if self.target:
                    self.target.shutdown(socket.SHUT_RDWR)
                    self.target.close()
            except Exception as e:
                self.server.printLog(f"Error closing target: {e}")
            finally:
                self.targetClosed = True
                
        if self.udp_assoc_socket:
            try:
                self.udp_assoc_socket.close()
            except Exception as e:
                self.server.printLog(f"Error closing UDP socket: {e}")
            finally:
                self.udp_assoc_socket = None

    def run(self):
        try:
            self.client_buffer = self.client.recv(BUFLEN)
            
            if self.client_buffer[0] == SOCKS_VERSION:
                self.handle_socks5()
            else:
                self.handle_http()
        except Exception as e:
            self.log += f' - error: {e}'
            self.server.printLog(self.log)
        finally:
            self.close()
            self.server.removeConn(self)

    def handle_http(self):
        self.client_buffer = self.client_buffer.decode('utf-8')
        hostPort = self.findHeader(self.client_buffer, 'X-Real-Host')

        if not hostPort:
            hostPort = DEFAULT_HOST

        split = self.findHeader(self.client_buffer, 'X-Split')

        if split:
            self.client.recv(BUFLEN)

        passwd = self.findHeader(self.client_buffer, 'X-Pass')

        if len(PASS) != 0 and passwd != PASS:
            self.client.sendall(b'HTTP/1.1 400 WrongPass!\r\n\r\n')
        elif len(PASS) != 0 or hostPort.startswith('127.0.0.1') or hostPort.startswith('localhost'):
            self.method_CONNECT(hostPort)
        else:
            self.client.sendall(b'HTTP/1.1 403 Forbidden!\r\n\r\n')

    def handle_socks5(self):
        # SOCKS5 handshake
        self.client.sendall(b"\x05\x00")  # Version 5, No Authentication Required

        # Request details
        request = self.client.recv(BUFLEN)
        if len(request) < 4:
            self.close()
            return
            
        version, cmd, _, address_type = request[:4]
        
        if cmd == 1:  # CONNECT command
            self.handle_socks5_connect(request, address_type)
        elif cmd == 3:  # UDP ASSOCIATE command
            self.handle_socks5_udp_associate()
        else:
            self.client.sendall(b"\x05\x07\x00\x01")  # Command not supported
            self.close()

    def handle_socks5_connect(self, request, address_type):
        # Parse address and port based on address type
        offset = 4
        if address_type == 1:  # IPv4
            if len(request) < offset + 4 + 2:
                self.close()
                return
            address = socket.inet_ntoa(request[offset:offset+4])
            offset += 4
        elif address_type == 3:  # Domain name
            domain_length = request[offset]
            offset += 1
            if len(request) < offset + domain_length + 2:
                self.close()
                return
            address = request[offset:offset+domain_length].decode('utf-8')
            offset += domain_length
        else:
            self.client.sendall(b"\x05\x08\x00\x01")  # Address type not supported
            self.close()
            return
            
        port = int.from_bytes(request[offset:offset+2], 'big')
        self.log += f' - SOCKS5 CONNECT {address}:{port}'
        self.connect_target(f"{address}:{port}")
        
        # Send success response
        reply = b"\x05\x00\x00\x01"
        reply += socket.inet_aton('0.0.0.0')  # Bind address (ignored)
        reply += (0).to_bytes(2, 'big')  # Bind port (ignored)
        self.client.sendall(reply)
        
        self.client_buffer = b''
        self.server.printLog(self.log)
        self.doCONNECT()

    def handle_socks5_udp_associate(self):
        # Create a UDP socket for association
        self.udp_assoc_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_assoc_socket.bind(('0.0.0.0', 0))  # Bind to any available port
        
        # Get the bound address and port
        udp_addr, udp_port = self.udp_assoc_socket.getsockname()
        
        # Send success response with the UDP port we're listening on
        reply = b"\x05\x00\x00\x01"
        reply += socket.inet_aton('0.0.0.0')  # Bind address
        reply += udp_port.to_bytes(2, 'big')  # Bind port
        self.client.sendall(reply)
        
        self.log += f' - SOCKS5 UDP ASSOCIATE on port {udp_port}'
        self.server.printLog(self.log)
        
        # Handle UDP association
        self.handle_udp_association()

    def handle_udp_association(self):
        self.udp_assoc_socket.settimeout(2)
        while not self.clientClosed:
            try:
                # Check if client is still connected
                try:
                    # Use select to check if client socket has data (closed connection)
                    read_sockets, _, _ = select.select([self.client], [], [], 1)
                    if self.client in read_sockets:
                        # Client sent data (which shouldn't happen for UDP associate)
                        data = self.client.recv(BUFLEN)
                        if not data:
                            break
                except (socket.error, OSError):
                    break
                
                # Check for UDP data
                try:
                    data, addr = self.udp_assoc_socket.recvfrom(BUFLEN)
                    if not data:
                        continue
                        
                    # Parse SOCKS5 UDP request header (first 10 bytes)
                    if len(data) < 10:
                        continue
                        
                    # Check RSV and FRAG fields (should be 0)
                    if data[2] != 0 or data[3] != 0:
                        continue
                        
                    # Parse address type
                    atype = data[3]
                    offset = 4
                    
                    if atype == 1:  # IPv4
                        if len(data) < offset + 4:
                            continue
                        dest_addr = socket.inet_ntoa(data[offset:offset+4])
                        offset += 4
                    elif atype == 3:  # Domain name
                        domain_len = data[offset]
                        offset += 1
                        if len(data) < offset + domain_len:
                            continue
                        dest_addr = data[offset:offset+domain_len].decode('utf-8')
                        offset += domain_len
                    else:
                        continue
                        
                    # Parse port
                    if len(data) < offset + 2:
                        continue
                    dest_port = int.from_bytes(data[offset:offset+2], 'big')
                    offset += 2
                    
                    # The actual data starts at offset
                    payload = data[offset:]
                    
                    # Forward to destination
                    try:
                        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
                            udp_socket.sendto(payload, (dest_addr, dest_port))
                            # Wait for response with timeout
                            udp_socket.settimeout(5)
                            response, _ = udp_socket.recvfrom(BUFLEN)
                            
                            # Build SOCKS5 UDP response header
                            reply_header = b"\x00\x00\x00\x01"  # RSV=0, FRAG=0, ATYPE=IPv4
                            reply_header += socket.inet_aton('0.0.0.0')  # DST.ADDR (ignored)
                            reply_header += (0).to_bytes(2, 'big')  # DST.PORT (ignored)
                            
                            # Send response back to client
                            self.udp_assoc_socket.sendto(reply_header + response, addr)
                    except (socket.error, OSError, TimeoutError):
                        # If we can't reach the destination, just continue
                        continue
                        
                except socket.timeout:
                    continue
                    
            except (socket.error, OSError):
                break

    def findHeader(self, headers, header_name):
        headers = headers.split('\r\n')
        for header in headers:
            if header.startswith(header_name + ': '):
                return header[len(header_name) + 2:]
        return ''

    def connect_target(self, host):
        try:
            host, port = (host.split(':') + [443])[:2]
            port = int(port)
            addr_info = socket.getaddrinfo(host, port)[0]
            self.target = socket.socket(addr_info[0], addr_info[1], addr_info[2])
            self.target.connect(addr_info[4])
            self.targetClosed = False
        except Exception as e:
            self.server.printLog(f"Error connecting to target {host}:{port} - {e}")
            self.client.sendall(b'HTTP/1.1 502 Bad Gateway\r\n\r\n')
            self.close()

    def method_CONNECT(self, path):
        self.log += f' - CONNECT {path}'
        self.connect_target(path)
        self.client.sendall(RESPONSE.encode('utf-8'))
        self.client_buffer = b''
        self.server.printLog(self.log)
        self.doCONNECT()

    def doCONNECT(self):
        socs = [self.client, self.target]
        count = 0
        while True:
            count += 1
            recv, _, err = select.select(socs, [], socs, 3)
            if err:
                break
            if recv:
                for s in recv:
                    try:
                        data = s.recv(BUFLEN)
                        if not data:
                            break
                        if s is self.target:
                            self.client.send(data)
                        else:
                            while data:
                                sent = self.target.send(data)
                                data = data[sent:]
                        count = 0
                    except Exception as e:
                        self.server.printLog(f"Data transfer error: {e}")
                        break
            if count >= TIMEOUT:
                break

def print_usage():
    print('Usage: proxy.py -p <port>')
    print('       proxy.py -b <bindAddr> -p <port>')
    print('       proxy.py -b 0.0.0.0 -p 80')

def parse_args(argv):
    global LISTENING_ADDR, LISTENING_PORT
    try:
        opts, _ = getopt.getopt(argv, "hb:p:", ["bind=", "port="])
    except getopt.GetoptError:
        print_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print_usage()
            sys.exit()
        elif opt in ("-b", "--bind"):
            LISTENING_ADDR = arg
        elif opt in ("-p", "--port"):
            LISTENING_PORT = int(arg)

def main():
    print("\n:-------PythonProxy-------:\n")
    print(f"Listening addr: {LISTENING_ADDR}")
    print(f"Listening port: {LISTENING_PORT}\n")
    print(":-------------------------:\n")
    server = Server(LISTENING_ADDR, LISTENING_PORT)
    server.start()
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        print('Stopping...')
        server.close()

if __name__ == '__main__':
    parse_args(sys.argv[1:])
    main()
