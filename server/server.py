import socket
import threading
import os

def read_msg(clients, sock_client, addr_client, username_client):
    while True:
        # terima pesan
        data = sock_client.recv(65535)
        if len(data) == 0:
            break
        
        # parsing pesannya
        dest, msg, cmd = data.decode("utf-8").split("|")
        # cmd = '' + msg 
        file_name = msg
        file_path = find_file(file_name)

        msg = "<{}>: {}".format(username_client, msg)

        if cmd == "bcast":
            # teruskan pesan ke semua client
            send_broadcast(clients, msg, addr_client, cmd, username_client)
        elif cmd == "add":
            if dest in clients:
                if dest in clients[username_client][3]:
                    send_msg(sock_client, "{} sudah menjadi teman".format(dest), cmd)
                else:
                    send_msg(sock_client, "Anda telah berteman dengan {}".format(dest), cmd)
                    clients[username_client][3].add(dest)

                    dest_sock_client = clients[dest][0]
                    send_msg(dest_sock_client, "Anda telah berteman dengan {}".format(username_client), cmd)
                    clients[dest][3].add(username_client)
            else:
                send_msg(sock_client, "{} tidak ditemukan".format(dest), cmd)
        elif cmd == "file":
            if dest in clients[username_client][3]:
                dest_sock_client = clients[dest][0]

                while True:
                    if file_path is None:
                        cmd = ""
                        send_msg(sock_client, "File tidak ditemukan", cmd)
                        break
                    send_msg(dest_sock_client, file_name, cmd)
                    file = open(file_path, 'rb')
                    while True:
                        data = file.read(1024)
                        if not data:
                            break
                        socket.send(data)
                    file.close()
            else:
                send_msg(sock_client, "{} belum menjadi teman".format(dest), cmd) 
        elif cmd == "msg":
            if dest in clients[username_client][3]:
                print(clients[username_client][3])
                dest_sock_client = clients[dest][0]
                send_msg(dest_sock_client, msg, cmd)
            else:
                send_msg(sock_client, "{} belum menjadi teman".format(dest), cmd)    
        print(data)

    sock_client.close()
    print("Connection closed", addr_client)

# kirim ke semua klien
def send_broadcast(clients, data, sender_addr_client, cmd, username_client):
    for username in clients[username_client][3]:
        sock_client, addr_client, _, friend = clients[username]
    # for sock_client, addr_client, _, friend in clients.values():
        if not (sender_addr_client[0] == addr_client[0] and sender_addr_client[1] == addr_client[1]):
            send_msg(sock_client, data, cmd)

def send_msg(socket_client, data, cmd):
    socket_client.send(bytes("{}|{}".format(data, cmd), "utf-8"))

# cek file path
def find_file(file_name):
    for root, dirs, files in os.walk('..'):
        for file in files:
            # print(file)
            if file == file_name:
                return os.path.join(root, file)
    return None

# membuat object socket server
sock_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bind object socket ke alamat ip dan port
sock_server.bind(("0.0.0.0", 6666))

# listen for an incoming connection
# 5 --> backlog, maksimum antrian (queue) untuk incoming connection
sock_server.listen(5)

# buat dictionary untuk menyimpan informasi tentang client
clients = {}
# friends = set()

while True:
    # accept connection from client
    sock_client, addr_client = sock_server.accept()

    # baca username client
    username_client = sock_client.recv(65535).decode("utf-8")
    print(username_client, "joined")

    #  buat thread baru untuk membaca pesan
    thread_client = threading.Thread(target=read_msg, args=(clients, sock_client, addr_client, username_client))
    thread_client.start()

    friends = set()

    # simpan informasi tentang client ke dictionary
    clients[username_client] = (sock_client, addr_client, thread_client, friends)