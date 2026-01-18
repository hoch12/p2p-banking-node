from shared.structures.Node import Node


class LinkedStack:
    """
    A custom implementation of a Stack data structure (LIFO - Last In, First Out).

    --- CODE REUSE NOTE ---
    This class was originally developed for the 'Algorithmic Thinking' course.
    Reused here to manage the Transaction History / Audit Log of the bank.
    -----------------------

    Attributes:
        top (Node): The most recently added element.
        _count (int): The current number of elements in the stack.
    """

    def __init__(self):
        self.top = None
        self._count = 0

    def add(self, value):
        """Pushes a new item onto the top of the stack."""
        new_node = Node(value)
        new_node.next = self.top
        self.top = new_node
        self._count += 1

    def pop(self):
        """Removes and returns the item from the top of the stack."""
        if self.top is None:
            raise IndexError("Pop from empty stack")
        value = self.top.value
        self.top = self.top.next
        self._count -= 1
        return value

    def count(self):
        """Returns the number of items in the stack."""
        return self._count

    def clear(self):
        """Removes all items from the stack."""
        self.top = None
        self._count = 0

    def popAll(self, as_list=True):
        """
        Removes all items and returns them as a collection.
        Useful for retrieving the full history log at once.
        """
        values = []
        while self.top is not None:
            values.append(self.pop())
        return values if as_list else tuple(values)