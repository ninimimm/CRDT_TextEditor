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
        flag = False
        for i in range(len(class_client.crdt.blocks)):
            if class_client.crdt.blocks[i][3] is not None and class_client.crdt.blocks[i][3] != -1 \
                    and class_client.crdt.blocks[i][2] == "replica2":
                flag = True
                len_cursor += class_client.crdt.blocks[i][3]
                class_client.crdt.blocks[i][3] = None
                break
            len_cursor += class_client.crdt.lens_of_blocks[i]
        print(cur, len_cursor, "inside")
        if cur != len_cursor and flag:
            gui.editor.mark_set("insert", f"1.{len_cursor}")
            if len_cursor > 1:
                gui.last_cursor = len_cursor - 1


def update_crdt(data):
    with class_client.crdt.lock:
        new_crdt = converter.convert_string_to_crdt(data)
        cur = gui.get_cursor_pos()
        if data != "empty":
            replace_text(''.join(re.findall(r"(?:\*\&#\(&|^)(.+?)#\$\(!\-\!\>", data)), cur)
        class_client.crdt = new_crdt
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
    class_client.crdt.gui = gui
    def run_start():
        gui.root.mainloop()
    def connection():
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip_port = ('178.154.244.233', 8080)

        start_connection(client, ip_port)
        while True:
            if not shared_data.send.empty():
                with class_client.crdt.lock:
                    while not shared_data.send.empty():
                        cursor, blocks, lens_of_blocks = shared_data.send.get()
                        index, count = class_client.crdt.cursor_to_index(cursor, blocks, lens_of_blocks)
                        if len(class_client.crdt.blocks) > 0:
                            class_client.crdt.blocks[index][3] = count
                        client.sendto(converter.convert_crdt_to_str(blocks).encode('utf-8'), ip_port)
            ready = select.select([client], [], [], 0.05)
            if ready[0]:
                data, _ = client.recvfrom(1024)
                update_crdt(data.decode('utf-8'))

    threading.Thread(target=connection).start()
    run_start()
