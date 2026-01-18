from shared.structures.Node import Node

class LinkedQueue:
    def __init__(self):
        self.head = None
        self.tail = None
        self._count = 0

    def add(self, value):
        new_node = Node(value)
        if self.tail is None:
            self.head = self.tail = new_node
        else:
            self.tail.next = new_node
            new_node.prev = self.tail
            self.tail = new_node
        self._count += 1

    def pop(self):
        if self.head is None:
            raise IndexError("Pop from empty queue")
        value = self.head.value
        self.head = self.head.next
        if self.head is not None:
            self.head.prev = None
        else:
            self.tail = None
        self._count -= 1
        return value

    def count(self):
        return self._count