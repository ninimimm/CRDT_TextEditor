from CRDT_structure import CRDT
import copy
class Merge:
    def __init__(self, server_blocks):
        self.set_merge = set()
        self.server_blocks = server_blocks
        pass

    def merge(self, crdt1):
        crdt_blocks = []
        new_set_merge = set()
        for block in crdt1.blocks:
            if (len(block[0]), block[1]) not in self.set_merge and block[3] is None:
                continue
            new_set_merge.add((len(block[0]), block[1]))
            crdt_blocks.append(block)

        crdt1.blocks = crdt_blocks
        self.server_blocks = crdt_blocks
        self.set_merge = new_set_merge
