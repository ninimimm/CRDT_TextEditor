from queue import Queue
import select
import socket
import threading
from GUI import GUI
from Converter import Converter
from CRDT_structure import CRDT

class Client:
    def __init__(self):
        self.crdt = CRDT("replica2")

class SharedData:
    def __init__(self):
        self.send = Queue()

def update_cursor():
    with gui.lock:
        len_cursor = 0
        for i in range(len(class_client.crdt.blocks)):
            if class_client.crdt.blocks[i][3] is not None and class_client.crdt.blocks[i][3] != -1 \
                    and class_client.crdt.blocks[i][2] == "replica2":
                len_cursor += class_client.crdt.blocks[i][3]
                class_client.crdt.blocks[i][3] = None
                break
            len_cursor += class_client.crdt.lens_of_blocks[i]
        gui.editor.mark_set("insert", f"1.{len_cursor}")
        if len_cursor > 1:
            gui.cursor = len_cursor - 1


def update_crdt(data):
    new_crdt = converter.convert_string_to_crdt(data.decode('utf-8'))
    apply_incremental_changes(new_crdt, class_client.crdt)
    class_client.crdt = new_crdt
    update_cursor()


def apply_incremental_changes(new_crdt, old_crdt):
    new_blocks = new_crdt.blocks
    old_blocks = old_crdt.blocks

    # Находим индекс, с которого начинаются изменения
    change_index = 0
    for new_block, old_block in zip(new_blocks, old_blocks):
        if new_block != old_block:
            break
        change_index += 1

    # Удаляем старые блоки, начиная с индекса изменений
    for _ in range(change_index, len(old_blocks)):
        gui.editor.delete(f"1.{change_index}", "end")

    # Добавляем новые блоки
    for new_block in new_blocks[change_index:]:
        gui.editor.insert(f"1.{change_index}", ''.join(new_block[0]))
        change_index += 1


def start_connection(client, ip_port):
    client.sendto("connect".encode('utf-8'), ip_port)
    ans, _ = client.recvfrom(1024)
    update_crdt(ans)

if __name__ == "__main__":
    class_client = Client()
    converter = Converter(class_client.crdt.replica_id)
    shared_data = SharedData()
    gui = GUI(shared_data, class_client)
    def run_start():
        gui.root.mainloop()
    def connection():
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip_port = ('178.154.244.233', 8080)

        start_connection(client, ip_port)
        while True:
            if not shared_data.send.empty():
                while not shared_data.send.empty():
                    index, count = class_client.crdt.cursor_to_index(gui.cursor)
                    if len(class_client.crdt.blocks) > 0:
                        class_client.crdt.blocks[index][3] = count
                    client.sendto(converter.convert_crdt_to_str(shared_data.send.get()).encode('utf-8'), ip_port)
                    ans, _ = client.recvfrom(1024)
                    update_crdt(ans)
            ready = select.select([client], [], [], 0.05)
            if ready[0]:
                data, _ = client.recvfrom(1024)
                update_crdt(data)

    threading.Thread(target=connection).start()
    run_start()
