import socket
from Converter import Converter
import threading
from CRDT_structure import CRDT
from Merge_crdt import Merge

class Server:
    def __init__(self):
        self.crdt = CRDT("server")
        self.Merge = Merge()

    def merge_and_send_crdt(self, address, cv, data):
        crdt = cv.convert_string_to_crdt(data)
        self.Merge.merge(crdt, self.crdt)
        print(self.crdt.blocks)
        server.sendto(cv.convert_crdt_to_str(crdt).encode("utf-8"), address)

def handle_clients():
    while True:
        try:
            data, address = server.recvfrom(1024)
            data = data.decode("utf-8")
            if len(data) > 0:
                server_class.merge_and_send_crdt(address, converter, data)
        except (ConnectionResetError, OSError) as Ex:
            print(Ex)
            print("Клиент отключился")
            break

if __name__ == '__main__':
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(('0.0.0.0', 8080))
    server_class = Server()
    converter = Converter()
    print("Сервер запущен и ждет подключений.")
    threading.Thread(target=handle_clients).start()
