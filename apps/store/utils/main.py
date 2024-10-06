class Node:
    def _init_(self, data, next=None) -> None:
        self.data = data
        self.next = next

    def _str_(self) -> str:
        if self.next:
            return f"{self.data}"
        return f"{self.data}"


class Timeline:
    def _init_(self, head=None) -> None:
        self.head = head

    def create_node(self, data, next=None):
        if data:
            return Node(data, next)

    def insert_end(self, node: Node):
        if not self.head:
            self.head = node
            return

        start = self.head
        while True:
            if not start.next:
                start.next = node
                break
            else:
                start = start.next
        return

    def build_timeline(self, data=[]):
        for i in data:
            self.insert_end(Node(i))

    def get_timeline_data(
        self,
    ):
        data = []

    def _str_(self) -> str:
        start = self.head
        display = ""
        while True:
            if not start:
                break
            if start.next:
                display += f"[ {start.data} ] --> "
            else:
                display += f"[ {start.data} ] "
            start = start.next
        return display
