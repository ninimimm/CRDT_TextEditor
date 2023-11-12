import asyncio
from Converter import Converter
from Merge_crdt import Merge

class ServerProtocol(asyncio.DatagramProtocol):
    def __init__(self, server):
        self.server = server

    def connection_made(self, transport):
        self.server.transport = transport
        self.server.set_transport(transport)  # Передаем transport в Server

    def datagram_received(self, data, addr):
        asyncio.create_task(self.server.handle_client_data(data, addr))

    def error_received(self, exc):
        print('Error received:', exc)

    def connection_lost(self, exc):
        print('Connection closed:', exc)


class Server:
    def __init__(self):
        self.server_blocks = []
        self.merge = Merge(self.server_blocks)
        self.addresses = set()
        self.addr_list = []
        self.converter = Converter("")
        self.transport = None  # Инициализируем transport как None

    def set_transport(self, transport):
        self.transport = transport  # Устанавливаем transport

    async def handle_client_data(self, data, addr):
        if addr not in self.addresses:
            self.addresses.add(addr)
            self.addr_list.append(addr)

        data = data.decode("utf-8")
        if len(data) > 0:
            if data == "connect":
                await self.send(self.converter.convert_crdt_to_str(self.server_blocks).encode("utf-8"), addr)
            else:
                await self.merge_and_send_crdt(data)

    async def merge_and_send_crdt(self, data):
        print(data)
        crdt = self.converter.convert_string_to_crdt(data)
        print(crdt.blocks, "который приняли")
        self.merge.merge(crdt)
        await asyncio.gather(*[self.send(crdt, address) for address in self.addr_list])

    async def send(self, crdt, addr):
        if self.transport:
            self.transport.sendto(self.converter.convert_crdt_to_str(crdt.blocks).encode("utf-8"), addr)
        else:
            print("Transport не установлен")


async def main():
    loop = asyncio.get_running_loop()
    server = Server()

    transport, protocol = await loop.create_datagram_endpoint(
        lambda: ServerProtocol(server),
        local_addr=('0.0.0.0', 8080))

    print("Сервер запущен и ждет подключений.")

    try:
        await asyncio.Future()  # Запуск бесконечного цикла
    finally:
        transport.close()

if __name__ == '__main__':
    asyncio.run(main())
