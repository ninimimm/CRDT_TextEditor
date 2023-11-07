import tkinter as tk
from tkinter import scrolledtext
from CRDT_structure import CRDTnew
from CRDT_structure import Merge

crdt1 = CRDTnew("replica1")
crdt2 = CRDTnew("replica2")
MERGE = Merge()

def get_cursor_pos(text_widget):
    current_index = text_widget.index(tk.INSERT)
    text_up_to_cursor = text_widget.get("1.0", current_index)
    return len(text_up_to_cursor)

def merge_texts():
    MERGE.merge(crdt1, crdt2)
    refresh_text_widgets()

def refresh_text_widgets():
    # Clear the existing content of the editor1
    editor1.delete("1.0", tk.END)
    # Insert the new content from crdt1's display method
    print(crdt1.blocks)
    print(crdt2.blocks)
    editor1_content = crdt1.display()  # ensure display() returns a string
    if editor1_content is not None:  # Check if content is not None
        editor1.insert("1.0", editor1_content)

    # Repeat the process for editor2 and crdt2
    editor2.delete("1.0", tk.END)
    editor2_content = crdt2.display()  # ensure display() returns a string
    if editor2_content is not None:  # Check if content is not None
        editor2.insert("1.0", editor2_content)


def on_key(event, crdt, text_widget):
    if len(event.char) == 1:  # Event for character input
        cursor_pos = get_cursor_pos(text_widget)
        print(event.char)
        crdt.add_string(cursor_pos, event.char)
        refresh_text_widgets()
        return "break"  # This prevents the default text widget behavior


def on_backspace(event, crdt, text_widget):
    cursor_pos = get_cursor_pos(text_widget)
    if cursor_pos > 0:
        crdt.cursor_remove(cursor_pos - 1)
        refresh_text_widgets()

# Создание объектов CRDT для каждого редактора


# Создание в окна
root = tk.Tk()
root.title("CRDT Text Editors")

# Создание первого текстового поля
editor1 = scrolledtext.ScrolledText(root, width=40, height=10)
editor1.pack(side="left", fill="both", expand=True)
editor1.bind("<Key>", lambda event: on_key(event, crdt1, editor1))
editor1.bind("<BackSpace>", lambda event: on_backspace(event, crdt1, editor1))

# Создание второго текстового поля
editor2 = scrolledtext.ScrolledText(root, width=40, height=10)
editor2.pack(side="right", fill="both", expand=True)
editor2.bind("<Key>", lambda event: on_key(event, crdt2, editor2))
editor2.bind("<BackSpace>", lambda event: on_backspace(event, crdt2, editor2))

# Создание кнопки для слияния текстов
merge_button = tk.Button(root, text="Merge", command=merge_texts)
merge_button.pack(side="bottom")

# Запуск главного цикла Tkinter
root.mainloop()
