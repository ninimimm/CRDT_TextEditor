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
    converter = Converter(class_client)
    shared_data = SharedData()
    gui = GUI(shared_data)
    def run_start():
        gui.root.mainloop()
    def connection():
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('178.154.244.233', 8080))
        while True:
            if len(shared_data.send) > 0:
                client.sendall(converter.convert_crdt_to_str(class_client.crdt).encode('utf-8'))
                class_client.crdt = converter.convert_string_to_crdt(client.recv(1024).decode('utf-8'))
                gui.refresh_text_widgets()


    threading.Thread(target=connection).start()
    run_start()
