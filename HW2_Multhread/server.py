import socket
import struct
import time
import threading
import json
import sys
import shutil

user = '[{"username":"andy","value":{"password":"123","status":"offline"},"friends":["mars"],"message":"empty"},' \
       '{"username":"mars","value":{"password":"123","status":"offline"},"friends":["andy"],"message":"empty"},' \
       '{"username":"shuai","value":{"password":"123","status":"offline"},"friends":["andy"],"message":"empty"},'\
        '{"username":"wang","value":{"password":"123","status":"offline"},"friends":["mars"],"message":"empty"}]'
json_user = json.loads(user)
thread = []
name = []
sendfile_from = ""
offline = ""
file = ""
sendfile_to = ""
class ClientHandler(threading.Thread):
    def __init__(self, client):
        threading.Thread.__init__(self)
        self.client_sock, self.client_addr = client
        thread.append(self.client_sock)
        name.append("")
        self.index_in_thread = len(thread) - 1;
    def run(self):
        global sendfile_from
        global file
        global sendfile_to
        thread_username = ""
        print >> sys.stderr, 'connection from', self.client_addr
        while True:
            data = self.client_sock.recv(1600)
            if True:
                if data:
                    print >> sys.stderr, 'sending data back to the client'
                    json_data = json.loads(data)

                    print json_data

                    if json_data["command"] == "login":
                        length = len(json_user)
                        i = 0
                        while i < length:
                            if json_data["value"]["username"] == json_user[i]["username"] and json_data["value"][
                                "password"] == json_user[i]["value"]["password"]:
                                self.client_sock.sendall('{"code":"100","message":"Login success"}')
                                json_user[i]["value"]["status"] = "online"
                                self.thread_username = json_user[i]["username"]
                                name[self.index_in_thread] = self.thread_username

                            elif json_data["value"]["username"] == json_user[i]["username"] and json_data["value"][
                                "password"] != json_user[i]["value"]["password"]:
                                self.client_sock.sendall('{"code":"99","message":"Wrong password"}')
                            i += 1

                        q = 0
                        while q < len(json_user):
                            if json_user[q]["message"] != "empty":
                                w = 0
                                while w < len(thread):
                                    if json_user[q]["username"] == name[w]:
                                        thread[w].sendall(json_user[q]["message"])
                                        json_user[q]["message"] = "empty"
                                    w += 1
                            q += 1




                    elif json_data["command"] == "friend list":
                        print >> sys.stderr, 'friend list'
                        friends = ""
                        length = len(json_user)
                        i = 0
                        while i < length:
                            if json_user[i]["username"] == json_data["username"]:
                                j = 0
                                while j < len(json_user[i]["friends"]):
                                    friendname = json_user[i]["friends"][j]
                                    w=0
                                    while w < len(json_user):
                                        if friendname == json_user[w]["username"]:
                                            friends += friendname +' '+ json_user[w]["value"]["status"] +'   '
                                        w += 1
                                    j +=1
                            i +=1
                        if friends != "":
                            self.client_sock.sendall('{"command":"friend list","message":"' + friends + '"}')
                        else:
                            self.client_sock.sendall('{"command":"friend list","message":"Friend list is empty!"}')

                    elif json_data["command"] == "friend add":
                        print >> sys.stderr, 'friend add'
                        add = json_data["add"]
                        i = 0
                        while i < len(json_user):
                            if json_user[i]["username"] == json_data["username"]:
                                json_user[i]["friends"].append(add)
                            i+=1
                        self.client_sock.sendall('{"command":"friend add","message":"'+ add +' added into the friend list"}')

                    elif json_data["command"] == "friend rm":
                        print >> sys.stderr, 'friend rm'
                        rm = json_data["rm"]
                        i = 0
                        while i < len(json_user):
                            if json_user[i]["username"] == json_data["username"]:
                                json_user[i]["friends"].remove(rm)
                            i += 1
                        self.client_sock.sendall('{"command":"friend rm","message":"' + rm + ' removed from the friend list"}')


                    elif json_data["command"] == "send":
                        who = json_data["who"]
                        username = json_data["username"]
                        message = json_data["message"]
                        i = 0
                        while i < len(json_user):
                            if who == json_user[i]["username"]:
                                if json_user[i]["value"]["status"] == "online":
                                    w = 0
                                    while w < len(thread):
                                        if who == name[w]:
                                            thread[w].sendall('{"command":"send","message":" ' + username + ':' +  message + ' "}')
                                            print >> sys.stderr, 'send message to ' + who
                                        w += 1
                                else:
                                    j = 0
                                    while j < len(json_user):
                                        if who == json_user[j]["username"]:
                                            json_user[j]["message"] = '{"command":"send","message":" Message from ' + username + ':' +  message + ' ","who":"'+ who +'"}'
                                        j += 1
                            i += 1

                    elif json_data["command"] == "sendfile":
                        who = json_data["who"]
                        filename = json_data["filename"]
                        username = json_data["username"]
                        print who
                        sendfile_to = who
                        sendfile_from = username
                        i = 0
                        while i < len(json_user):
                            if who == json_user[i]["username"]:
                                if json_user[i]["value"]["status"] == "online":
                                    w = 0
                                    while w < len(thread):
                                        if who == name[w]:
                                            thread[w].sendall(
                                                '{"command":"sandfile","message":"Do you want accept ' + filename + ' from ' + username + '?(yes/no)"}')
                                            print >> sys.stderr, 'send file ' + who
                                            file = filename
                                        w += 1
                            i += 1
                    elif json_data["command"] == "no":
                        if sendfile_from == "":
                            print >> sys.stderr, "no"
                        else:
                            username = json_data["username"]
                            w = 0
                            while w < len(thread):
                                if sendfile_from == name[w]:
                                    thread[w].sendall('{"command":"no","message":" denied from ' + username + '"}')
                                    print >> sys.stderr, 'send message to ' + user
                                    sendfile_from = ""
                                w += 1

                    elif json_data["command"] == "yes":
                        if sendfile_from == "":
                            print >> sys.stderr, "yes"
                        else:
                            w = 0
                            while w < len(thread):
                                if sendfile_from == name[w]:
                                    shutil.copy(file,sendfile_to)
                                    print sendfile_to
                                    print file
                                    thread[w].sendall('{"command":"yes","message":"100% of '+ file +' transmitted...."}')
                                    thread[w].sendall('{"command":"yes","message":"end of file transmission"}')
                                    print >> sys.stderr, 'send message to ' + user
                                    sendfile_from = ""
                                    file = ""
                                    sendfile_to = ""
                                w += 1


                    elif json_data["command"] == "quit":
                        length = len(json_user)
                        i = 0
                        while i < length:
                            if json_data["username"] == json_data["username"]:
                                json_user[i]["value"]["status"] = "offline"
                            i += 1


                    else:
                        self.client_sock.sendall('{"code":"0","error":"not implemented"}')


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
sock.bind(('', 8888))
sock.listen(5)
print "Waiting for clients ..."

while True:  # Serve forever
    client = sock.accept()
    ClientHandler(client).start()