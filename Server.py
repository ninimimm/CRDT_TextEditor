import asyncio
from Converter import Converter
from Merge_crdt import Merge
from queue import Queue
import threading

class ServerProtocol(asyncio.DatagramProtocol):
    def __init__(self, server):
        self.server = server

    def connection_made(self, transport):
        self.server.transport = transport
        self.server.set_transport(transport)  # Передаем transport в Server

    def datagram_received(self, data, addr):
        if addr not in self.server.addresses:
            self.server.addresses.add(addr)
            self.server.addr_list.append(addr)
        data = data.decode("utf-8")
        print(data)
        if data == "connect":
            self.server.send(self.server.merge.server_crdt.blocks, addr)
        else:
            print(self.server.converter.convert_string_to_crdt(data)[1].blocks, "пришло")
            self.server.stack_crdt.put(self.server.converter.convert_string_to_crdt(data))

    def error_received(self, exc):
        print('Error received:', exc)

    def connection_lost(self, exc):
        print('Connection closed:', exc)


class Server:
    def __init__(self):
        self.merge = Merge()
        self.addresses = set()
        self.addr_list = []
        self.converter = Converter("олег")
        self.stack_crdt = Queue()
        self.transport = None  # Инициализируем transport как None

    def set_transport(self, transport):
        self.transport = transport  # Устанавливаем transport

    def stack_processing(self):
        while True:
            if not self.stack_crdt:
                continue
            replica, crdt = self.stack_crdt.get()
            self.merge.merge(crdt, replica)
            for address in self.addr_list:
                self.send(crdt.blocks, address)

    def send(self, crdt_blocks, addr):
        if self.transport:
            self.transport.sendto(self.converter.convert_crdt_to_str(crdt_blocks).encode("utf-8"), addr)
        else:
            print("Transport не установлен")


async def main():
    loop = asyncio.get_running_loop()
    server = Server()

    transport, protocol = await loop.create_datagram_endpoint(
        lambda: ServerProtocol(server),
        local_addr=('0.0.0.0', 8080))

    print("Сервер запущен и ждет подключений.")

    threading.Thread(target=server.stack_processing).start()

    try:
        await asyncio.Future()  # Запуск бесконечного цикла
    finally:
        transport.close()

if __name__ == '__main__':
    asyncio.run(main())
