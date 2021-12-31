import unittest

from mabooia.collections import *


class StackTest(unittest.TestCase):

    def test_empty_stack(self):
        # given
        st = EmptyStack()

        # then
        self.assertIsInstance(st, EmptyStack)
        self.assertTrue(st.is_empty)
        self.assertFalse(st.is_not_empty)
        self.assertEqual(0, len(st))
        self.assertEqual(Nothing(), st.head_option)
        self.assertEqual(EmptyStack(), st.pop())

    def test_lifo(self):
        # given
        ls = [1, 2, 3, 4, 5]
        st = EmptyStack()

        # when
        for it in ls:
            st = st.push(it)

        ls2 = []
        for it in st:
            ls2.append(it)

        # then
        self.assertEqual([5, 4, 3, 2, 1], ls2)

    def test_not_empty_stack(self):
        # given
        ls = [1, 2, 3, 4, 5]
        st = Stack.of(ls)

        # then
        self.assertIsInstance(st, NonEmptyStack)
        self.assertTrue(st.is_not_empty)
        self.assertFalse(st.is_empty)
        self.assertEqual(len(ls), len(st))
        self.assertEqual(ls[-1], st.peek())
        self.assertEqual(Some(st.peek()), st.head_option)

    def test_stack_push(self):
        # given
        new_elem = 0
        st = Stack.of([1, 2, 3, 4, 5])

        # when
        res = st.push(new_elem)

        # then
        self.assertTrue(res.is_not_empty)
        self.assertEqual(len(res), len(st) + 1)
        self.assertEqual(new_elem, res.peek())

    def test_empty_stack_pop(self):
        # given
        st = EmptyStack()

        # when
        res = st.pop()

        # then
        self.assertEqual(st, res)

    def test_non_empty_stack_pop(self):
        # given
        st = Stack.of([1, 2, 3, 4, 5])

        # when
        res = st.pop()

        # then
        self.assertEqual(len(res), len(st) - 1)
        self.assertEqual(st.tail, res)

    def test_empty_stack_str(self):
        self.assertEqual("Stack[]", str(EmptyStack()))

    def test_non_empty_stack_str(self):
        self.assertEqual("Stack[5, 4, 3, 2, 1]", str(Stack.of([1, 2, 3, 4, 5])))


if __name__ == '__main__':
    unittest.main()
