#  coding: utf-8 
import SocketServer, mimetypes, os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos, Tiegan Bonowicz
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(SocketServer.BaseRequestHandler):

    # Function made so user can't access anything outside of ./www
    # Just counts the depth based on the amount of "/" and "../" in the path
    def preventLeavingwww(self, path):
        depth = 0
        for idx in range(1, len(path)):
            if(path[idx] == "/"):
                depth += 1
            elif(path[idx:idx+3] == "../"):
                depth -= 1
                if(depth < 0):
                    return False
        return True
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)

        # Splits the gotten data into a list.
        splitData = self.data.split()
        
        # There's some weird empty requests from Firefox sometimes, this is just meant as a way to
        # not get an error (which doesn't affect the server, mind you)
        if(len(splitData) == 0):
            self.request.sendall("HTTP/1.1 404 Not Found\r\n\r\n")

        # Any non-GET methods are rejected and are sent back a 405
        elif(splitData[0] != "GET"):
            self.request.sendall("HTTP/1.1 405 Method Not Allowed\r\n\r\n")

        else:
            # Making sure user isn't trying to access anything outside of ./www
            if(not self.preventLeavingwww(splitData[1])):
                self.request.sendall("HTTP/1.1 404 Not Found\r\n\r\n")
            else:
                path = "./www" + splitData[1]

                # Need to add index.html at the end of the path if it ends in "/"
                if(splitData[1][-1] == "/"):
                    path += "index.html"

                # Using os.path.exists to check if the given path exists. If it does, continue,
                # else return a 404.
                if(os.path.exists(path)):
                    # Get the MIME type of the given path.
                    type = mimetypes.guess_type(path)[0]

                    # If the MIME type is HTML or CSS, we open it and send the content to the
                    # client
                    if(type == "text/html" or type == "text/css"):
                        self.request.sendall("HTTP/1.1 200 OK\r\nContent-Type: %s\r\n\r\n" % type)
                        requestedFile = open(path, "r")
                        self.request.sendall(requestedFile.read())
                        requestedFile.close()

                    # If the MIME type is None, we see if adding "/index.html" to the path leads
                    # leads to a valid file. If it does we give a 302 Found, else return a 404.
                    elif(type == None):
                        path += "/index.html"
                        if(os.path.exists(path)):
                            self.request.sendall("HTTP/1.1 302 Found\r\n")
                            self.request.sendall("Location: http://127.0.0.1:8080%s\r\n\r\n"
                                                 %(splitData[1] + "/"))
                        else:
                            self.request.sendall("HTTP/1.1 404 Not Found\r\n\r\n")

                    # Not supposed to have any other MIME types, throw a 404.
                    else:
                        self.request.sendall("HTTP/1.1 404 Not Found\r\n\r\n")

                else:
                    self.request.sendall("HTTP/1.1 404 Not Found\r\n\r\n")

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    SocketServer.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = SocketServer.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
