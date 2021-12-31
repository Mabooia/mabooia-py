from typing import *


class LinkedList(Iterable, Sized):

    class _LinkedNode:
        def __init__(self, _info, _prev, _next):
            self.info = _info
            self.prev = _prev
            self.next = _next

        @property
        def is_head(self):
            return self.prev is None

        @property
        def is_rear(self):
            return self.next is None

        def get(self, idx):
            curr = self
            if idx > 0:
                while not curr.is_rear and idx > 0:
                    curr = curr.next
                    idx -= 1
            elif idx < 0:
                while not curr.is_head and idx < 0:
                    curr = curr.prev
                    idx += 1

            return curr

    def __init__(self, collection=None):
        self._head = self._LinkedNode(None, None, None)
        self._rear = self._LinkedNode(None, None, None)
        self.clear()
        self.add_collection(collection)

    def __add__(self, other: Iterable):
        res = LinkedList()

        for it in self:
            res.append(it)

        for it in other:
            res.append(it)

        return res

    def __mul__(self, n):
        if isinstance(n, int) and n >= 0:
            res = LinkedList()
            for i in range(n):
                for it in self:
                    res.append(it)

            return res

        raise TypeError

    def __contains__(self, item):
        return self.index_of(item) >= 0

    def __copy__(self):
        res = LinkedList()
        for it in self:
            res.append(it)

        return res

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._get_node_at(key).info
        elif isinstance(key, slice):
            return self._get_slice(key)

        raise IndexError

    def __setitem__(self, key, value):
        if isinstance(key, int):
            self._get_node_at(key).info = value
        else:
            raise TypeError

    def __delitem__(self, key):
        if isinstance(key, int):
            node = self._get_node_at(key)
            self._remove_node(node)
        elif isinstance(key, slice):
            ls = self.to_list()
            del(ls[key])
            self.clear()
            self.add_collection(ls)
        else:
            raise TypeError

    def __iter__(self):
        class Iter(Iterator):
            def __init__(self, head, rear):
                self._curr = head.next
                self._rear = rear

            def __next__(self):
                if self._curr == self._rear:
                    raise StopIteration

                res = self._curr.info
                self._curr = self._curr.next
                return res

        return Iter(self._head, self._rear)

    def __len__(self):
        curr = self._head.next
        res = 0
        while curr != self._rear:
            res += 1
            curr = curr.next

        return res

    def __str__(self):
        count = len(self)
        sb = [''] * count

        idx = 0
        for it in self:
            sb[idx] = str(it)
            idx += 1

        return f"[{', '.join(sb)}]"

    @property
    def is_empty(self) -> bool:
        return self._head.next == self._rear

    def add_collection(self, col: Iterable):
        if isinstance(col, Iterable):
            for it in col:
                self.append(it)

    def append(self, item):
        node = self._LinkedNode(item, self._rear.prev, self._rear)
        self._rear.prev = node
        node.prev.next = node
        return self

    def append_iterable(self, tail: Iterable):
        for it in tail:
            self.append(it)

        return self

    def clear(self):
        self._head.next = self._rear
        self._rear.prev = self._head

    def count_of(self, item):
        res = 0
        for it in self:
            if it == item:
                res += 1

        return res

    def index_of(self, item):
        curr = self._head.next
        idx = 0
        while curr != self._rear:
            if curr.info == item:
                return idx

            idx += 1
            curr = curr.next

        return -1

    def prepend(self, item):
        node = self._LinkedNode(item, self._head, self._head.next)
        self._head.next = node
        node.next.prev = node
        return self

    def prepend_iterable(self, head: Iterable):
        for it in head:
            self.prepend(it)

        return self

    def remove(self, item):
        curr = self._head.next
        while not curr.is_rear:
            if curr.info == item:
                self._remove_node(curr)
                break

            curr = curr.next

    def remove_first(self):
        self._remove_node(self._head.next)
        return self

    def remove_last(self):
        self._remove_node(self._rear.prev)
        return self

    def to_list(self):
        res = [None] * len(self)
        idx = 0
        for it in self:
            res[idx] = it
            idx += 1

        return res

    # private methods

    @staticmethod
    def _remove_node(node: _LinkedNode):
        if not node.is_head and not node.is_rear:
            pv = node.prev
            nx = node.next
            pv.next = nx
            nx.prev = pv

    def _get_abs_index(self, idx):
        if idx >= 0:
            return idx
        else:
            return len(self) + idx

    def _get_node_at(self, idx: int):
        if idx >= 0:
            curr_idx = 0
            curr = self._head
            while curr_idx <= idx and not curr.is_rear:
                curr = curr.next
                curr_idx += 1

            if curr.is_rear:
                raise IndexError

            return curr
        else:
            curr_idx = -1
            curr = self._rear
            while curr_idx >= idx and not curr.is_head:
                curr = curr.prev
                curr_idx -= 1

            if curr.is_head:
                raise IndexError

            return curr

    def _get_slice(self, sl: slice):
        return LinkedList(self.to_list()[sl])
