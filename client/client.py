import socket
import sys
import threading

def read_mdg(socket_client):
    while True:
        # terima pesan
        data, cmd = socket_client.recv(65535).decode("utf-8").split("|")
        if len(data) == 0:
            break
        if cmd == "file":
            file = open(data, 'wb')
            while True:
                isi_data = socket.recv(1024)
                if not isi_data:
                    break
                file.write(isi_data)
        else:
            print(data)

# buat object socket
socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect ke server
socket_client.connect(("127.0.0.1", 6666))

# kirim username ke server
socket_client.send(bytes(sys.argv[1], "utf-8"))

# buat thread untuk membaca pesan dan jalankan threadnya
thread_client = threading.Thread(target=read_mdg, args=(socket_client,))
thread_client.start()

while True:
    # kirim/terima pesan
    cmd = input("Apa yang ingin Anda lakukan? \nbcast: broadcast pesan\nadd: menambah teman\nmsg: mengirim pesan\nfile: mengirim file\n >>>")
    if cmd == "bcast":
        dest = "bcast"
        msg = input("Masukkan pesan Anda: ")
    elif cmd == "msg":
        dest = input("Masukkan username tujuan: ")
        msg = input("Masukkan pesan Anda: ")
    elif cmd == "add":
        dest = input("Masukkan username tujuan: ")
        msg = "add"
    elif cmd == "file":
        dest = input("Masukkan username tujuan: ")
        msg = input("Masukkan lokasi file yang akan dikirim: ")
    elif cmd == "exit":
        socket_client.close()
        break
    else:
        "Ups, command tidak ada! Coba lagi."

    socket_client.send(bytes("{}|{}|{}".format(dest, msg, cmd), "utf-8"))