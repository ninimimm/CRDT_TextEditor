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
        self.send = ""

if __name__ == "__main__":
    class_client = Client()
    converter = Converter()
    shared_data = SharedData()
    gui = GUI(shared_data, class_client)
    def run_start():
        gui.root.mainloop()
    def connection():
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # '178.154.244.233'
        client.connect(('178.154.244.233', 8080))
        while True:
            if len(shared_data.send) > 0:
                print(shared_data.send)
                print(converter.convert_crdt_to_str(class_client.crdt))
                index, count = class_client.crdt.cursor_to_index(gui.cursor)
                class_client.crdt.blocks[index][3] = count
                print(class_client.crdt.blocks)
                client.sendall(converter.convert_crdt_to_str(class_client.crdt).encode('utf-8'))
                ans = client.recv(1024).decode('utf-8')
                class_client.crdt = converter.convert_string_to_crdt(ans)
                gui.refresh_text_widgets()
                len_cursor = 0
                for i in range(len(class_client.crdt.blocks)):
                    print(class_client.crdt.blocks[i], "тут")
                    if class_client.crdt.blocks[i][3] is not None:
                        len_cursor += class_client.crdt.blocks[i][3]
                        class_client.crdt.blocks[i][3] = None
                        break
                    len_cursor += class_client.crdt.lens_of_blocks[i]
                gui.editor.mark_set("insert", f"1.{len_cursor}")
                gui.cursor = len_cursor - 1
                shared_data.send = ""


    threading.Thread(target=connection).start()
    run_start()
