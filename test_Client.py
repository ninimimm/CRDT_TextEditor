import unittest
from Converter import Converter
from datetime import datetime
import time
from CRDT_structure import CRDT, Block, Range
from Client import Client, SharedData
from GUI import GUI


class TestClient(unittest.TestCase):  # pragma: no cover
    def __init__(self, *args, **kwargs):
        super(TestClient, self).__init__(*args, **kwargs)
        self.share_date = SharedData()
        self.client = Client()
        self.gui = GUI(self.share_date, self.client)
        self.crdt = CRDT("replica2")
        self.converter = Converter(self.crdt.replica_id)
        self.based_block1 = Block(value=["к", "о", "ш", "к", "а"], replica=self.crdt.replica_id,
                                 cursor=5, Range=Range(start=0, finish=5), time=datetime.now(),
                                 hash=0)
        time.sleep(0.1)
        self.based_block2 = Block(value=["м", "ы", "ш", "к", "а"], replica=self.crdt.replica_id,
                                 cursor=5, Range=Range(start=0, finish=5), time=datetime.now(),
                                 hash=1)
        self.crdt.append(self.based_block1, len(self.based_block1.value))
        self.crdt.append(self.based_block2, len(self.based_block2.value))
        self.client.crdt = self.crdt.copy()

    def test_update_cursor(self):
        self.assertEqual(self.client.update_cursor(0), 10)



if __name__ == '__main__':  # pragma: no cover
    unittest.main()