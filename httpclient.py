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
from typing import Dict
import ssl

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # obtained info about SSL and encryption via chat GPT-3.5
        if port == 443:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.verify_mode = ssl.CERT_REQUIRED
            context.load_default_certs()
            self.socket = context.wrap_socket(self.socket, server_hostname=host)
        
        self.socket.connect((host, port))
        return None



    def get_headers(self,data):
        
        headers = {}
        data = data.split('\r\n')
        for line in data:
            key_value = line.split(":", 1)
            if (len(key_value) == 2):
                headers[key_value[0]] = key_value[1].strip()
        # print(headers)
        # print(data)
        return headers

    
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
            if parsed_url.scheme == "http":
                port = 80
            elif parsed_url.scheme == "https":
                port = 443
        else:
            host = host_info[0]
            port = int(host_info[1])
        return host, port, parsed_url

    def GET(self, url, args=None):
        # # ex: google.com
        # # scheme='https', netloc='www.google.com', path='/', params='', query='', fragment=''
        host, port, parsed_url = self.parse_url(url)        
        self.connect(host, port)
        connection_type = "close"
        request = f"GET {parsed_url.path} HTTP/1.1\r\nHost: {host}\r\nConnection: {connection_type}\r\n\r\n"
        
        self.sendall(request)
        response = self.recvall(self.socket)
        
        code = int(self.get_code(response))
        body = self.get_body(response)
        
        print(f"Response code: {code}")
        print(f"Response body: {body}")
        # headers = self.get_headers(response)
        self.close()
        
        if 300 <= code < 400:
            print(code)
            print("redirecting")
            headers = self.get_headers(response)
            new_url = headers["Location"]
            return self.GET(new_url)

        return HTTPResponse(code, body)

    def POST(self, url, args:Dict = None):
        host, port, parsed_url = self.parse_url(url)
        self.connect(host, port)
        connection_type = "close"
        request = f"POST {parsed_url.path} HTTP/1.1\r\nHost: {host}\r\nConnection: {connection_type}\r\n"
        if args:
            request_body = '&'.join([f'{key}={value}' for key, value in args.items()])
            request += "Content-Type: application/x-www-form-urlencoded\r\n"
            request += f"Content-Length: {len(request_body.encode('utf-8'))}\r\n"
            request += "\r\n"
            request += request_body
            
        else:
            request += "Content-Length: 0\r\n"
            request += "\r\n"
        self.sendall(request)
        response = self.recvall(self.socket)
          
        code = int(self.get_code(response))
        body = self.get_body(response)
        
        print(f"Response code: {code}")
        print(f"Response body: {body}")
        self.close()
        
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
