from datetime import datetime, timedelta
import threading


class CRDT:
    def __init__(self, replica_id):
        self.replica_id = replica_id
        self.blocks = []
        self.lens_of_blocks = []
        self.editor = None
        self.lock = threading.Lock()

    def append(self, block, length):
        self.blocks.append(block)
        self.lens_of_blocks.append(length)

    def insert(self, index, value, timestamp=None, replica = None, cursor = None):
        if timestamp is None:
            timestamp = datetime.now()
        if replica is None:
            replica = self.replica_id
        self.blocks.insert(index, [list(value), timestamp, replica, cursor])
        self.lens_of_blocks.insert(index, len(value))


    def remove(self, index):
        self.blocks.pop(index)
        self.lens_of_blocks.pop(index)

    def cursor_to_index(self, cursor, blocks, lens_of_blocks):
        index = -1
        if cursor == 0:
            return (0, 0)
        while cursor > 0 and len(blocks) > 0:
            index += 1
            if index == len(blocks):
                break
            cursor -= lens_of_blocks[index]
        return index, cursor + lens_of_blocks[index]

    def cursor_insert(self, cursor, value):
        with self.lock:
            index, count = self.cursor_to_index(cursor, self.blocks, self.lens_of_blocks)
            if len(self.blocks) > index:
                save_block = self.blocks[index].copy()
                self.remove(index)
                first_part, second_part = save_block[0][:count], save_block[0][count:]
                if len(second_part) > 0:
                    self.insert(index, second_part, save_block[1] + timedelta(microseconds=1), cursor=-1, replica=save_block[2])
                self.insert(index, value)
                if len(first_part) > 0:
                    self.insert(index, first_part, save_block[1], cursor=-1, replica=save_block[2])
            else:
                self.insert(index, value)

    def cursor_remove(self, cursor):
        with self.lock:
            index, count = self.cursor_to_index(cursor, self.blocks, self.lens_of_blocks)
            if count == len(self.blocks[index][0]):
                self.blocks[index][0].pop(count - 1)
                if len(self.blocks[index][0]) == 0:
                    self.remove(index)
            else:
                print(index, count, self.blocks)
                save_block = self.blocks[index].copy()
                self.remove(index)
                first_part, second_part = save_block[0][:count - 1], save_block[0][count:]
                print(first_part, second_part)
                print(first_part, second_part)
                if len(second_part) > 0:
                    self.insert(index, second_part, cursor=1)
                print(self.blocks)
                if len(first_part) > 0:
                    self.insert(index, first_part, cursor=len(first_part))
                print(self.blocks)



    def add_string(self, cursor, string):
        with self.lock:
            index, count = self.cursor_to_index(cursor, self.blocks, self.lens_of_blocks)
            if index < len(self.blocks):
                if count == 0:
                    self.insert(index, list(string), datetime.now())
                else:
                    self.blocks[index][0] += list(string)
                    self.lens_of_blocks[index] += len(string)
            else:
                self.insert(index, list(string), datetime.now())

    def display(self):
        return ''.join([''.join(block[0]) for block in self.blocks])
