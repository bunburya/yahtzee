#!/usr/bin/env python
# -*- coding: utf-8 -*-

from socket import socket, AF_INET, SOCK_STREAM

class Connection:
    
    def __init__(self, host, port, callback, listener=False):
        self.host = host
        self.port = port
        self.socket = socket(AF_INET, SOCK_STREAM)
        if listener:
            # after a while this class will never have to listen;
            # listening will be done at server level and will probably
            # use Twisted or similar
            self.listen()
        else:
            self.connect()
        self.mainloop()
    
    def listen(self):
        self.socket.bind((self.host, self.port))
        self.socket.listen(1)
        self.conn, self.addr = self.socket.accept()
    
    def connect(self):
        self.socket.connect((host, port))
        self.conn = self.socket
    
    def send(self, data):
        self.conn.send('{}\r\n'.format(data.encode()))
    
    def receive(self):
        buf = []
        while buf[-2:] != [b'\r', b'\n']:
            c = self.conn.recv(1)
            if not c:
                self.handle_connection_closed()
            buf.append(c)
        line = b''.join(buf[:-2]).decode()
        print('received:', line)
        return line

    def handle_connection_closed(self):
        print('connection closed.')
