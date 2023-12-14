from CRDT_structure import CRDT
import copy
from datetime import timedelta
class Merge:
    def __init__(self):
        self.server_crdt = CRDT("")
        self.set_merge = set()
        self.server_blocks = []
        pass

    def add_in_crdt(self, crdt, crdt1, i, times):
        if crdt1.blocks[i][1] not in times:
            crdt.insert(len(crdt.blocks), crdt1.blocks[i][0], timestamp=crdt1.blocks[i][1],
                        replica=crdt1.blocks[i][2], cursor=crdt1.blocks[i][3])
            times.add(crdt1.blocks[i][1])
            save = crdt.blocks[-1]
            self.set_merge.add((''.join(save[0]), save[1]))

    def merge(self, crdt1, replica):
        print("merge")
        print(crdt1.blocks)
        first_index = 0
        second_index = 0
        crdt = CRDT("")
        times_crdt = set((x[1] for x in crdt1.blocks))
        times = set()
        while first_index < len(crdt1.blocks) and second_index < len(self.server_crdt.blocks):
            if crdt1.blocks[first_index][1] < self.server_crdt.blocks[second_index][1]:
                if crdt1.blocks[first_index][0] == self.server_crdt.blocks[second_index][0] and \
                        (''.join(crdt1.blocks[first_index][0]), crdt1.blocks[first_index][1]) in self.set_merge:
                    self.add_in_crdt(crdt, crdt1, first_index, times)
                    first_index += 1
                    second_index += 1
                else:
                    self.add_in_crdt(crdt, crdt1, first_index, times)
                    first_index += 1
            elif crdt1.blocks[first_index][1] > self.server_crdt.blocks[second_index][1]:
                if crdt1.blocks[first_index][0] == self.server_crdt.blocks[second_index][0] and\
                    (''.join(crdt1.blocks[first_index][0]), crdt1.blocks[first_index][1]) in self.set_merge:
                    self.add_in_crdt(crdt, crdt1, first_index, times)
                    first_index += 1
                    second_index += 1
                else:
                    self.add_in_crdt(crdt, self.server_crdt, second_index, times)
                    second_index += 1
            else:
                print(crdt1.replica_id)
                if self.server_crdt.blocks[second_index][2] == replica:
                    self.add_in_crdt(crdt, crdt1, first_index, times)
                else:
                    self.add_in_crdt(crdt, self.server_crdt, second_index, times)
                first_index += 1
                second_index += 1

        if first_index == len(crdt1.blocks):
            for i in range(second_index, len(self.server_crdt.blocks)):
                self.add_in_crdt(crdt, self.server_crdt, i, times)
        else:
            for i in range(first_index, len(crdt1.blocks)):
                self.add_in_crdt(crdt, crdt1, i, times)
        crdt1.blocks = copy.deepcopy(crdt.blocks)
        crdt1.lens_of_blocks = crdt.lens_of_blocks.copy()
        self.server_crdt.blocks = copy.deepcopy(crdt.blocks)
        self.server_crdt.lens_of_blocks = crdt.lens_of_blocks.copy()
        print(self.server_crdt.blocks, "итог")
