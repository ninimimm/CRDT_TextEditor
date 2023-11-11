from CRDT_structure import CRDT
import copy
class Merge:
    def __init__(self):
        self.set_merge = set()
        pass
    def merge(self, crdt1):
        crdt = CRDT("")
        new_set_merge = set()
        for block in crdt1.blocks:
            tuple = (len(block[0]), block[1])
            if tuple not in self.set_merge and block[3] is None:
                    continue
            new_set_merge.add((len(block[0]), block[1]))
            crdt.insert(len(crdt.blocks), block[0], block[1], block[2], block[3])
        crdt1.blocks = copy.deepcopy(crdt.blocks)
        crdt1.lens_of_blocks = crdt.lens_of_blocks.copy()
        self.set_merge = new_set_merge

