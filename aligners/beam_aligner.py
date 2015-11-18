import heapq


class Alignment:
    def __init__(self, final_node, source, target):
        self.nodes = final_node.flatten()
        self.nodes.reverse()

        self.source = source
        self.target = target
        self.cost = final_node.cost

    def size(self):
        return len(self.nodes)

    def get_source(self, align_x):
        return self.source[self.nodes[align_x].sourcePos]

    def get_target(self, align_x):
        return self.target[self.nodes[align_x].targetPos]

    def get_type(self, align_x):
        return self.nodes[align_x].align_type

    def __str__(self):
        return ("size={} len(source)={}, len(target)={}, cost={}"
                .format(self.size(), len(self.source), len(self.target), self.cost)
                )

    def pretty_print(self):
        pretty = self.__str__() + "\n"
        for i in xrange(self.size()):
            pretty += "{:<30}{:^10}{:>30}\n".format(self.get_source(i), self.get_type(i), self.get_target(i))
        return pretty


class AlignmentType:
    def __init__(self):
        assert False, "Cannot instantiate this 'enum' type"

    START = "START"
    MATCH = "MATCH"
    SUB = "SUB"
    INS = "INS"
    DEL = "DEL"


class AlignmentNode:
    def __init__(self, align_type, previous, source_pos, target_pos, cost):
        """

        :rtype: AlignmentNode
        """
        self.align_type = align_type
        self.previous = previous
        self.cost = cost
        self.sourcePos = source_pos
        self.targetPos = target_pos

    def flatten(self):
        """
        Flatten the linked nodes into a list.
        :return:
        """
        flat = []
        current = self
        while current != Aligner.START_NODE:
            flat.append(current)
            current = current.previous
        return flat

    def __eq__(self, other):
        return (
            self.previous == other.previous and
            self.cost == other.cost and
            self.sourcePos == other.sourcePos and
            self.targetPos == other.targetPos
        )

    def __lt__(self, other):
        return self.cost < other.cost

    def __le__(self, other):
        return self.cost <= other.cost

    def __str__(self):
        return "{type: %s, source_pos: %d, target_pos: %d, cost: %d}" % (
            self.align_type, self.sourcePos, self.targetPos, self.cost)


class Aligner:
    START_NODE = AlignmentNode(AlignmentType.START, None, -1, -1, 0)

    def __init__(self, beam_size, sub_cost=1, ins_cost=2, del_cost=2):
        assert beam_size > 0, "beam_size must be > 0"

        self.beam_size = beam_size
        self.sub_cost = sub_cost
        self.ins_cost = ins_cost
        self.del_cost = del_cost

    def align(self, source, target):
        heap = [Aligner.START_NODE]

        while heap[0].sourcePos < len(source) - 1 or heap[0].targetPos < len(target) - 1:
            next_heap = []
            for node in heap:
                self.__populate_nodes(next_heap, node, source, target)
            heap = next_heap[:min(self.beam_size, len(next_heap))]

        return Alignment(heap[0], source, target)

    def __populate_nodes(self, heap, previous_node, source, target):
        source_x = previous_node.sourcePos
        target_x = previous_node.targetPos
        cost = previous_node.cost

        # we're at the end of the source sequence, this must be an insertion
        if source_x >= len(source) - 1:
            heapq.heappush(heap, AlignmentNode(AlignmentType.INS, previous_node, source_x, target_x + 1,
                                               cost + self.ins_cost))
            return

        # we're at the end of the target sequence, this must be a deletion
        if target_x >= len(target) - 1:
            heapq.heappush(heap, AlignmentNode(AlignmentType.DEL, previous_node, source_x + 1, target_x,
                                               cost + self.del_cost))
            return

        # match
        if source[source_x + 1] == target[target_x + 1]:
            heapq.heappush(heap, AlignmentNode(AlignmentType.MATCH, previous_node, source_x + 1, target_x + 1, cost))
        # sub
        else:
            heapq.heappush(heap, AlignmentNode(AlignmentType.SUB, previous_node, source_x + 1, target_x + 1,
                                               cost + self.sub_cost))

        # always allow for insertions
        heapq.heappush(heap,
                       AlignmentNode(AlignmentType.INS, previous_node, source_x, target_x + 1, cost + self.ins_cost))
        # and deletions
        heapq.heappush(heap,
                       AlignmentNode(AlignmentType.DEL, previous_node, source_x + 1, target_x, cost + self.del_cost))
