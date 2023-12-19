from CRDT_structure import CRDT
from datetime import datetime
from CRDT_structure import Block, Range
class Converter:
    def __init__(self, replica):
        self.replica = replica

    def convert_crdt_to_str(self, crdt_blocks):
        return "*&#(&".join([self.convert_block_to_str(x) for x in crdt_blocks])\
            if len(crdt_blocks) > 0 else "empty"

    def convert_block_to_str(self, block):
        replace = '#$(!-!>'
        return f"{''.join(block.value)}{replace}{block.replica}{replace}{block.cursor}{replace}" \
               f"{block.Range.start},{block.Range.finish}{replace}{block.time.strftime('%m/%d/%y %H:%M:%S.%f')}" \
               f"{replace}{block.hash}"

    def convert_string_to_crdt(self, data_string):
        replace = '*&#(&'
        crdt1 = CRDT(self.replica)
        if data_string == "empty":
            return crdt1
        blocks_str = data_string.split(replace)
        for block_str in blocks_str:
            block = self.convert_string_to_block(block_str)
            crdt1.blocks.append(block, len(block[0]))
        return crdt1

    def convert_string_to_block(self, string):
        value, replica, cursor, range, time, hash = string.split('#$(!-!>')
        start, finish = range.split(',')
        return Block(value=list(value), replica=replica, cursor=None if cursor == "None" else int(cursor),
                     Range=Range(start=int(start), finish=int(finish)), time=datetime.strptime(time, '%m/%d/%y %H:%M:%S.%f'),
                     hash=hash)
