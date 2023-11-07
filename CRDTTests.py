import unittest
from CRDT_structure import CRDTDocument


class CRDTTests(unittest.TestCase):
    def setUp(self):
        self.user1 = CRDTDocument('user1', ['user1', 'user2'])
        self.user2 = CRDTDocument('user2', ['user1', 'user2'])

    def test_sequential_typing(self):
        # Пользователь 1 пишет "hello"
        for ch in "hello":
            self.user1.local_insert(ch, len(self.user1.text))

        # Пользователь 2 пишет "world"
        for ch in "world":
            self.user2.local_insert(ch, len(self.user2.text))

        # Синхронизация документов
        for op in self.user1.history:
            self.user2.integrate_operation(op)

        for op in self.user2.history:
            self.user1.integrate_operation(op)

        # Ожидаемый результат: "helloworld"
        self.assertEqual(str(self.user1), "helloworld")
        self.assertEqual(str(self.user2), "helloworld")

    def test_simultaneous_typing_at_start(self):
        # Пользователи одновременно вставляют символ в начало
        self.user1.local_insert('A', 0)
        self.user2.local_insert('B', 0)

        # Синхронизация документов
        for op in self.user1.history:
            self.user2.integrate_operation(op)

        for op in self.user2.history:
            self.user1.integrate_operation(op)

        # Результат зависит от реализации, но символы должны упорядочиться в соответствии с их идентификаторами
        self.assertTrue(str(self.user1) == "AB" or str(self.user1) == "BA")
        self.assertEqual(str(self.user1), str(self.user2))

    def test_simultaneous_typing_in_middle_of_text(self):
        # Пользователь 1 пишет "hello"
        for ch in "hello":
            self.user1.local_insert(ch, len(self.user1.text))

        # Синхронизация документов
        for op in self.user1.history:
            self.user2.integrate_operation(op)

        # Пользователи одновременно вставляют символ в середину слова "hello"
        self.user1.local_insert('A', 2)  # "heAllo"
        self.user2.local_insert('B', 2)  # "heBllo"

        # Синхронизация документов
        for op in self.user1.history[-1:]:
            self.user2.integrate_operation(op)

        for op in self.user2.history[-1:]:
            self.user1.integrate_operation(op)

        # Результат зависит от реализации, но символы должны упорядочиться
        expected_results = ["heABllo", "heBAllo"]
        self.assertIn(str(self.user1), expected_results)
        self.assertEqual(str(self.user1), str(self.user2))


if __name__ == '__main__':
    unittest.main()
