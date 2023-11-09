import socket
from Converter import Converter
import threading
from CRDT_structure import CRDT
from Merge_crdt import Merge

def get_data(cl):
    return cl.recv(1024).decode('utf-8')

def send_data(cl, data):
    cl.sendall(data.encode('utf-8'))

class Server:
    def __init__(self):
        self.crdt = CRDT("server")
        self.Merge = Merge()

    def merge_and_send_crdt(self, cl, cv, data):
        crdt = cv.convert_string_to_crdt(data)
        self.Merge.merge(crdt, self.crdt)
        print(self.crdt.blocks)
        send_data(cl, cv.convert_crdt_to_str(crdt))

def handle_client(client, address):
    while True:
        try:
            data = get_data(client)
            if len(data) > 0:
                server_class.merge_and_send_crdt(client, converter, data)
        except (ConnectionResetError, OSError) as Ex:
            print(Ex)
            print("Клиент отключился")
            break
    client.close()

if __name__ == '__main__':
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 8080))
    server.listen()
    server_class = Server()
    converter = Converter(server_class)
    print("Сервер запущен и ждет подключений.")
    clients = []
    while True:
        client, address = server.accept()
        clients.append(client)
        print(f"Подключен клиент {address}")
        threading.Thread(target=handle_client, args=(client, address)).start()
