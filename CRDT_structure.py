import datetime
import copy
import time
class CRDTnew:
    def __init__(self, replica_id):
        self.replica_id = replica_id
        self.blocks = []
        self.lens_of_blocks = []

    def insert(self, index, value, timestamp=None, replica = None):
        if timestamp is None:
            timestamp = datetime.datetime.now()
        if replica is None:
            replica = self.replica_id
        self.blocks.insert(index, [list(value), timestamp, replica])
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
        index, count = self.cursor_to_index(cursor - 1)
        self.blocks[index][0].pop(count)

    def add_string(self, cursor, string):
        index, count = self.cursor_to_index(cursor)
        if index < len(self.blocks):
            self.blocks[index][0] = self.blocks[index][0] + list(string)
            self.lens_of_blocks[index] += len(string)
        else:
            self.insert(index, list(string), datetime.datetime.now())

    def display(self):
        return ''.join([''.join(block[0]) for block in self.blocks])

class Merge:
    def __init__(self):
        pass
    def merge(self, crdt1, crdt2):
        first_index = 0
        second_index = 0
        crdt = CRDTnew("")
        crdt_values = []
        while first_index < len(crdt1.blocks) and second_index < len(crdt2.blocks):
            if crdt1.blocks[first_index][1] < crdt2.blocks[second_index][1]:
                if crdt1.blocks[first_index][0] not in crdt_values:
                    crdt.insert(len(crdt.blocks), crdt1.blocks[first_index][0])
                    crdt_values.append(crdt1.blocks[first_index][0])
                first_index += 1
            else:
                if crdt2.blocks[second_index][0] not in crdt_values:
                    crdt_values.append(crdt2.blocks[second_index][0])
                    crdt.insert(len(crdt.blocks), crdt2.blocks[second_index][0])
                second_index += 1
        if first_index == len(crdt1.blocks):
            for i in range(second_index, len(crdt2.blocks)):
                if crdt2.blocks[second_index][0] not in crdt_values:
                    crdt_values.append(crdt2.blocks[i][0])
                    crdt.insert(len(crdt.blocks), crdt2.blocks[i][0])
        else:
            for i in range(first_index, len(crdt1.blocks)):
                if crdt1.blocks[first_index][0] not in crdt_values:
                    crdt_values.append(crdt1.blocks[i][0])
                    crdt.insert(len(crdt.blocks), crdt1.blocks[i][0])
        crdt1.blocks = copy.deepcopy(crdt.blocks)
        for block in crdt1.blocks:
            block[2] = crdt1.replica_id
        crdt1.lens_of_blocks = crdt.lens_of_blocks.copy()
        crdt2.blocks = copy.deepcopy(crdt.blocks)
        for block in crdt2.blocks:
            block[2] = crdt2.replica_id
        crdt2.lens_of_blocks = crdt.lens_of_blocks.copy()
        print(crdt1.blocks)
        print(crdt2.blocks)
        print(crdt.blocks)

"""
a b
a b c

Привет - a Алиса -b
Привет - a Алиса -b , пока! - c

Привет Алиса Привет Алиса, пока!
"""