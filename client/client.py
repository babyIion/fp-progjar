import socket
import sys
import select
import threading
import time
from threading import Timer

def countdown(t):
    while t:
        mins, secs = divmod(t, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        print(timer, end="\r")
        time.sleep(1)
        t -= 1

    print("Waktu habis!!")


def rebel_hide(socket_client):
    # countdown(int(5))
    t = Timer(5, print, ['Waktu habis!'])
    t.start()
    opt_place = input("Ayo cari tempat untuk bersembunyi!\n1. Pohon dekat jendela\n2. Meja teras\n3. Semak teras\n4. Rongsokan pojok halaman\n>>> ")
    t.cancel()

    return opt_place
    
    socket_client.send(bytes("{}".format(opt_place), "utf-8"))

def hunter_seek(socket_client):
    print("Tunggu para rebel untuk bersembunyi dahulu ya!")
    countdown(10)

    t = Timer(5, print, ['Waktu habis!'])
    t.start()
    opt_place = input("Para Rebel telah bersembunyi, mau cari ke mana?\n1. Pohon dekat jendela\n2. Meja teras\n3. Semak teras\n4. Rongsokan pojok halaman\n5. Bawah pohon beringin\n6. Gundukan semen\n>>> ")
    t.cancel()
    
    socket_client.send(bytes("{}".format(opt_place), "utf-8"))

def read_msg(socket_client):
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
thread_client = threading.Thread(target=read_msg, args=(socket_client,))
thread_client.start()

while True:
    # kirim/terima pesan
    # terima pesan tentang role
    # role = socket_client.recv(65535).decode("utf-8")
    role = input("Apa role Anda? (hunter atau rebel)\n>>> ") # buat testing
    if role == "rebel":
        opt_place = rebel_hide(socket_client)
    else:
        opt_place = hunter_seek(socket_client)
    
    
    cmd = input("Apa yang ingin Anda lakukan? \nbcast: broadcast pesan\nadd: menambah teman\nmsg: mengirim pesan\nfile: mengirim file\n>>>")
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