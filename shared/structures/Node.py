class Node:
    """
    Represents a fundamental building block (node) for linked data structures.
    Used in both LinkedStack and LinkedQueue.

    Attributes:
        value (any): The data stored in this node.
        prev (Node): Reference to the previous node (for doubly linked lists).
        next (Node): Reference to the next node.
    """
    def __init__(self, value):
        self.value = value
        self.prev = None
        self.next = None