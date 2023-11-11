import socket
from Converter import Converter
import threading
from CRDT_structure import CRDT
from Merge_crdt import Merge
import asyncio

class Server:
    def __init__(self):
        self.Merge = Merge()
        self.addresses = set()
        self.addr_list = []

    def merge_and_send_crdt(self, cv, data):
        crdt = cv.convert_string_to_crdt(data)
        print(crdt.blocks, "который приняли")
        self.Merge.merge(crdt)
        await asyncio.gather(*[self.send(cv, crdt, addr) for addr in server_class.addr_list])


    async def send(self, cv, crdt, addr):
        server.sendto(cv.convert_crdt_to_str(crdt.blocks).encode("utf-8"), addr)
def handle_clients():
    while True:
        try:
            data, address = server.recvfrom(1024)
            if address not in server_class.addresses:
                server_class.addresses.add(address)
                server_class.addr_list.append(address)
            data = data.decode("utf-8")
            if len(data) > 0:
                server_class.merge_and_send_crdt(converter, data)
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
