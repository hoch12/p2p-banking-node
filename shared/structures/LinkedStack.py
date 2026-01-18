from shared.structures.Node import Node

class LinkedStack:
    def __init__(self):
        self.top = None
        self._count = 0

    def add(self, value):
        new_node = Node(value)
        new_node.next = self.top
        self.top = new_node
        self._count += 1

    def pop(self):
        if self.top is None:
            raise IndexError("Pop from empty stack")
        value = self.top.value
        self.top = self.top.next
        self._count -= 1
        return value

    def count(self):
        return self._count

    def clear(self):
        self.top = None
        self._count = 0

    def popAll(self, as_list=True):
        values = []
        while self.top is not None:
            values.append(self.pop())
        return values if as_list else tuple(values)