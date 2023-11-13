import tkinter as tk
from tkinter import scrolledtext
import threading
from queue import Queue

class GUI:
    def __init__(self, shared_data, struct):
        self.shared_data = shared_data
        self.struct = struct
        self.cursor = 0
        self.last_cursor = 0
        self.len_text = 0
        self.root = tk.Tk()
        self.root.title("CRDT Text Editors")

        self.editor = scrolledtext.ScrolledText(self.root, width=40, height=10)
        self.full_text_editor()

        self.lock = threading.Lock()
        self.input_queue = Queue()

    def full_text_editor(self):
        self.editor.pack(side="left", fill="both", expand=True)
        self.editor.bind("<Key>", self.on_key)
        self.editor.bind("<BackSpace>", self.on_backspace)
        # self.editor.bind("<Control-KeyPress>", self.keypress)
        # self.editor.bind('<Control-v>', self.paste_text or 'break')
        self.editor.bind("<Left>", self.move_cursor_left)
        self.editor.bind("<Right>", self.move_cursor_right)

    def move_cursor_left(self):
        if self.cursor > 0:
            self.cursor -= 1

    def move_cursor_right(self):
        if self.cursor < self.len_text:
            self.cursor += 1

    def merge_texts(self):
        self.shared_data.send.put(self.struct.crdt.blocks)

    def on_key(self, event):
        if len(event.char) == 1:

            if self.last_cursor - 1 != self.cursor or self.cursor == 0:
                self.struct.crdt.cursor_insert(self.cursor, event.char)
            else:
                self.struct.crdt.add_string(self.last_cursor, event.char)
            self.last_cursor = self.cursor
            self.cursor += 1
            self.merge_texts()

    def on_backspace(self, event):
        if self.cursor > 0:
            self.struct.crdt.cursor_remove(self.cursor - 1)
            self.editor.delete(f"1.{self.cursor}", f"1.{self.cursor}")
            self.cursor -= 1
            self.last_cursor = self.cursor - 1
            self.merge_texts()

    # def copy_text(self):
    #     selected_text = self.editor.selection_get()
    #     self.root.clipboard_clear()
    #     self.root.clipboard_append(selected_text)
    #
    # def paste_text(self):
    #     try:
    #         clipboard_text = self.root.clipboard_get()
    #     except tk.TclError as e:
    #         return
    #     cursor_pos = self.get_cursor_pos()
    #     self.struct.crdt.cursor_insert(cursor_pos, clipboard_text)
    #     self.cursor = cursor_pos + len(clipboard_text)
    #     self.editor.insert(tk.INSERT, clipboard_text)
    #     self.editor.see(tk.INSERT)

    # def keypress(self, e):
    #     if e.keycode == 86 and e.keysym != 'v':
    #         self.paste_text() or 'break'
    #     elif e.keycode == 67 and e.keysym != 'c':
    #         self.copy_text()
