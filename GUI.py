import tkinter as tk
from tkinter import scrolledtext
import threading
from queue import Queue

class GUI:
    def __init__(self, shared_data, struct):
        self.shared_data = shared_data
        self.struct = struct
        self.last_cursor = -1
        self.root = tk.Tk()
        self.root.title("CRDT Text Editors")

        self.editor = scrolledtext.ScrolledText(self.root, width=40, height=10)
        self.full_text_editor()
        self.input_queue = Queue()

    def full_text_editor(self):
        self.editor.pack(side="left", fill="both", expand=True)
        self.editor.bind("<Key>", self.on_key)
        self.editor.bind("<BackSpace>", self.on_backspace)
        # self.editor.bind("<Control-KeyPress>", self.keypress)
        # self.editor.bind('<Control-v>', self.paste_text or 'break')

    def get_cursor_pos(self):
        current_index = self.editor.index(tk.INSERT)
        return int(current_index.split('.')[1])

    def merge_texts(self, cursor, blocks, lens_of_blocks):
        self.shared_data.send.put([cursor, blocks, lens_of_blocks])

    def on_key(self, event):
        if len(event.char) == 1:
            with self.struct.crdt.lock:
                cursor = self.get_cursor_pos()
            print(cursor, "ON KEY", self.last_cursor)
            if self.last_cursor != cursor - 1 or cursor == 0:
                self.struct.crdt.cursor_insert(cursor, event.char)
            else:
                self.struct.crdt.add_string(cursor, event.char)
            self.last_cursor = cursor
            self.merge_texts(cursor + 1, self.struct.crdt.blocks, self.struct.crdt.lens_of_blocks)

    def on_backspace(self, event):
        cursor = self.get_cursor_pos()
        if cursor > 0:
            self.struct.crdt.cursor_remove(cursor)
            self.last_cursor = cursor - 2
            self.merge_texts(cursor - 1, self.struct.crdt.blocks, self.struct.crdt.lens_of_blocks)

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
