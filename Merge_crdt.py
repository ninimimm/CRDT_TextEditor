from CRDT_structure import CRDT
import copy
from queue import Queue


class Merge:
    def __init__(self):
        self.server_blocks = []

    def merge_enumeration(self, enum1, enum2):
        print([x.value for x in enum1], [x.value for x in enum2], "enum")
        ans_enum = []
        if enum1:
            hash = enum1[0].hash
        while enum1 and enum2:
            if enum1[0].Range < enum2[0].Range:
                for i in range(len(enum1[0].value)):
                    enum2[0].value.pop(0)
                    if enum2[0].cursor is not None:
                        enum2[0].cursor -= 1
                ans_enum.append(enum1.pop(0))
                while enum1 and enum1[0].hash != hash:
                    ans_enum.append(enum1.pop(0))
            elif enum1[0].Range > enum2[0].Range:
                for i in range(len(enum2[0].value)):
                    enum1[0].value.pop(0)
                    if enum1[0].cursor is not None:
                        enum1[0].cursor -= 1
                ans_enum.append(enum2.pop(0))
                while enum2 and enum2[0].hash != hash:
                    ans_enum.append(enum2.pop(0))
            else:
                ans_enum.append(enum1.pop(0))
                enum2.pop(0)
                while enum1 and enum1[0].hash != hash:
                    ans_enum.append(enum1.pop(0))
                while enum2 and enum2[0].hash != hash:
                    ans_enum.append(enum2.pop(0))
        if enum1:
            for block in enum1:
                ans_enum.append(block)
        else:
            for block in enum2:
                ans_enum.append(block)

        result = []
        for block in ans_enum:
            if not result or result[-1].hash != block.hash:
                result.append(block)
            else:
                if result[-1].time < block.time:
                    if result[-1].cursor is not None and block.cursor is not None:
                        result[-1].cursor = len(result[-1].value) + block.cursor
                    result[-1].time = block.time
                result[-1].value += block.value
                result[-1].Range.finish += len(block.value)

        return result

    def get_replica(self, crdt1):
        for block in crdt1.blocks:
            if block.replica is not None:
                return block.replica
        return None

    def merge(self, crdt1):
        print(self.server_blocks, "тут")
        print(crdt1.blocks)
        set_hash_server = set([x.hash for x in self.server_blocks])
        merge_blocks = []
        new_blocks = Queue()
        person_blocks = crdt1.blocks.copy()

        while person_blocks:
            if person_blocks[0].replica is None:
                if new_blocks.empty():
                    person_blocks.pop(0)
                    continue
                while self.server_blocks and self.server_blocks[0].hash != person_blocks[0].hash:
                    merge_blocks.append(self.server_blocks.pop(0))
                while not new_blocks.empty():
                    merge_blocks.append(new_blocks.get())
            if person_blocks[0].hash not in set_hash_server:
                new_blocks.put(person_blocks.pop(0))
            else:
                enum1, enum2 = [], []
                hash = person_blocks[0].hash
                while person_blocks and person_blocks[0].replica is not None:
                    enum1.append(person_blocks.pop(0))
                while self.server_blocks and self.server_blocks[0].hash != hash:
                    merge_blocks.append(self.server_blocks.pop(0))

                i = 0
                while len(self.server_blocks) > i:
                    if self.server_blocks[i].hash == hash:
                        enum2 += self.server_blocks[0 : i + 1]
                        self.server_blocks = self.server_blocks[i + 1:]
                        i = 0
                    else:
                        i += 1
                merge_blocks += self.merge_enumeration(enum1, enum2)
        replica = self.get_replica(crdt1)
        set_crdt1 = set(crdt1.blocks)
        merge_blocks += [x for x in self.server_blocks if x.replica != replica or x in set_crdt1]
        while not new_blocks.empty():
            merge_blocks.append(new_blocks.get())
        crdt1.blocks = merge_blocks
        self.server_blocks = merge_blocks
        print(self.server_blocks)
