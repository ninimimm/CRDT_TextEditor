import unittest
from Converter import Converter
from datetime import datetime
from unittest.mock import patch
from CRDT_structure import CRDT, Block, Range


class TestConverter(unittest.TestCase):  # pragma: no cover
    def __init__(self, *args, **kwargs):
        super(TestConverter, self).__init__(*args, **kwargs)
        self.crdt = CRDT("replica1")
        self.converter = Converter(self.crdt.replica_id)
        self.based_block1 = Block(value=["к", "о", "ш", "к", "а"], replica=self.crdt.replica_id,
                                 cursor=5, Range=Range(start=0, finish=5), time=datetime.now(),
                                 hash=0)

        self.based_block2 = Block(value=["м", "ы", "ш", "к", "а"], replica=self.crdt.replica_id,
                                 cursor=5, Range=Range(start=0, finish=5), time=datetime.now(),
                                 hash=1)

    def test_converter_empty(self):  # pragma: no cover
        with patch.object(Block, '__eq__', self.based_block1.custom_eq):
            self.assertEqual(self.crdt.copy(),
                self.converter.convert_string_to_crdt(
                    self.converter.convert_crdt_to_str(self.crdt.blocks.copy())))

    def test_converter(self):  # pragma: no cover
        with patch.object(Block, '__eq__', self.based_block1.custom_eq):
            self.crdt.cursor_insert(0, self.based_block1.value)
            self.crdt.cursor_insert(5, self.based_block2.value)
            self.assertEqual(self.crdt.copy(),
                self.converter.convert_string_to_crdt(
                    self.converter.convert_crdt_to_str(self.crdt.blocks.copy())))


if __name__ == '__main__':  # pragma: no cover
    unittest.main()