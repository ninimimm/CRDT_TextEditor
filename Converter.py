from CRDT_structure import CRDT
from datetime import datetime
class Converter:
    def __init__(self):
        pass

    def convert_crdt_to_str(self, crdt):
        replace = '*&#(&^#$)(&^)*&!#^&$**!'
        return f"{replace}".join([self.convert_block_to_str(x) for x in crdt.blocks])

    def convert_block_to_str(self, block):
        replace = '<*%*$&:-*&#$(!-!>'
        return f"{''.join(block[0])}{replace}{block[1].strftime('%m/%d/%y %H:%M:%S.%f')}{replace}{block[2]}{replace}{block[3]}"

    def convert_string_to_crdt(self, data_string):
        replace = '*&#(&^#$)(&^)*&!#^&$**!'
        blocks_str = data_string.split(replace)
        crdt1 = CRDT("")
        for block_str in blocks_str:
            block = self.convert_string_to_block(block_str)
            crdt1.append(block, len(block[0]))
        return crdt1

    def convert_string_to_block(self, string):
        value, time, replica, cursor = string.split('<*%*$&:-*&#$(!-!>')
        return [list(value), datetime.strptime(time, '%m/%d/%y %H:%M:%S.%f'), replica, None if cursor == "None" else int(cursor)]
