import socket
import threading
import os
import random

hunted = 0

def read_msg(clients, sock_client, addr_client, username_client):
    while True:
        # terima pesan
        data = sock_client.recv(65535).decode("utf-8")
        print(data)

        if len(data) == 0:
            break
        if "|" in data:
            # parsing pesannya
            dest, msg, cmd = data.split("|")
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
        else:
            if clients[username_client][4] == "rebel":
                clients[username_client][5] = data
                send_msg(sock_client, "Kamu bersembunyi di {}".format(data), "sembunyi")
            elif clients[username_client][4] == "hunter":
                opt_place = data
                for _, _, _, _,role, place in clients.values():
                    if role == "rebel":
                        # rebels += 1
                        if opt_place == place:
                            hunted += 1
                            if hunted == rebels:
                                send_msg(sock_client, "Kamu berhasil menangkap semua rebel! Selamat, hunter adalah pemenang!", "hunter menang")
                            else:
                                send_msg(sock_client, "Kamu berhasil menangkap rebel! Coba cari rebel yang lain!", "tangkap")
                        elif opt_place != place:
                            send_msg(sock_client, "Ups tidak ada rebel di sini! Coba cari tempat lain!", "gagal tangkap")

        # sock_client.close()
        print("Connection closed", addr_client)

# kirim ke semua klien
def send_broadcast(clients, data, sender_addr_client, cmd, username_client):
    for username in clients[username_client][3]:
        sock_client, addr_client, _, friend = clients[username]
    # for sock_client, addr_client, _, friend in clients.values():
        if not (sender_addr_client[0] == addr_client[0] and sender_addr_client[1] == addr_client[1]):
            send_msg(sock_client, data, cmd)

def send_msg(socket_client, data, cmd):
    print("{}|{}".format(data, cmd))
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

hunter = 0
rebel = 0

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
    place = ""
    roles = ["hunter", "rebel"]

    role = random.choice(roles)
    while hunter != 1:
        role = random.choice(roles)
        if role == "hunter":
            print(hunter)
            hunter += 1
        else:
            print(rebel)
            rebel += 1

    # simpan informasi tentang client ke dictionary
    clients[username_client] = [sock_client, addr_client, thread_client, friends, role, place]
    rebels = len(clients)

    for sock_client, addr_client, _, _, role, _ in clients.values():
        send_msg(sock_client, role, "Pembagian role")