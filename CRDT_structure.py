from datetime import datetime, timedelta
from typing import List
from dataclasses import dataclass
import threading


@dataclass
class Range:
    start: int
    finish: int

    def __lt__(self, other):
        return (self.start, self.finish) < (other.start, other.finish)

    def __gt__(self, other):
        return (self.start, self.finish) > (other.start, other.finish)

    def __eq__(self, other):
        return self.start == other.start and self.finish == other.finish


@dataclass
class Block:
    value: List[str]
    replica: str or None
    cursor: int or None
    Range: Range or None
    time: datetime
    hash: int


class CRDT:
    def __init__(self, replica_id):
        self.replica_id = replica_id
        self.blocks = []
        self.lens_of_blocks = []
        self.editor = None
        self.lock = threading.Lock()
        self.current_hash = 0

    def append(self, block, length):
        self.blocks.append(block)
        self.lens_of_blocks.append(length)

    def insert(self, index, value, replica=None, cursor=None, range=None, hash=None, time=datetime.now()):
        self.blocks.insert(index, Block(value=value, replica=replica, cursor=cursor,
                                        Range=Range(start=range.start, finish=range.finish), time=time,
                                        hash=hash if hash is not None else self.current_hash))
        self.current_hash += 1
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
                save_block = self.blocks[index]
                first_part, second_part = save_block.value[:count], save_block.value[count:]
                if len(second_part) > 0 and len(first_part) > 0:
                    self.remove(index)
                    self.insert(index, value=second_part, replica=self.replica_id,
                                range=Range(start=save_block.Range.start + count, finish=save_block.Range.finish),
                                hash=save_block.hash, time=save_block.time)
                    self.insert(index, value=list(value), replica=self.replica_id, cursor=len(value),
                                range=Range(start=0, finish=len(value)))
                    self.insert(index, value=first_part, replica=self.replica_id,
                                range=Range(start=save_block.Range.start, finish=save_block.Range.start + count),
                                hash=save_block.hash, time=save_block.time)
                else:
                    self.insert(index, value=list(value), replica=self.replica_id, cursor=len(value), range=Range(start=0, finish=len(value)))
            else:
                self.insert(index, value=list(value), replica=self.replica_id, cursor=len(value), range=Range(start=0, finish=len(value)))

    def cursor_remove(self, cursor):
        with self.lock:
            index, count = self.cursor_to_index(cursor, self.blocks, self.lens_of_blocks)
            if count == len(self.blocks[index].value):
                self.blocks[index].value.pop(count - 1)
                if len(self.blocks[index].value) == 0:
                    self.remove(index)
            else:
                save_block = self.blocks[index]
                self.remove(index)
                first_part, second_part = save_block.value[:count - 1], save_block.value[count:]
                if len(second_part) > 0:
                    self.insert(index, value=second_part, replica=self.replica_id,
                                range=Range(start=save_block.Range.start + count, finish=save_block.Range.finish),
                                hash=save_block.hash, time=save_block.time)
                if len(first_part) > 0:
                    self.insert(index, value=first_part, replica=self.replica_id, cursor=len(first_part),
                                range=Range(start=save_block.Range.start, finish=save_block.Range.start + count - 1),
                                hash=save_block.hash, time=save_block.time)

    def add_string(self, cursor, string):
        with self.lock:
            index, count = self.cursor_to_index(cursor, self.blocks, self.lens_of_blocks)
            if index < len(self.blocks):
                if count == 0:
                    self.insert(index, value=list(string), replica=self.replica_id,
                                cursor=1, range=Range(start=0, finish=1))
                else:
                    self.blocks[index].value.append(string)
                    self.blocks[index].cursor = len(self.blocks[index].value)
                    self.blocks[index].replica = self.replica_id
                    self.blocks[index].Range.finish += 1
                    self.blocks[index].time = datetime.now()
                    self.lens_of_blocks[index] += len(string)
            else:
                self.insert(index, value=list(string), replica=self.replica_id,
                            cursor=1, range=Range(start=0, finish=1))

    def display(self):
        return ''.join([''.join(block.value) for block in self.blocks])
