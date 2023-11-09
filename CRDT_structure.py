import datetime
class CRDT:
    def __init__(self, replica_id):
        self.replica_id = replica_id
        self.blocks = []
        self.lens_of_blocks = []
        self.editor = None

    def append(self, block, length):
        self.blocks.append(block)
        self.lens_of_blocks.append(length)

    def insert(self, index, value, timestamp=None, replica = None, cursor = None):
        if timestamp is None:
            timestamp = datetime.datetime.now()
        if replica is None:
            replica = self.replica_id
        self.blocks.insert(index, [list(value), timestamp, replica, cursor])
        self.lens_of_blocks.insert(index, len(value))


    def remove(self, index):
        self.blocks.pop(index)
        self.lens_of_blocks.pop(index)

    def cursor_to_index(self, cursor):
        index = -1
        if cursor == 0:
            return (0, 0)
        while cursor > 0 and len(self.blocks) > 0:
            index += 1
            if index == len(self.blocks):
                break
            cursor -= self.lens_of_blocks[index]
        return (index, cursor + self.lens_of_blocks[index])

    def cursor_insert(self, cursor, value):
        index, count = self.cursor_to_index(cursor)
        if len(self.blocks) > index:
            save_block = self.blocks[index].copy()
            self.remove(index)
            first_part, second_part = save_block[0][:count], save_block[0][count:]
            if len(second_part) > 0:
                self.insert(index, second_part, save_block[1])
            self.insert(index, value)
            if len(first_part) > 0:
                self.insert(index, first_part, save_block[1])
        else:
            self.insert(index, value)

    def cursor_remove(self, cursor):
        index, count = self.cursor_to_index(cursor)
        self.blocks[index][0].pop(count - 1)
        if len(self.blocks[index][0]) == 0:
            self.remove(index)

    def add_string(self, cursor, string):
        index, count = self.cursor_to_index(cursor)
        if index < len(self.blocks):
            self.blocks[index][0] = self.blocks[index][0] + list(string)
            self.lens_of_blocks[index] += len(string)
        else:
            self.insert(index, list(string), datetime.datetime.now())

    def display(self):
        return ''.join([''.join(block[0]) for block in self.blocks])
