from CRDT_structure import CRDT
import copy
class Merge:
    def __init__(self):
        self.set_merge = set()
        pass
    def merge(self, crdt1, crdt2):
        first_index = 0
        second_index = 0
        crdt = CRDT("")
        print(self.set_merge)
        while first_index < len(crdt1.blocks) and second_index < len(crdt2.blocks):
            first, second = crdt1.blocks[first_index], crdt2.blocks[second_index]
            if first[1] < second[1]:
                if first[1] in self.set_merge:
                    crdt.insert(len(crdt.blocks), first[0], timestamp=first[1], cursor=first[3])
                    first_index += 1
                    second_index += 1
                else:
                    crdt.insert(len(crdt.blocks), first[0], timestamp=first[1], cursor=first[3])
                    first_index += 1
                save = crdt.blocks[-1]
                self.set_merge.add(save[1])
            elif first[1] > second[1]:
                if first[1] in self.set_merge:
                    crdt.insert(len(crdt.blocks), first[0], timestamp=first[1], cursor=first[3])
                    first_index += 1
                    second_index += 1
                else:
                    crdt.insert(len(crdt.blocks), second[0], timestamp=second[1], cursor=second[3])
                    second_index += 1
                save = crdt.blocks[-1]
                self.set_merge.add(save[1])
            else:
                if first[3] is not None:
                    crdt.insert(len(crdt.blocks), first[0], timestamp=first[1], cursor=first[3])
                else:
                    crdt.insert(len(crdt.blocks), second[0], timestamp=second[1], cursor=second[3])
                first_index += 1
                second_index += 1
        if first_index == len(crdt1.blocks):
            for i in range(second_index, len(crdt2.blocks)):
                crdt.insert(len(crdt.blocks), crdt2.blocks[i][0], timestamp=crdt2.blocks[i][1], cursor=crdt2.blocks[i][3])
                save = crdt.blocks[-1]
                self.set_merge.add(save[1])
        else:
            for i in range(first_index, len(crdt1.blocks)):
                crdt.insert(len(crdt.blocks), crdt1.blocks[i][0], timestamp=crdt1.blocks[i][1], cursor=crdt1.blocks[i][3])
                save = crdt.blocks[-1]
                self.set_merge.add(save[1])
        crdt1.blocks = copy.deepcopy(crdt.blocks)
        for block in crdt1.blocks:
            block[2] = crdt1.replica_id
        crdt1.lens_of_blocks = crdt.lens_of_blocks.copy()
        crdt2.blocks = copy.deepcopy(crdt.blocks)
        for block in crdt2.blocks:
            block[2] = crdt2.replica_id
            if block[3] is not None:
                block[3] = None
        crdt2.lens_of_blocks = crdt.lens_of_blocks.copy()
        print(crdt1.blocks)
        print(crdt2.blocks)
