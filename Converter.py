from CRDT_structure import CRDT
from datetime import datetime
class Converter:
    def __init__(self, struct):
        self.struct = struct

    def convert_crdt_to_str(self, crdt):
        return '--'.join([self.convert_block_to_str(x) for x in crdt.blocks])

    def convert_block_to_str(self, block):
        return f"{''.join(block[0])}::{block[1].strftime('%m/%d/%y %H:%M:%S')}::{block[2]}"

    def convert_string_to_crdt(self, data_string):
        blocks_str = data_string.split('--')
        crdt1 = CRDT("")
        for block_str in blocks_str:
            block = self.convert_string_to_block(block_str)
            crdt1.append(block, len(block[0]))
        return crdt1

    def convert_string_to_block(self, string):
        value, time, replica = string.split('::')
        return [list(value), datetime.strptime(time[1], '%m/%d/%y %H:%M:%S'), replica[3]]
