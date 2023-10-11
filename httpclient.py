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
# import urllib.parse import url
from urllib.parse import urlparse

import re

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return None

    def get_headers(self,data):
        return None

    def get_body(self, data):
        return None
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()


    def get_body(self, data):
        return data.split("\r\n\r\n")[1]
    
    def get_code(self, data):
        # HTTP/1.1 200 OK
        data = data.split("\r\n\r\n")[0]
        data = data.split("\r\n")[0]
        data = data.split(" ")
        return data[1]
        

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8', errors='ignore')
    
    def parse_url(self, url):
        parsed_url = urlparse(url=url) 
        
        if parsed_url.scheme not in ["http","https"]:
            raise ValueError("Url scheme not provided")
        if parsed_url.path == "":
            parsed_url = parsed_url._replace(path="/")
            
        host_info = parsed_url.netloc.split(":")
        if len(host_info) == 1:
            host = host_info[0]
            port = 80
        else:
            host = host_info[0]
            port = int(host_info[1])
        return host, port, parsed_url

    def GET(self, url, args=None):
        # parsed_url = urlparse(url=url) # dict object?
        # # ex: google.com
        # # scheme='https', netloc='www.google.com', path='/', params='', query='', fragment=''
        
        # if parsed_url.scheme not in ["http","https"]:
        #     raise ValueError("Url scheme not provided")
        # if parsed_url.path == "":
        #     parsed_url = parsed_url._replace(path="/")
            
        # host_info = parsed_url.netloc.split(":")
        # if len(host_info) == 1:
        #     host = host_info[0]
        #     port = 80
        # else:
        #     host = host_info[0]
        #     port = int(host_info[1])
        host, port, parsed_url = self.parse_url(url)
        
        print(f"host: {host}, port: {port}")
        self.connect(host, port)
        connection_type = "close"
        # request = "GET " + parsed_url.path + " HTTP/1.1\r\nHost: " + parsed_url.hostname + "\r\nConnection: close\r\n\r\n"
        request = f"GET {parsed_url.path} HTTP/1.1\r\nHost: {host}\r\nConnection: {connection_type}\r\n\r\n"
        
        
        self.sendall(request)
        # print(request.encode('utf-8'))
        response = self.recvall(self.socket)
        
        code = int(self.get_code(response))
        body = self.get_body(response)
        # code = 500
        # body = ""
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        host, port, parsed_url = self.parse_url(url)
        
        
        
        code = 500
        body = ""
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
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
# 
# BASEHOST = '127.0.0.1'
# BASEPORT = 27600 + random.randint(1,100)
# req = http.GET("http://%s:%d/49872398432" % (BASEHOST,BASEPORT) )
