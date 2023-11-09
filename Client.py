import socket
import select
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

# Создаем единственный экземпляр SharedData
shared_data = SharedData()
gui = GUI(shared_data)

# В ваших потоках используйте shared_data.coordinate и shared_data.gam
if __name__ == "__main__":
    class_client = Client()
    converter = Converter(class_client)
    def run_start():
        global gui
        gui.root.mainloop()
    def connection():
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('178.154.244.233', 8080))
        while True:
            if len(shared_data.send) > 0:
                client.sendall("merge".encode('utf-8'))
                client.sendall(shared_data.send.encode('utf-8'))
                class_client.crdt = converter.convert_string_to_crdt(client.recv(1024).decode('utf-8'))
                gui.refresh_text_widgets()

    threading.Thread(target=run_start).start()
    threading.Thread(target=connection).start()
