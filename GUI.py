import tkinter as tk
from tkinter import scrolledtext
from queue import Queue


class GUI:
    def __init__(self, shared_data, struct):
        self.shared_data = shared_data
        struct.gui = self
        self.struct = struct
        self.last_cursor = -1
        self.root = tk.Tk()
        self.root.title("CRDT Text Editors")

        self.editor = scrolledtext.ScrolledText(self.root, width=40, height=10)
        self.full_text_editor()
        self.input_queue = Queue()
        self.is_blame = False

    def full_text_editor(self):  # pragma: no cover
        self.editor.pack(side="left", fill="both", expand=True)
        self.editor.bind("<Key>", self.on_key)
        self.editor.bind("<BackSpace>", self.on_backspace)
        self.editor.bind("<Control-KeyPress>", self.keypress)
        self.editor.tag_configure("replica1", foreground="green")
        self.editor.tag_configure("replica2", foreground="red")
        self.editor.tag_configure("black", foreground="black")

    def get_cursor_pos(self):  # pragma: no cover
        current_index = self.editor.index(tk.INSERT)
        return int(current_index.split('.')[1])

    def merge_texts(self, cursor, blocks, lens_of_blocks):  # pragma: no cover
        self.shared_data.send.put([cursor, blocks, lens_of_blocks])

    def on_key(self, event):  # pragma: no cover
        if len(event.char) == 1:
            with self.struct.crdt.lock:
                cursor = self.get_cursor_pos()
            if self.last_cursor != cursor - 1 or cursor == 0:
                self.struct.crdt.cursor_insert(cursor, event.char)
            else:
                self.struct.crdt.add_string(cursor, event.char)
            self.last_cursor = cursor
            self.merge_texts(cursor + 1, self.struct.crdt.blocks, self.struct.crdt.lens_of_blocks)

    def on_backspace(self, event):  # pragma: no cover
        cursor = self.get_cursor_pos()
        if cursor > 0:
            self.struct.crdt.cursor_remove(cursor)
            self.last_cursor = cursor - 2
            self.merge_texts(cursor - 1, self.struct.crdt.blocks, self.struct.crdt.lens_of_blocks)

    def copy_text(self):  # pragma: no cover
        selected_text = self.editor.selection_get()
        self.root.clipboard_clear()
        self.root.clipboard_append(selected_text)

    def paste_text(self):  # pragma: no cover
        try:
            clipboard_text = self.root.clipboard_get()
        except tk.TclError as e:
            return
        cursor_pos = self.get_cursor_pos()
        self.struct.crdt.cursor_insert(cursor_pos, clipboard_text)
        self.last_cursor = cursor_pos + len(clipboard_text)
        self.merge_texts(self.last_cursor, self.struct.crdt.blocks, self.struct.crdt.lens_of_blocks)
        self.editor.insert(tk.INSERT, clipboard_text)
        self.editor.see(tk.INSERT)

    def keypress(self, e):  # pragma: no cover
        if e.keycode == 86 or e.keysym == 'v':
            self.paste_text()
        elif e.keycode == 67 or e.keysym == 'c':
            self.copy_text()
        elif e.keycode == 66 or e.keysym == 'b':
            self.update_blame()

    def update_blame(self):  # pragma: no cover
        self.is_blame = not self.is_blame
        self.merge_texts(self.last_cursor, self.struct.crdt.blocks, self.struct.crdt.lens_of_blocks)
