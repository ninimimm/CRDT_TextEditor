import datetime
from queue import Queue
import select
import socket
import threading
import re
from GUI import GUI
from Converter import Converter
from CRDT_structure import CRDT

class Client:
    def __init__(self):
        self.crdt = CRDT("replica2")
        self.lock = threading.Lock()

class SharedData:
    def __init__(self):
        self.send = Queue()


def update_cursor(cur):
    with class_client.crdt.lock:
        len_cursor = 0
        max_time, index = datetime.datetime(2000, 1, 1), -1
        for i in range(len(class_client.crdt.blocks)):
            if class_client.crdt.blocks[i].cursor is not None\
                    and class_client.crdt.blocks[i].replica == "replica2":
                if class_client.crdt.blocks[i].time > max_time:
                    max_time = class_client.crdt.blocks[i].time
                    index = i
            class_client.crdt.blocks[i].replica = None
            len_cursor += len(class_client.crdt.blocks[i].value)
        if cur != len_cursor and index != -1:
            gui.editor.mark_set("insert", f"1.{len_cursor}")
            if len_cursor > 1:
                gui.last_cursor = len_cursor - 1


def update_crdt(data):
    with class_client.crdt.lock:
        new_crdt = converter.convert_string_to_crdt(data)
        cur = gui.get_cursor_pos()
        if data != "empty":
            replace_text(''.join(re.findall(r"(?:\*\&#\(&|^)(.+?)#\$\(!\-\!\>", data)), cur)
        hash = class_client.crdt.current_hash
        class_client.crdt = new_crdt
        class_client.crdt.current_hash = hash
        update_cursor(cur)


def replace_text(update, cur):
    gui.editor.delete("1.0", "end")
    gui.editor.insert("1.0", update)
    gui.editor.mark_set("insert", f"1.{cur}")


def start_connection(client, ip_port):
    client.sendto("connect".encode('utf-8'), ip_port)
    data, _ = client.recvfrom(1024)
    update_crdt(data.decode('utf-8'))


if __name__ == "__main__":
    pattern = r"\*&#\(&([^*#$]*)#\$\(!\-!\>"
    class_client = Client()
    converter = Converter(class_client.crdt.replica_id)
    shared_data = SharedData()
    gui = GUI(shared_data, class_client)

    def run_start():
        gui.root.mainloop()

    def connection():
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip_port = ('158.160.7.179', 8080)

        start_connection(client, ip_port)
        while True:
            if not shared_data.send.empty():
                with class_client.crdt.lock:
                    while not shared_data.send.empty():
                        cursor, blocks, lens_of_blocks = shared_data.send.get()
                        index, count = class_client.crdt.cursor_to_index(cursor, blocks, lens_of_blocks)
                        if len(class_client.crdt.blocks) > 0:
                            class_client.crdt.blocks[index].cursor = count
                        client.sendto(converter.convert_crdt_to_str(blocks).encode('utf-8'), ip_port)
                        print(blocks)
            ready = select.select([client], [], [], 0.05)
            if ready[0]:
                data, _ = client.recvfrom(1024)
                update_crdt(data.decode('utf-8'))

    threading.Thread(target=connection).start()
    run_start()
