from shared.structures.Node import Node


class LinkedQueue:
    """
    A custom implementation of a Queue data structure (FIFO - First In, First Out).

    --- CODE REUSE NOTE ---
    This class was originally developed for the 'Algorithmic Thinking' course.
    Reused here to serve as a buffer for incoming requests before processing.
    -----------------------

    Attributes:
        head (Node): The first element in the queue (to be removed next).
        tail (Node): The last element in the queue (most recently added).
        _count (int): The current number of elements in the queue.
    """

    def __init__(self):
        self.head = None
        self.tail = None
        self._count = 0

    def add(self, value):
        """Enqueues a new item at the end of the queue."""
        new_node = Node(value)
        if self.tail is None:
            self.head = self.tail = new_node
        else:
            self.tail.next = new_node
            new_node.prev = self.tail
            self.tail = new_node
        self._count += 1

    def pop(self):
        """Dequeues (removes and returns) the item from the front of the queue."""
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
        """Returns the number of items in the queue."""
        return self._count