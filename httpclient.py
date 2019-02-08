#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def parse_url(self,url):
        url_info = urllib.parse.urlparse(url)
        self.hostname = url_info.hostname
        self.port = url_info.port if url_info.port else 80
        self.path = url_info.path if url_info.path else '/'

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return int(data.split("\r\n")[0].split()[1])

    def get_headers(self,data):
        header_str = data.split("\r\n\r\n")[0].split("\r\n")[1:]
        headers = dict()
        for header in header_str:
            split_head = header.split(":")
            key = split_head[0]
            value = ":".join(split_head[1:]).lstrip()
            headers[key] = value.lstrip()
        return headers

    def get_body(self, data):
        return data.split("\r\n\r\n")[1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buf = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buf.extend(part)
            else:
                done = not part
        return buf.decode('utf-8')

    def GET(self, url, args=None):
        self.parse_url(url)
        
        req =   "GET {path} HTTP/1.1\r\n".format(path=self.path) + \
                "Host: {host}:{port}\r\n".format(host=self.hostname, port=self.port) + \
                "Accept: */*\r\n" + \
                "Connection: close\r\n\r\n"

        self.connect(self.hostname, self.port)
        self.sendall(req)
        response = self.recvall(self.socket)
        self.close()

        code = self.get_code(response)
        body = self.get_body(response)

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        self.parse_url(url)

        req =   "POST {path} HTTP/1.1\r\n".format(path=self.path) + \
                "Host: {host}:{port}\r\n".format(host=self.hostname, port=self.port) + \
                "Accept: */*\r\n" + \
                "Connection: close\r\n"

        if args:
            content = urllib.parse.urlencode(args)
            content_length = str(len(content))
            req += "Content-Type: application/x-www-form-urlencoded\r\n"
            req += "Content-Length: {content_length}\r\n\r\n".format(content_length = content_length)
            req += content
        else:
            req += "Content-Length: {content_length}\r\n\r\n".format(content_length = '0')

        self.connect(self.hostname, self.port)
        self.sendall(req)
        response = self.recvall(self.socket)
        self.close()

        code = self.get_code(response)
        body = self.get_body(response)

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        # printout result to stdout
        print(client.command( sys.argv[2], sys.argv[1]).body)
    else:
        # printout result to stdout
        print(client.command( sys.argv[1] ).body)
