from CRDT_structure import CRDT
import copy
class Merge:
    def __init__(self):
        self.set_merge = set()
        self.server_blocks = []
        pass

    def merge(self, crdt1):
        crdt_blocks = []
        new_set_merge = set()
        for i in range(len(crdt1.blocks)):
            if (len(crdt1.blocks[i][0]), crdt1.blocks[i][1]) not in self.set_merge and crdt1.blocks[i][3] is None:
                print("не добавляем", crdt1.blocks[i][0])
                continue
            if i > 0 and crdt1.blocks[i][3] is not None and crdt1.blocks[i - 1][3] is not None\
                    and crdt1.blocks[i][2] == crdt1.blocks[i - 1][2]:
                crdt1.blocks[i][3] = None
            print("добавляем", crdt1.blocks[i][0])
            new_set_merge.add((len(crdt1.blocks[i][0]), crdt1.blocks[i][1]))
            crdt_blocks.append(crdt1.blocks[i])

        crdt1.blocks = crdt_blocks
        self.server_blocks = crdt_blocks
        self.set_merge = new_set_merge
