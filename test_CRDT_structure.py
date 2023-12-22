import unittest
import time
from datetime import datetime
from unittest.mock import patch
from CRDT_structure import CRDT, Block, Range


class TestCRDTStructure(unittest.TestCase):  # pragma: no cover
    def __init__(self, *args, **kwargs):
        super(TestCRDTStructure, self).__init__(*args, **kwargs)
        self.crdt = CRDT("replica1")
        self.based_block = Block(value=["к", "о", "ш", "к", "а"], replica=self.crdt.replica_id,
                                 cursor=5, Range=Range(start=0, finish=5), time=datetime.now(),
                                 hash=0)

    def reset_crdt(self):  # pragma: no cover
        self.crdt = CRDT("replica1")

    def test_append(self):  # pragma: no cover
        with patch.object(Block, '__eq__', self.based_block.custom_eq):
            self.crdt.append(self.based_block, len(self.based_block.value))
            self.assertEqual(len(self.crdt.blocks), 1)
            self.assertEqual(len(self.crdt.lens_of_blocks), 1)
            self.assertEqual(self.crdt.blocks[0], self.based_block.copy())
            self.assertEqual(self.crdt.lens_of_blocks[0], 5)
            self.reset_crdt()

    def test_insert(self):  # pragma: no cover
        for i in range(100):
            self.assertEqual(self.crdt.current_hash, i)
            self.crdt.insert(i, value=["к", "о", "ш", "к", "а"], replica=self.crdt.replica_id,
                                cursor=5, range=Range(start=0, finish=5), hash=self.crdt.current_hash,
                                time=datetime.now())
            self.assertEqual(self.crdt.current_hash, i + 1)
            self.assertEqual(self.crdt.lens_of_blocks[i], 5)
        self.reset_crdt()

    def test_remove(self):  # pragma: no cover
        for i in range(50):
            self.crdt.insert(i, value=["к", "о", "ш", "к", "а", "1", "1"], replica=self.crdt.replica_id,
                                cursor=6, range=Range(start=0, finish=6), hash=self.crdt.current_hash,
                                time=datetime.now())
        self.crdt.insert(50, value=["к", "о", "ш", "к", "а"], replica=self.crdt.replica_id,
                         cursor=6, range=Range(start=0, finish=6), hash=self.crdt.current_hash,
                         time=datetime.now())
        for i in range(1, 50):
            self.crdt.insert(50 + i, value=["к", "о", "ш", "к", "а", "2"], replica=self.crdt.replica_id,
                                cursor=6, range=Range(start=0, finish=6), hash=self.crdt.current_hash,
                                time=datetime.now())
        self.crdt.remove(50)
        self.assertEqual(self.crdt.blocks[49].value, ["к", "о", "ш", "к", "а", "1", "1"])
        self.assertEqual(self.crdt.blocks[50].value, ["к", "о", "ш", "к", "а", "2"])
        self.assertEqual(self.crdt.lens_of_blocks[49], 7)
        self.assertEqual(self.crdt.lens_of_blocks[50], 6)
        self.reset_crdt()

    def test_cursor_to_index(self):  # pragma: no cover
        self.crdt.insert(0, value=["к"], replica=self.crdt.replica_id,
                         cursor=1, range=Range(start=0, finish=6), hash=self.crdt.current_hash,
                         time=datetime.now())
        self.crdt.insert(1, value=["ш", "к", "а", "1", "1"], replica=self.crdt.replica_id,
                         cursor=5, range=Range(start=0, finish=6), hash=self.crdt.current_hash,
                         time=datetime.now())
        self.crdt.insert(2, value=["к", "о", "ш", "к", "а", "1", "1"], replica=self.crdt.replica_id,
                         cursor=7, range=Range(start=0, finish=6), hash=self.crdt.current_hash,
                         time=datetime.now())
        self.assertEqual(self.crdt.cursor_to_index(0, self.crdt.blocks, self.crdt.lens_of_blocks), (0, 0))
        self.assertEqual(self.crdt.cursor_to_index(1, self.crdt.blocks, self.crdt.lens_of_blocks), (0, 1))
        self.assertEqual(self.crdt.cursor_to_index(2, self.crdt.blocks, self.crdt.lens_of_blocks), (1, 1))
        self.assertEqual(self.crdt.cursor_to_index(6, self.crdt.blocks, self.crdt.lens_of_blocks), (1, 5))
        self.assertEqual(self.crdt.cursor_to_index(7, self.crdt.blocks, self.crdt.lens_of_blocks), (2, 1))
        self.assertEqual(self.crdt.cursor_to_index(10, self.crdt.blocks, self.crdt.lens_of_blocks), (2, 4))
        self.reset_crdt()

    def test_cursor_to_index_end_blocks(self):  # pragma: no cover
        self.crdt.insert(0, value=["к"], replica=self.crdt.replica_id,
                         cursor=1, range=Range(start=0, finish=6), hash=self.crdt.current_hash,
                         time=datetime.now())
        self.crdt.insert(1, value=["ш", "к", "а", "1", "1"], replica=self.crdt.replica_id,
                         cursor=5, range=Range(start=0, finish=6), hash=self.crdt.current_hash,
                         time=datetime.now())
        self.crdt.insert(2, value=["к", "о", "ш", "к", "а", "1", "1"], replica=self.crdt.replica_id,
                         cursor=7, range=Range(start=0, finish=6), hash=self.crdt.current_hash,
                         time=datetime.now())
        self.assertEqual(self.crdt.cursor_to_index(14, self.crdt.blocks, self.crdt.lens_of_blocks), (2, 7))
        self.reset_crdt()

    def test_cursor_insert_beginning(self):  # pragma: no cover
        self.crdt.insert(0, value=["к"], replica=self.crdt.replica_id,
                         cursor=1, range=Range(start=0, finish=6), hash=self.crdt.current_hash,
                         time=datetime.now())
        self.crdt.insert(1, value=["ш", "к", "а", "1", "1"], replica=self.crdt.replica_id,
                         cursor=5, range=Range(start=0, finish=6), hash=self.crdt.current_hash,
                         time=datetime.now())
        self.crdt.cursor_insert(0, ["ж", "о", "п", "a"])
        self.assertEqual(len(self.crdt.blocks), 3)
        self.assertEqual(self.crdt.blocks[0].value, ["ж", "о", "п", "a"])
        self.assertEqual(self.crdt.blocks[0].cursor, 4)
        self.assertEqual(self.crdt.blocks[1].value, ["к"])
        self.assertEqual(self.crdt.blocks[1].cursor, 1)
        self.assertEqual(self.crdt.blocks[2].value, ["ш", "к", "а", "1", "1"])
        self.reset_crdt()

    def test_cursor_insert_between_blocks(self):  # pragma: no cover
        self.crdt.insert(0, value=["к"], replica=self.crdt.replica_id,
                         cursor=1, range=Range(start=0, finish=6), hash=self.crdt.current_hash,
                         time=datetime.now())
        self.crdt.insert(1, value=["ш", "к", "а", "1", "1"], replica=self.crdt.replica_id,
                         cursor=5, range=Range(start=0, finish=6), hash=self.crdt.current_hash,
                         time=datetime.now())
        self.crdt.cursor_insert(1, ["ж", "о", "п", "a"])
        self.assertEqual(len(self.crdt.blocks), 3)
        self.assertEqual(self.crdt.blocks[0].value, ["к"])
        self.assertEqual(self.crdt.blocks[1].value, ["ж", "о", "п", "a"])
        self.assertEqual(self.crdt.blocks[1].cursor, 4)
        self.assertEqual(self.crdt.blocks[2].value, ["ш", "к", "а", "1", "1"])
        self.reset_crdt()

    def test_cursor_insert_inside_blocks(self):  # pragma: no cover
        self.crdt.insert(0, value=["к"], replica=self.crdt.replica_id,
                         cursor=1, range=Range(start=0, finish=6), hash=self.crdt.current_hash,
                         time=datetime.now())
        self.crdt.insert(1, value=["ш", "к", "а", "1", "1"], replica=self.crdt.replica_id,
                         cursor=5, range=Range(start=0, finish=6), hash=self.crdt.current_hash,
                         time=datetime.now())
        self.crdt.cursor_insert(3, ["ж", "о", "п", "a"])
        self.assertEqual(len(self.crdt.blocks), 4)
        self.assertEqual(self.crdt.blocks[0].value, ["к"])
        self.assertEqual(self.crdt.blocks[1].value, ["ш", "к"])
        self.assertEqual(self.crdt.blocks[2].value, ["ж", "о", "п", "a"])
        self.assertEqual(self.crdt.blocks[2].cursor, 4)
        self.assertEqual(self.crdt.blocks[3].value, ["а", "1", "1"])
        self.reset_crdt()

    def test_cursor_insert_end(self):  # pragma: no cover
        self.crdt.insert(0, value=["к"], replica=self.crdt.replica_id,
                         cursor=1, range=Range(start=0, finish=6), hash=self.crdt.current_hash,
                         time=datetime.now())
        self.crdt.insert(1, value=["ш", "к", "а", "1", "1"], replica=self.crdt.replica_id,
                         cursor=5, range=Range(start=0, finish=6), hash=self.crdt.current_hash,
                         time=datetime.now())
        self.crdt.cursor_insert(6, ["ж", "о", "п", "a"])
        self.assertEqual(len(self.crdt.blocks), 3)
        self.assertEqual(self.crdt.blocks[0].value, ["к"])
        self.assertEqual(self.crdt.blocks[1].value, ["ш", "к", "а", "1", "1"])
        self.assertEqual(self.crdt.blocks[2].value, ["ж", "о", "п", "a"])
        self.reset_crdt()

    def test_cursor_insert_empty(self):  # pragma: no cover
        self.crdt.cursor_insert(0, ["ж", "о", "п", "a"])
        self.assertEqual(len(self.crdt.blocks), 1)
        self.assertEqual(self.crdt.blocks[0].value, ["ж", "о", "п", "a"])
        self.reset_crdt()

    def test_cursor_remove_end_block(self):  # pragma: no cover
        self.crdt.cursor_insert(0, ["ж", "о", "п", "a"])
        self.crdt.cursor_remove(4)
        self.assertEqual(len(self.crdt.blocks), 1)
        self.assertEqual(self.crdt.blocks[0].value, ["ж", "о", "п"])
        self.reset_crdt()

    def test_cursor_remove_in_block(self):  # pragma: no cover
        self.crdt.cursor_insert(0, ["ж", "о", "п", "а"])
        time.sleep(1)
        self.crdt.cursor_remove(2)
        self.assertEqual(len(self.crdt.blocks), 2)
        self.assertEqual(self.crdt.blocks[0].value, ["ж"])
        self.assertEqual(self.crdt.blocks[1].value, ["п", "а"])
        self.assertLess(self.crdt.blocks[1].time, self.crdt.blocks[0].time)
        self.reset_crdt()

    def test_cursor_remove_empty(self):  # pragma: no cover
        self.crdt.cursor_remove(0)
        self.assertEqual(len(self.crdt.blocks), 0)
        self.reset_crdt()

    def test_cursor_remove_block(self):  # pragma: no cover
        self.crdt.cursor_insert(0, ["ж"])
        self.crdt.cursor_remove(1)
        self.assertEqual(len(self.crdt.blocks), 0)
        self.reset_crdt()

    def test_add_string(self):  # pragma: no cover
        self.crdt.cursor_insert(0, ["ж"])
        self.crdt.add_string(1, "чушпан")
        self.assertEqual(len(self.crdt.blocks), 1)
        self.assertEqual(self.crdt.blocks[0].value, ["ж", "ч", "у", "ш", "п", "а", "н"])
        self.assertEqual(self.crdt.blocks[0].Range.finish, 7)
        self.assertEqual(self.crdt.lens_of_blocks[0], 7)

    def test_add_string_empty(self):  # pragma: no cover
        self.crdt.add_string(0, "чушпан")
        self.assertEqual(len(self.crdt.blocks), 1)
        self.assertEqual(self.crdt.blocks[0].value, ["ч", "у", "ш", "п", "а", "н"])
        self.assertEqual(self.crdt.blocks[0].Range.finish, 6)
        self.assertEqual(self.crdt.lens_of_blocks[0], 6)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()