import asyncio  # pragma: no cover
from Converter import Converter  # pragma: no cover
from Merge_crdt import Merge  # pragma: no cover


class ServerProtocol(asyncio.DatagramProtocol):  # pragma: no cover
    def __init__(self, server):
        self.server = server

    def connection_made(self, transport):  # pragma: no cover
        self.server.transport = transport
        self.server.set_transport(transport)

    def datagram_received(self, data, addr):  # pragma: no cover
        asyncio.create_task(self.server.handle_client_data(data, addr))

    def error_received(self, exc):  # pragma: no cover
        print('Error received:', exc)

    def connection_lost(self, exc):  # pragma: no cover
        print('Connection closed:', exc)


class Server:  # pragma: no cover
    def __init__(self):
        self.merge = Merge()
        self.addresses = set()
        self.addr_list = []
        self.converter = Converter("")
        self.transport = None

    def set_transport(self, transport):  # pragma: no cover
        self.transport = transport

    async def handle_client_data(self, data, addr):  # pragma: no cover
        if addr not in self.addresses:
            self.addresses.add(addr)
            self.addr_list.append(addr)

        data = data.decode("utf-8")
        if len(data) > 0:
            if data == "connect":
                await self.send(self.merge.server_blocks, addr)
            else:
                await self.merge_and_send_crdt(data)

    async def merge_and_send_crdt(self, data):  # pragma: no cover
        crdt = self.converter.convert_string_to_crdt(data)
        self.merge.merge(crdt)
        await asyncio.gather(*[self.send(crdt.blocks, address) for address in self.addr_list])
        print(self.merge.server_blocks)

    async def send(self, crdt_blocks, addr):  # pragma: no cover
        if self.transport:
            self.transport.sendto(self.converter.convert_crdt_to_str(crdt_blocks).encode("utf-8"), addr)
        else:
            print("Transport не установлен")


async def main():  # pragma: no cover
    loop = asyncio.get_running_loop()
    server = Server()

    transport, protocol = await loop.create_datagram_endpoint(
        lambda: ServerProtocol(server),
        local_addr=('0.0.0.0', 8080))

    print("Сервер запущен и ждет подключений.")

    try:
        await asyncio.Future()
    finally:
        transport.close()

if __name__ == '__main__':  # pragma: no cover
    asyncio.run(main())
