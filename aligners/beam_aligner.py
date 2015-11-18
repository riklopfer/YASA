import heapq


class Alignment:
    def __init__(self, final_node, source, target):
        self.pairs = []
        self.source = source
        self.target = target
        self.cost = final_node.cost

        node = final_node
        while node is not None:
            self.pairs.append((node.sourcePos, node.targetPos))
            node = node.previous
        self.pairs.reverse()

    def get_source_x(self, align_x):
        return self.pairs[align_x][0]

    def get_target_x(self, align_x):
        return self.pairs[align_x][0]

    def __str__(self):
        ret_value = "source={}, target={}, cost={}".format(self.source, self.target, self.cost)
        for pair in self.pairs:
            (source_x, target_x) = pair
            source_token = "" if source_x < 0 else self.source[source_x]
            target_token = "" if target_x < 0 else self.target[target_x]
            ret_value += "{:<30}{:>30}\n".format(source_token, target_token)
        return ret_value


class AlignmentNode:
    def __init__(self, previous, source_pos, target_pos, cost):
        self.previous = previous
        self.cost = cost
        self.sourcePos = source_pos
        self.targetPos = target_pos

    def __lt__(self, other):
        return self.cost < other.cost

    def __le__(self, other):
        return self.cost <= other.cost

    def __str__(self):
        return "{source_pos: %d, target_pos: %d, cost: %d}" % (self.sourcePos, self.targetPos, self.cost)


class Aligner:
    def __init__(self, beam_size, sub_cost, ins_cost, del_cost):
        assert beam_size > 0, "beam_size must be > 0"

        self.beam_size = beam_size
        self.sub_cost = sub_cost
        self.ins_cost = ins_cost
        self.del_cost = del_cost

    def align(self, source, target):
        heap = [AlignmentNode(None, -1, -1, 0)]

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

        if source_x >= len(source) - 1:
            heapq.heappush(heap, AlignmentNode(previous_node, source_x, target_x + 1, cost + self.ins_cost))
            return

        if target_x >= len(target) - 1:
            heapq.heappush(heap, AlignmentNode(previous_node, source_x + 1, target_x, cost + self.del_cost))
            return

        if source[source_x + 1] == target[target_x + 1]:
            heapq.heappush(heap, AlignmentNode(previous_node, source_x + 1, target_x + 1, cost))
        else:
            heapq.heappush(heap, AlignmentNode(previous_node, source_x + 1, target_x + 1, cost + self.sub_cost))

        # always allow for insertions
        heapq.heappush(heap, AlignmentNode(previous_node, source_x, target_x + 1, cost + self.ins_cost))
        # and deletions
        heapq.heappush(heap, AlignmentNode(previous_node, source_x + 1, target_x, cost + self.del_cost))
