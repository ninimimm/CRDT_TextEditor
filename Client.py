import datetime
from queue import Queue
import select
import socket
import threading
import re
from GUI import GUI
from Converter import Converter
from CRDT_structure import CRDT
import tkinter as tk


class SharedData:  # pragma: no cover
    def __init__(self):
        self.send = Queue()


class Client:  # pragma: no cover
    def __init__(self):
        self.crdt = CRDT("replica2")
        self.lock = threading.Lock()
        self.gui = None

    def update_cursor(self, cur):
        with self.crdt.lock:
            len_cursor = 0
            max_time, index, current_len = datetime.datetime(2000, 1, 1), -1, 0
            for i in range(len(self.crdt.blocks)):
                if self.crdt.blocks[i].cursor is not None\
                        and self.crdt.blocks[i].replica == "replica2":
                    if self.crdt.blocks[i].time > max_time:
                        max_time = self.crdt.blocks[i].time
                        index = i
                        current_len = len_cursor
                self.crdt.blocks[i].replica = None
                len_cursor += len(self.crdt.blocks[i].value)
            cur_cur = None
            if index != -1:
                cur_cur = current_len + self.crdt.blocks[index].cursor
            if cur != cur_cur and index != -1:
                self.gui.editor.mark_set("insert", f"1.{cur_cur}")
                if cur_cur > 1:
                    self.gui.last_cursor = cur_cur - 1
            return cur_cur

    def update_crdt(self, data):  # pragma: no cover
        with self.crdt.lock:
            new_crdt = converter.convert_string_to_crdt(data)
            cur = self.gui.get_cursor_pos()
            if data != "empty":
                self.replace_text(''.join(re.findall(r"(?:\*\&#\(&|^)(.+?)#\$\(!\-\!\>", data)), cur, new_crdt)
            hash = self.crdt.current_hash
            self.crdt = new_crdt
            self.crdt.current_hash = hash
            self.update_cursor(cur)

    def replace_text(self, update, cur, new_crdt):  # pragma: no cover
        self.gui.editor.delete("1.0", "end")
        if self.gui.is_blame:
            last_index = 0
            for block in new_crdt.blocks:
                block_length = len(block.value)
                self.gui.editor.insert(tk.END, ''.join(block.value), block.replica)
                last_index += block_length
        else:
            self.gui.editor.insert("1.0", update)
        self.gui.editor.mark_set("insert", f"1.{cur}")

    def start_connection(self, client, ip_port):  # pragma: no cover
        client.sendto("connect".encode('utf-8'), ip_port)
        data, _ = client.recvfrom(1024)
        self.update_crdt(data.decode('utf-8'))


if __name__ == "__main__":  # pragma: no cover
    pattern = r"\*&#\(&([^*#$]*)#\$\(!\-!\>"
    class_client = Client()
    converter = Converter(class_client.crdt.replica_id)
    shared_data = SharedData()
    gui = GUI(shared_data, class_client)

    def run_start():   # pragma: no cover
        gui.root.mainloop()

    def connection():  # pragma: no cover
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip_port = ('127.0.0.1', 8080)
        # ip_port = ('158.160.7.179', 8080)

        class_client.start_connection(client, ip_port)
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
                class_client.update_crdt(data.decode('utf-8'))

    threading.Thread(target=connection).start()
    run_start()
