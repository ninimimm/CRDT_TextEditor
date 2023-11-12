import tkinter as tk
from tkinter import scrolledtext


class GUI:
    def __init__(self, shared_data, struct):
        self.shared_data = shared_data
        self.struct = struct
        self.cursor = 0
        self.root = tk.Tk()
        self.root.title("CRDT Text Editors")

        self.editor = scrolledtext.ScrolledText(self.root, width=40, height=10)
        self.full_text_editor()


    def full_text_editor(self):
        self.editor.pack(side="left", fill="both", expand=True)
        self.editor.bind("<Key>", lambda event: self.on_key(event))
        self.editor.bind("<BackSpace>", self.on_backspace)
        self.editor.bind("<Control-KeyPress>", self.keypress)
        self.editor.bind('<Control-v>', self.paste_text or 'break')

    def get_cursor_pos(self):
        current_index = self.editor.index(tk.INSERT)
        text_up_to_cursor = self.editor.get("1.0", current_index)
        return len(text_up_to_cursor)

    def merge_texts(self):
        self.shared_data.send.put(self.struct.crdt.blocks)

    def refresh_text_widgets(self):
        position = self.editor.index(tk.INSERT)
        self.editor.delete("1.0", tk.END)
        editor_content = self.struct.crdt.display()
        if editor_content is not None:
            self.editor.insert("1.0", editor_content)
        self.editor.mark_set("insert", f"{position}")
        self.cursor = int(position.split('.')[1]) - 1


    def on_key(self, event):
        if len(event.char) == 1:
            cursor_pos = self.get_cursor_pos()
            if cursor_pos - 1 != self.cursor:
                self.struct.crdt.cursor_insert(cursor_pos, event.char)
            else:
                self.struct.crdt.add_string(cursor_pos, event.char)
            self.cursor = cursor_pos
            self.editor.insert(f"1.{cursor_pos}", event.char)
            self.merge_texts()
            return "break"

    def on_backspace(self, event):
        cursor_pos = self.get_cursor_pos()
        if cursor_pos > 0:
            self.cursor -= 1
            self.struct.crdt.cursor_remove(cursor_pos)
            self.editor.delete(f"1.{cursor_pos}", f"1.{cursor_pos}")
            self.merge_texts()

    def copy_text(self):
        selected_text = self.editor.selection_get()
        self.root.clipboard_clear()
        self.root.clipboard_append(selected_text)

    def paste_text(self):
        try:
            clipboard_text = self.root.clipboard_get()
        except tk.TclError as e:
            return
        cursor_pos = self.get_cursor_pos()
        self.struct.crdt.cursor_insert(cursor_pos, clipboard_text)
        self.cursor = cursor_pos + len(clipboard_text)
        self.editor.insert(tk.INSERT, clipboard_text)
        self.editor.see(tk.INSERT)

    def keypress(self, e):
        if e.keycode == 86 and e.keysym != 'v':
            self.paste_text() or 'break'
        elif e.keycode == 67 and e.keysym != 'c':
            self.copy_text()
