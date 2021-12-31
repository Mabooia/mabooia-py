import unittest
from copy import copy

from mabooia.collections.mutable import LinkedList


class LinkedListTest(unittest.TestCase):

    def test_empty(self):
        # given
        ll = LinkedList()

        # then
        self.assertTrue(ll.is_empty)
        self.assertEqual(0, len(ll))
        self.assertEqual("[]", str(ll))
        self.assertTrue(ll[1:].is_empty)
        self.assertRaises(IndexError, lambda: ll[0])
        self.assertRaises(IndexError, lambda: ll[1])
        self.assertRaises(IndexError, lambda: ll[-1])
        self.assertFalse("any" in ll)
        self.assertTrue(copy(ll).is_empty)
        self.assertTrue((ll + ll).is_empty)
        self.assertTrue((ll * 2).is_empty)
        self.assertEqual(-1, ll.index_of("any"))
        self.assertEqual(0, ll.count_of("any"))

    def test_add(self):
        # given
        ll = LinkedList([1, 2, 3])
        other = LinkedList([4, 5, 6])

        # when
        res = ll + other

        # then
        self.assertEqual(6, len(res))
        self.assertEqual(1, res[0])
        self.assertEqual(2, res[1])
        self.assertEqual(3, res[2])
        self.assertEqual(4, res[3])
        self.assertEqual(5, res[4])
        self.assertEqual(6, res[5])

    def test_mul(self):
        # given
        ll = LinkedList([1, 2, 3])

        # when
        res = ll * 2

        # then
        self.assertEqual(6, len(res))
        self.assertEqual(1, res[0])
        self.assertEqual(2, res[1])
        self.assertEqual(3, res[2])
        self.assertEqual(1, res[3])
        self.assertEqual(2, res[4])
        self.assertEqual(3, res[5])

    def test_get_item(self):
        # given
        ll = LinkedList([1, 2, 3, 4, 5])

        # then
        self.assertEqual(1, ll[0])
        self.assertEqual(2, ll[1])
        self.assertEqual(3, ll[2])
        self.assertEqual(4, ll[3])
        self.assertEqual(5, ll[4])
        self.assertRaises(IndexError, lambda: ll[5])
        self.assertEqual(5, ll[-1])
        self.assertEqual(4, ll[-2])
        self.assertEqual(3, ll[-3])
        self.assertEqual(2, ll[-4])
        self.assertEqual(1, ll[-5])
        self.assertRaises(IndexError, lambda: ll[-6])

    def test_set_item(self):
        # given
        new_item = "any"
        ll = LinkedList([1, 2, 3, 4, 5])
        initial_len = len(ll)

        # when
        ll[3] = new_item

        # then
        self.assertEqual(initial_len, len(ll))
        self.assertEqual(1, ll[0])
        self.assertEqual(2, ll[1])
        self.assertEqual(3, ll[2])
        self.assertEqual(new_item, ll[3])
        self.assertEqual(5, ll[4])

    def test_del_item(self):
        # given
        ll = LinkedList([1, 2, 3, 4, 5])

        # when
        del ll[2]

        # then
        self.assertEqual([1, 2, 4, 5], ll.to_list())

    def test_del_slice(self):
        # given
        ll = LinkedList([1, 2, 3, 4, 5])

        # when
        del ll[1:3]

        # then
        self.assertEqual([1, 4, 5], ll.to_list())

    def test_slices(self):
        # given
        ll = LinkedList([1, 2, 3, 4, 5])

        # then
        self.assertEqual([1, 2, 3, 4, 5], ll[:].to_list())
        self.assertEqual([2, 3, 4, 5], ll[1:].to_list())
        self.assertEqual([1, 2, 3, 4], ll[:4].to_list())
        self.assertEqual([2, 3, 4], ll[1:4].to_list())
        self.assertEqual([5], ll[-1:].to_list())
        self.assertEqual([4, 5], ll[-2:].to_list())
        self.assertEqual([4], ll[-2:-1].to_list())
        self.assertEqual([5, 4, 3, 2, 1], ll[::-1].to_list())

    def test_contains(self):
        # given
        ll = LinkedList([1, 2, 3, 4, 3, 5])

        # then
        self.assertTrue(5 in ll)
        self.assertTrue(3 in ll)
        self.assertFalse(7 in ll)

    def test_count_of(self):
        # given
        ll = LinkedList([1, 2, 3, 4, 3, 5])

        # then
        self.assertEqual(1, ll.count_of(4))
        self.assertEqual(2, ll.count_of(3))
        self.assertEqual(0, ll.count_of(7))

    def test_append(self):
        # given
        new_item = "any"
        ll = LinkedList()
        initial_len = len(ll)

        # when
        ll.append(new_item)

        # then
        self.assertEqual(initial_len + 1, len(ll))
        self.assertIs(new_item, ll[-1])

    def test_prepend(self):
        # given
        new_item = "any"
        ll = LinkedList()
        initial_len = len(ll)

        # when
        ll.prepend(new_item)

        # then
        self.assertEqual(initial_len + 1, len(ll))
        self.assertIs(new_item, ll[0])

    def test_remove(self):
        # given
        ll = LinkedList([1, 2, 3, 4, 5, 3])

        # when
        ll.remove(3)
        ll.remove(7)

        # then
        self.assertEqual([1, 2, 4, 5, 3], ll.to_list())

    def test_remove_first(self):
        # given
        ll = LinkedList([1, 2, 3, 4, 5])

        # when
        ll.remove_first()

        # then
        self.assertEqual([2, 3, 4, 5], ll.to_list())

    def test_remove_last(self):
        # given
        ll = LinkedList([1, 2, 3, 4, 5])

        # when
        ll.remove_last()

        # then
        self.assertEqual([1, 2, 3, 4], ll.to_list())

    def test_to_list(self):
        # given
        ll = LinkedList([1, 2, 3, 4, 5])

        # then
        self.assertEqual([1, 2, 3, 4, 5], ll.to_list())


if __name__ == '__main__':
    unittest.main()
