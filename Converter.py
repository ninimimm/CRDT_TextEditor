from CRDT_structure import CRDT
from datetime import datetime
class Converter:
    def __init__(self, replica):
        self.replica = replica

    def convert_crdt_to_str(self, crdt_blocks):
        return f"{self.replica}!1#3$4№%" + "*&#(&".join([self.convert_block_to_str(x) for x in crdt_blocks])\
            if len(crdt_blocks) > 0 else "empty"

    def convert_block_to_str(self, block):
        replace = '#$(!-!>'
        return f"{''.join(block[0])}{replace}{block[1].strftime('%m/%d/%y %H:%M:%S.%f')}{replace}{block[2]}{replace}{block[3]}"

    def convert_string_to_crdt(self, data_string):
        replace = '*&#(&'
        if data_string == "empty":
            return ("replica2", CRDT("replica2"))
        replica, data_string = data_string.split("!1#3$4№%")
        print(data_string)
        crdt1 = CRDT(replica)
        blocks_str = data_string.split(replace)
        for block_str in blocks_str:
            block = self.convert_string_to_block(block_str)
            crdt1.append(block, len(block[0]))
        return (replica, crdt1)

    def convert_string_to_block(self, string):
        value, time, replica, cursor = string.split('#$(!-!>')
        return [list(value), datetime.strptime(time, '%m/%d/%y %H:%M:%S.%f'), replica, None if cursor == "None" else int(cursor)]
