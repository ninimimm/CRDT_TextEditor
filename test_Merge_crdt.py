import unittest
import copy
from datetime import datetime
from unittest.mock import patch
from CRDT_structure import CRDT, Block, Range
from Merge_crdt import Merge


class TestMergeCRDT(unittest.TestCase):  # pragma: no cover
    def __init__(self, *args, **kwargs):
        super(TestMergeCRDT, self).__init__(*args, **kwargs)
        self.merge = Merge()
        self.crdt = CRDT("replica1")
        self.based_block = Block(value=["к", "о", "ш", "к", "а"], replica=self.crdt.replica_id,
                                 cursor=5, Range=Range(start=0, finish=5), time=datetime.now(),
                                 hash=0)
    
    def reset_server(self):
        self.merge.server_blocks = []
        
    def reset_crdt(self):  # pragma: no cover
        self.crdt = CRDT("replica1")

    def test_empty_on_server(self):
        block = Block(value=["к"], replica=self.crdt.replica_id,
                                 cursor=1, Range=Range(start=0, finish=1), time=datetime.now(),
                                 hash=0)
        self.crdt.append(block, len(block.value))
        self.merge.merge(self.crdt)
        with patch.object(Block, '__eq__', self.based_block.custom_eq):
            self.assertEqual(self.crdt.blocks, self.merge.server_blocks)
        self.assertEqual(len(self.merge.server_blocks), 1)
        self.assertEqual(self.merge.server_blocks[0].value, ["к"])
        self.assertEqual(self.merge.server_blocks[0].replica, "replica1")
        self.assertEqual(self.merge.server_blocks[0].Range, Range(start=0, finish=1))
        self.reset_server()
        self.reset_crdt()

    def test_our_replica_change(self):
        block1 = Block(value=["к"], replica=self.crdt.replica_id,
                      cursor=1, Range=Range(start=0, finish=1), time=datetime.now(),
                      hash=0)
        block2 = Block(value=["к", "a"], replica=self.crdt.replica_id,
                      cursor=2, Range=Range(start=0, finish=2), time=datetime.now(),
                      hash=0)
        self.crdt.append(block1, len(block1.value))
        self.merge.merge(self.crdt.copy())
        self.reset_crdt()
        self.crdt.append(block2, len(block2.value))
        self.merge.merge(self.crdt)
        with patch.object(Block, '__eq__', self.based_block.custom_eq):
            self.assertEqual(self.crdt.blocks, self.merge.server_blocks)
        self.assertEqual(len(self.merge.server_blocks), 1)
        self.assertEqual(self.merge.server_blocks[0].value, ["к", "a"])
        self.assertEqual(self.merge.server_blocks[0].replica, "replica1")
        self.assertEqual(self.merge.server_blocks[0].Range, Range(start=0, finish=2))
        self.reset_server()
        self.reset_crdt()

    def test_other_replica(self):
        block1 = Block(value=["к"], replica=self.crdt.replica_id,
                      cursor=1, Range=Range(start=0, finish=1), time=datetime.now(),
                      hash=0)
        block2 = Block(value=["к", "a"], replica="replica2",
                      cursor=2, Range=Range(start=0, finish=2), time=datetime.now(),
                      hash=1000000000)
        self.crdt.append(block1, len(block1.value))
        self.merge.merge(self.crdt.copy())
        self.reset_crdt()
        self.crdt.append(block2, len(block2.value))
        self.merge.merge(self.crdt)
        with patch.object(Block, '__eq__', self.based_block.custom_eq):
            self.assertEqual(self.crdt.blocks, self.merge.server_blocks)
        self.assertEqual(len(self.merge.server_blocks), 2)
        self.assertEqual(self.merge.server_blocks[0].value, ["к"])
        self.assertEqual(self.merge.server_blocks[1].value, ["к", "a"])
        self.assertEqual(self.merge.server_blocks[0].replica, "replica1")
        self.assertEqual(self.merge.server_blocks[1].replica, "replica2")
        self.assertEqual(self.merge.server_blocks[0].Range, Range(start=0, finish=1))
        self.assertEqual(self.merge.server_blocks[1].Range, Range(start=0, finish=2))
        self.reset_server()
        self.reset_crdt()

    def test_add_block_in_end(self):
        block1 = Block(value=["к"], replica=self.crdt.replica_id,
                       cursor=1, Range=Range(start=0, finish=1), time=datetime.now(),
                       hash=0)
        block2 = Block(value=["к", "a"], replica=self.crdt.replica_id,
                       cursor=2, Range=Range(start=0, finish=2), time=datetime.now(),
                       hash=1)
        block3 = Block(value=["ш", "у", "р", "у", "п"], replica=self.crdt.replica_id,
                       cursor=5, Range=Range(start=0, finish=5), time=datetime.now(),
                       hash=2)
        self.crdt.append(block1, len(block1.value))
        self.crdt.append(block2, len(block2.value))
        self.crdt.append(block3, len(block2.value))
        self.merge.merge(self.crdt.copy())
        block4 = Block(value=["м", "а", "р", "т", "ы", "ш", "к", "а"], replica="replica2",
                       cursor=8, Range=Range(start=0, finish=8), time=datetime.now(),
                       hash=10000000)
        for block in self.crdt.blocks:
            block.replica = None
        self.crdt.append(block4, len(block1.value))
        self.merge.merge(self.crdt)
        with patch.object(Block, '__eq__', self.based_block.custom_eq):
            self.assertEqual(self.crdt.blocks, self.merge.server_blocks)
        self.assertEqual(len(self.merge.server_blocks), 4)
        self.assertEqual(self.merge.server_blocks[0].value, ["к"])
        self.assertEqual(self.merge.server_blocks[1].value, ["к", "a"])
        self.assertEqual(self.merge.server_blocks[2].value, ["ш", "у", "р", "у", "п"])
        self.assertEqual(self.merge.server_blocks[3].value, ["м", "а", "р", "т", "ы", "ш", "к", "а"])
        self.assertEqual(self.crdt.blocks[3].replica, "replica2")
        self.assertEqual(self.merge.server_blocks[0].Range, Range(start=0, finish=1))
        self.assertEqual(self.merge.server_blocks[1].Range, Range(start=0, finish=2))
        self.assertEqual(self.merge.server_blocks[2].Range, Range(start=0, finish=5))
        self.assertEqual(self.merge.server_blocks[3].Range, Range(start=0, finish=8))
        self.reset_server()
        self.reset_crdt()

    def test_add_block_between(self):
        block1 = Block(value=["к"], replica=self.crdt.replica_id,
                       cursor=1, Range=Range(start=0, finish=1), time=datetime.now(),
                       hash=0)
        block2 = Block(value=["к", "a"], replica=self.crdt.replica_id,
                       cursor=2, Range=Range(start=0, finish=2), time=datetime.now(),
                       hash=1)
        block3 = Block(value=["ш", "у", "р", "у", "п"], replica=self.crdt.replica_id,
                       cursor=5, Range=Range(start=0, finish=5), time=datetime.now(),
                       hash=2)
        self.crdt.append(block1, len(block1.value))
        self.crdt.append(block2, len(block2.value))
        self.crdt.append(block3, len(block2.value))
        self.merge.merge(self.crdt.copy())
        for block in self.crdt.blocks:
            block.replica = None
        self.crdt.replica_id = "replica2"
        self.crdt.current_hash = 100000000
        self.crdt.cursor_insert(3, ["м", "а", "р", "т", "ы", "ш", "к", "а"])
        self.merge.merge(self.crdt)
        with patch.object(Block, '__eq__', self.based_block.custom_eq):
            self.assertEqual(self.crdt.blocks, self.merge.server_blocks)
        self.assertEqual(len(self.merge.server_blocks), 4)
        self.assertEqual(self.merge.server_blocks[0].value, ["к"])
        self.assertEqual(self.merge.server_blocks[1].value, ["к", "a"])
        self.assertEqual(self.merge.server_blocks[2].value, ["м", "а", "р", "т", "ы", "ш", "к", "а"])
        self.assertEqual(self.merge.server_blocks[3].value, ["ш", "у", "р", "у", "п"])
        self.assertEqual(self.crdt.blocks[2].replica, "replica2")
        self.assertEqual(self.merge.server_blocks[0].Range, Range(start=0, finish=1))
        self.assertEqual(self.merge.server_blocks[1].Range, Range(start=0, finish=2))
        self.assertEqual(self.merge.server_blocks[2].Range, Range(start=0, finish=8))
        self.assertEqual(self.merge.server_blocks[3].Range, Range(start=0, finish=5))
        self.reset_server()
        self.reset_crdt()

    def test_three_users(self):
        block1 = Block(value=["к"], replica="replica1",
                       cursor=1, Range=Range(start=0, finish=1), time=datetime.now(),
                       hash=0)
        block2 = Block(value=["к", "о", "ш", "к", "а"], replica="replica3",
                       cursor=5, Range=Range(start=0, finish=5), time=datetime.now(),
                       hash=1000000000)
        block3 = Block(value=["ш", "у", "р", "у", "п"], replica="replica1",
                       cursor=5, Range=Range(start=0, finish=5), time=datetime.now(),
                       hash=1)
        self.crdt.append(block1.copy(), len(block1.value))
        self.crdt.append(block2.copy(), len(block2.value))
        self.crdt.append(block3.copy(), len(block3.value))
        self.merge.merge(self.crdt.copy())
        self.crdt.current_hash = 1
        for block in self.crdt.blocks:
            block.replica = None
        self.crdt.cursor_insert(3, ["1"])
        self.merge.merge(self.crdt.copy())
        self.reset_crdt()
        self.crdt.append(block1.copy(), len(block1.value))
        self.crdt.append(block2.copy(), len(block2.value))
        self.crdt.append(block3.copy(), len(block3.value))
        self.crdt.replica_id = "replica2"
        self.crdt.current_hash = 2000000000
        for block in self.crdt.blocks:
            block.replica = None
        self.crdt.cursor_insert(4, ["6"])
        self.merge.merge(self.crdt)
        with patch.object(Block, '__eq__', self.based_block.custom_eq):
            self.assertEqual(self.crdt.blocks, self.merge.server_blocks)
        self.assertEqual(len(self.merge.server_blocks), 7)
        self.assertEqual(self.merge.server_blocks[0].value, ["к"])
        self.assertEqual(self.merge.server_blocks[1].value, ["к", "о"])
        self.assertEqual(self.merge.server_blocks[2].value, ["1"])
        self.assertEqual(self.merge.server_blocks[3].value, ["ш"])
        self.assertEqual(self.merge.server_blocks[4].value, ["6"])
        self.assertEqual(self.merge.server_blocks[5].value, ["к", "а"])
        self.assertEqual(self.merge.server_blocks[6].value, ["ш", "у", "р", "у", "п"])
        self.assertEqual(self.crdt.blocks[1].replica, "replica1")
        self.assertEqual(self.crdt.blocks[2].replica, "replica1")
        self.assertEqual(self.crdt.blocks[3].replica, "replica2")
        self.assertEqual(self.crdt.blocks[4].replica, "replica2")
        self.assertEqual(self.crdt.blocks[5].replica, "replica2")
        self.assertEqual(self.merge.server_blocks[0].Range, Range(start=0, finish=1))
        self.assertEqual(self.merge.server_blocks[1].Range, Range(start=0, finish=2))
        self.assertEqual(self.merge.server_blocks[2].Range, Range(start=0, finish=1))
        self.assertEqual(self.merge.server_blocks[3].Range, Range(start=2, finish=3))
        self.assertEqual(self.merge.server_blocks[4].Range, Range(start=0, finish=1))
        self.assertEqual(self.merge.server_blocks[5].Range, Range(start=3, finish=5))
        self.assertEqual(self.merge.server_blocks[6].Range, Range(start=0, finish=5))
        self.reset_server()
        self.reset_crdt()

    def test_change_our_inside_block(self):
        block1 = Block(value=["к"], replica=self.crdt.replica_id,
                       cursor=1, Range=Range(start=0, finish=1), time=datetime.now(),
                       hash=0)
        block2 = Block(value=["к", "а"], replica=self.crdt.replica_id,
                       cursor=2, Range=Range(start=0, finish=2), time=datetime.now(),
                       hash=1)
        block3 = Block(value=["ш", "у", "р", "у", "п"], replica=self.crdt.replica_id,
                       cursor=5, Range=Range(start=0, finish=5), time=datetime.now(),
                       hash=2)
        self.crdt.append(block1.copy(), len(block1.value))
        self.crdt.append(block2.copy(), len(block2.value))
        self.crdt.append(block3.copy(), len(block3.value))
        self.merge.merge(self.crdt.copy())
        self.crdt.add_string(3, "кашка")
        self.merge.merge(self.crdt)
        self.assertEqual(self.merge.server_blocks[0].value, ["к"])
        self.assertEqual(self.merge.server_blocks[1].value, ["к", "а", "к", "а", "ш", "к", "а"])
        self.assertEqual(self.merge.server_blocks[2].value, ["ш", "у", "р", "у", "п"])
        self.assertEqual(self.merge.server_blocks[1].cursor, 7)
        self.assertEqual(self.merge.server_blocks[1].Range, Range(start=0, finish=7))
        self.assertEqual(self.merge.server_blocks[1].replica, "replica1")

    def test_text_in_server_new_our_block(self):
        block1 = Block(value=["1"], replica="replica1",
                       cursor=1, Range=Range(start=0, finish=1), time=datetime.now(),
                       hash=0)
        block2 = Block(value=["к"], replica="replica1",
                       cursor=1, Range=Range(start=0, finish=1), time=datetime.now(),
                       hash=1)
        block3 = Block(value=["2"], replica="replica1",
                       cursor=5, Range=Range(start=0, finish=1), time=datetime.now(),
                       hash=2)
        self.crdt.append(block1.copy(), len(block1.value))
        self.crdt.append(block2.copy(), len(block2.value))
        self.crdt.append(block3.copy(), len(block3.value))
        self.merge.merge(self.crdt.copy())
        self.reset_crdt()
        block4 = Block(value=["к"], replica="replica2",
                       cursor=1, Range=Range(start=0, finish=1), time=datetime.now(),
                       hash=1000000000)
        self.crdt.append(block4.copy(), len(block4.value))
        self.merge.merge(self.crdt)
        with patch.object(Block, '__eq__', self.based_block.custom_eq):
            self.assertEqual(self.crdt.blocks, self.merge.server_blocks)
        self.assertEqual(len(self.merge.server_blocks), 4)
        self.assertEqual(self.merge.server_blocks[0].value, ["1"])
        self.assertEqual(self.merge.server_blocks[1].value, ["к"])
        self.assertEqual(self.merge.server_blocks[2].value, ["2"])
        self.assertEqual(self.merge.server_blocks[3].value, ["к"])
        self.assertEqual(self.merge.server_blocks[0].replica, "replica1")
        self.assertEqual(self.merge.server_blocks[1].replica, "replica1")
        self.assertEqual(self.merge.server_blocks[2].replica, "replica1")
        self.assertEqual(self.merge.server_blocks[3].replica, "replica2")

    def test_replace_inside(self):
        block1 = Block(value=["1"], replica="replica1",
                       cursor=1, Range=Range(start=0, finish=1), time=datetime.now(),
                       hash=0)
        block2 = Block(value=["к"], replica="replica1",
                       cursor=1, Range=Range(start=0, finish=1), time=datetime.now(),
                       hash=1)
        block3 = Block(value=["2"], replica="replica1",
                       cursor=5, Range=Range(start=0, finish=1), time=datetime.now(),
                       hash=2)
        self.crdt.append(block1.copy(), len(block1.value))
        self.crdt.append(block2.copy(), len(block2.value))
        self.crdt.append(block3.copy(), len(block3.value))
        self.merge.merge(self.crdt.copy())
        self.reset_crdt()
        block2.replica = "replica2"
        block2.hash = 1000000000
        block1.replica = None
        block3.replica = None
        self.crdt.append(block1.copy(), len(block1.value))
        self.crdt.append(block2.copy(), len(block2.value))
        self.crdt.append(block3.copy(), len(block3.value))
        self.merge.merge(self.crdt)
        with patch.object(Block, '__eq__', self.based_block.custom_eq):
            self.assertEqual(self.crdt.blocks, self.merge.server_blocks)
        self.assertEqual(len(self.merge.server_blocks), 4)
        self.assertEqual(self.merge.server_blocks[0].value, ["1"])
        self.assertEqual(self.merge.server_blocks[1].value, ["к"])
        self.assertEqual(self.merge.server_blocks[2].value, ["к"])
        self.assertEqual(self.merge.server_blocks[3].value, ["2"])
        self.assertEqual(self.merge.server_blocks[0].replica, "replica1")
        self.assertEqual(self.merge.server_blocks[1].replica, "replica1")
        self.assertEqual(self.merge.server_blocks[2].replica, "replica2")
        self.assertEqual(self.merge.server_blocks[3].replica, "replica1")

    def test_remove_end_and_include_inside(self):
        block1 = Block(value=["1"], replica="replica1",
                       cursor=1, Range=Range(start=0, finish=1), time=datetime.now(),
                       hash=10)
        block2 = Block(value=["к"], replica="replica1",
                       cursor=1, Range=Range(start=0, finish=1), time=datetime.now(),
                       hash=11)
        block3 = Block(value=["м", "а", "ш", "и", "н", "а"], replica="replica1",
                       cursor=6, Range=Range(start=0, finish=6), time=datetime.now(),
                       hash=12)
        block4 = Block(value=["2"], replica="replica1",
                       cursor=1, Range=Range(start=0, finish=1), time=datetime.now(),
                       hash=111)
        self.crdt.append(block1.copy(), len(block1.value))
        self.crdt.append(block2.copy(), len(block2.value))
        self.crdt.append(block3.copy(), len(block3.value))
        self.crdt.append(block4.copy(), len(block4.value))
        self.merge.merge(self.crdt.copy())
        for block in self.crdt.blocks:
            block.replica = None
        self.crdt.cursor_remove(2)
        self.crdt.cursor_insert(1, ["н", "о"])
        self.crdt.cursor_remove(9)
        self.crdt.cursor_insert(6, ["1"])
        self.merge.merge(self.crdt)
        with patch.object(Block, '__eq__', self.based_block.custom_eq):
            self.assertEqual(self.crdt.blocks, self.merge.server_blocks)
        self.assertEqual(len(self.merge.server_blocks), 7)
        self.assertEqual(self.merge.server_blocks[0].value, ["1"])
        self.assertEqual(self.merge.server_blocks[1].value, ["н", "о"])
        self.assertEqual(self.merge.server_blocks[1].replica, "replica1")
        self.assertEqual(self.merge.server_blocks[2].replica, "replica1")
        self.assertEqual(self.merge.server_blocks[0].Range, Range(start=0, finish=1))
        self.assertEqual(self.merge.server_blocks[1].Range, Range(start=0, finish=2))
        self.reset_server()
        self.reset_crdt()

    def test_refactor_after_new(self):
        block1 = Block(value=["к", "а"], replica="replica1",
                       cursor=2, Range=Range(start=0, finish=2), time=datetime.now(),
                       hash=0)
        block3 = Block(value=["ш", "у", "р", "у", "п"], replica="replica1",
                       cursor=5, Range=Range(start=0, finish=5), time=datetime.now(),
                       hash=1)
        self.crdt.append(block1.copy(), len(block1.value))
        self.crdt.append(block3.copy(), len(block3.value))
        self.merge.merge(self.crdt.copy())
        for block in self.crdt.blocks:
            block.replica = None
        self.merge.server_blocks.insert(1, Block(value=["1"], replica="replica1",
                       cursor=1, Range=Range(start=0, finish=1), time=datetime.now(),
                       hash=10))
        self.merge.server_blocks.pop(0)
        self.merge.server_blocks.insert(0, Block(value=["к"], replica="replica1",
                       cursor=1, Range=Range(start=0, finish=1), time=datetime.now(),
                       hash=0))
        self.merge.server_blocks.insert(2, Block(value=["а"], replica="replica1",
                       cursor=1, Range=Range(start=1, finish=2), time=datetime.now(),
                       hash=0))
        self.crdt.cursor_insert(1, ["1"])
        self.crdt.cursor_insert(0, ["н", "а"])
        self.merge.merge(self.crdt)
        with patch.object(Block, '__eq__', self.based_block.custom_eq):
            self.assertEqual(self.crdt.blocks, self.merge.server_blocks)
        self.assertEqual(len(self.merge.server_blocks), 5)
        self.assertEqual(self.merge.server_blocks[0].value, ["н", "а"])
        self.assertEqual(self.merge.server_blocks[1].value, ["к"])
        self.assertEqual(self.merge.server_blocks[2].value, ["1"])
        self.assertEqual(self.merge.server_blocks[3].value, ["а"])
        self.assertEqual(self.merge.server_blocks[4].value, ["ш", "у", "р", "у", "п"])
        self.assertEqual(self.crdt.blocks[0].replica, "replica1")
        self.assertEqual(self.crdt.blocks[1].replica, "replica1")
        self.assertEqual(self.crdt.blocks[2].replica, "replica1")
        self.assertEqual(self.merge.server_blocks[0].Range, Range(start=0, finish=2))
        self.assertEqual(self.merge.server_blocks[1].Range, Range(start=0, finish=1))
        self.assertEqual(self.merge.server_blocks[2].Range, Range(start=0, finish=1))
        self.assertEqual(self.merge.server_blocks[3].Range, Range(start=1, finish=2))
        self.assertEqual(self.merge.server_blocks[4].Range, Range(start=0, finish=5))
        self.reset_server()
        self.reset_crdt()

    def test_add_block_end(self):
        block1 = Block(value=["ш", "у", "р", "у", "п"], replica=self.crdt.replica_id,
                       cursor=5, Range=Range(start=0, finish=5), time=datetime.now(),
                       hash=0)
        self.crdt.append(block1, len(block1.value))
        self.merge.merge(self.crdt.copy())
        self.crdt.cursor_remove(5)
        self.merge.merge(self.crdt)
        with patch.object(Block, '__eq__', self.based_block.custom_eq):
            self.assertEqual(self.crdt.blocks, self.merge.server_blocks)
        self.assertEqual(len(self.merge.server_blocks), 1)
        self.assertEqual(self.merge.server_blocks[0].value, ["ш", "у", "р", "у"])
        self.assertEqual(self.crdt.blocks[0].replica, "replica1")
        self.assertEqual(self.merge.server_blocks[0].Range, Range(start=0, finish=4))
        self.reset_server()
        self.reset_crdt()
        

if __name__ == '__main__':  # pragma: no cover
    unittest.main()