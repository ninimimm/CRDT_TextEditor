from queue import Queue
import socket
import threading
from GUI import GUI
from Converter import Converter
from CRDT_structure import CRDT
from Merge_crdt import Merge

class Client:
    def __init__(self):
        self.crdt = CRDT("replica1")
        self.Merge = Merge()

class SharedData:
    def __init__(self):
        self.send = Queue()

if __name__ == "__main__":
    class_client = Client()
    converter = Converter()
    shared_data = SharedData()
    gui = GUI(shared_data, class_client)
    def run_start():
        gui.root.mainloop()
    def connection():
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip_port = ('178.154.244.233', 8080)
        while True:
            if not shared_data.send.empty():
                get = None
                while not shared_data.send.empty():
                    get = shared_data.send.get()
                index, count = class_client.crdt.cursor_to_index(gui.get_cursor_pos())
                if len(class_client.crdt.blocks) > 0:
                    class_client.crdt.blocks[index][3] = count
                client.sendto(converter.convert_crdt_to_str(get).encode('utf-8'), ip_port)
                ans, _ = client.recvfrom(1024)
                class_client.crdt = converter.convert_string_to_crdt(ans.decode('utf-8'))
                gui.refresh_text_widgets()
                len_cursor = 0
                for i in range(len(class_client.crdt.blocks)):
                    if class_client.crdt.blocks[i][3] is not None and class_client.crdt.blocks[i][3] != -1:
                        len_cursor += class_client.crdt.blocks[i][3]
                        class_client.crdt.blocks[i][3] = None
                        break
                    len_cursor += class_client.crdt.lens_of_blocks[i]
                gui.editor.mark_set("insert", f"1.{len_cursor}")
                gui.cursor = len_cursor - 1

    threading.Thread(target=connection).start()
    run_start()
