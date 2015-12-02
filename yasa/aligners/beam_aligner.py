"""
beam_aligner
Author: Russell Klopfer
"""


class Alignment(object):
    def __init__(self, final_node, source_seq, target_seq):
        """
        Construct a new alignment from the given parameters.

        :param final_node:
        :param source_seq:
        :param target_seq:
        :return:
        :rtype: Alignment
        """
        self.__nodes = final_node.flatten()
        self.__nodes.reverse()

        self.source_seq = source_seq
        self.target_seq = target_seq
        self.cost = final_node.cost

    def size(self):
        return len(self.__nodes)

    def get_source(self, align_x):
        if self.get_type(align_x) == AlignmentType.INS:
            return ''
        return self.source_seq[self.__nodes[align_x].sourcePos]

    def get_target(self, align_x):
        if self.get_type(align_x) == AlignmentType.DEL:
            return ''
        return self.target_seq[self.__nodes[align_x].targetPos]

    def get_type(self, align_x):
        return self.__nodes[align_x].align_type

    def get_cost(self, align_x):
        return self.__nodes[align_x].cost

    def get_wer(self):
        """
        Get the Word Error Rate for this alignment. Naturally, you can do this even if the alignment
        doesn't consist of words.
        :return: word error rate
        :rtype: float
        """
        s = len(filter(lambda n: n.align_type == AlignmentType.SUB, self.__nodes))
        i = len(filter(lambda n: n.align_type == AlignmentType.INS, self.__nodes))
        d = len(filter(lambda n: n.align_type == AlignmentType.DEL, self.__nodes))
        # let's actually count the matches, since we don't want to include START or other signal nodes
        m = len(filter(lambda n: n.align_type == AlignmentType.MATCH, self.__nodes))
        return float(s + i + d) / float(s + i + d + m)

    def as_tuples(self):
        return [(self.get_source(i), self.get_target(i)) for i in xrange(self.size())]

    def __str__(self):
        return ("size={} len(source)={}, len(target)={}, cost={}, WER={}"
                .format(self.size(), len(self.source_seq), len(self.target_seq), self.cost, self.get_wer())
                )

    def pretty_print(self):
        pretty = self.__str__() + "\n"
        for i in xrange(self.size()):
            a_type = self.get_type(i)
            source = self.get_source(i).replace("\n", "\\n")
            target = self.get_target(i).replace("\n", "\\n")
            pretty += "{:<30}{:^10}{:>30}   {:<5}\n".format(source, a_type, target, self.get_cost(i))
        return pretty


class AlignmentType:
    def __init__(self):
        raise AssertionError("Cannot instantiate this 'enum' type")

    START = "START"
    MATCH = "MATCH"
    SUB = "SUB"
    INS = "INS"
    DEL = "DEL"


class AlignmentNode(object):
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
        :rtype: list
        """
        flat = []
        current = self
        while current != Aligner.START_NODE:
            flat.append(current)
            current = current.previous
        return flat

    def is_source_end(self, source):
        return self.sourcePos >= len(source) - 1

    def is_target_end(self, target):
        return self.targetPos >= len(target) - 1

    def __eq__(self, other):
        return (
            self.previous == other.previous and
            self.cost == other.cost and
            self.sourcePos == other.sourcePos and
            self.targetPos == other.targetPos
        )

    def __str__(self):
        return "{type: %s, source_pos: %d, target_pos: %d, cost: %d}" % (
            self.align_type, self.sourcePos, self.targetPos, self.cost)

    def pretty_print(self, source, target):
        return Alignment(self, source, target).pretty_print()


class Aligner(object):
    # Constants
    START_NODE = AlignmentNode(AlignmentType.START, None, -1, -1, 0)
    MAX_BEAM_SIZE = 50000

    def __init__(self, beam_size, sub_cost=1, ins_cost=1, del_cost=1):
        """
        Construct a new aligner with the given parameters.

        :param sub_cost: cost of substituting one token for another
        :param ins_cost: cost of inserting a token (something in target that isn't in source)
        :param del_cost: cost of deleting a token (something in source that isn't in target)
        :return: a new Aligner object
        :rtype: Aligner
        """
        assert beam_size > 0, "beam_size must be > 0"
        self.beam_size = beam_size
        self.sub_cost = sub_cost
        self.ins_cost = ins_cost
        self.del_cost = del_cost

    def __str__(self):
        return ("beam_size: {}, sub_cost: {}, ins_cost: {}, del_cost: {}".
                format(self.beam_size, self.sub_cost, self.ins_cost, self.del_cost))

    @staticmethod
    def __print_heap(heap, source, target, n=None):
        """
        Prints the top-n elements of the heap.

        :param heap:
        :param n:
        :return: None
        """
        n = len(heap) if n is None else min(n, len(heap))
        print "************HEAP**************\n({}) [[[".format(len(heap))
        for i in xrange(n - 1, 0, -1):
            print "{}.) {}\n".format(i, Alignment(heap[i], source, target).pretty_print())
        print "]]]"

    @staticmethod
    def __add_new_node(node_list, node):
        node_list.append(node)

    @staticmethod
    def __prune(node_list, top_n):
        return sorted(node_list, key=lambda node: node.cost)[:min(top_n, len(node_list))]

    def align(self, source, target):
        """

        :param source:
        :param target:
        :return:
        :rtype: Alignment
        """
        current_heap = [Aligner.START_NODE]

        while current_heap[0].sourcePos < len(source) - 1 or current_heap[0].targetPos < len(target) - 1:
            # Aligner.__print_heap(current_heap, source, target, 5)
            next_heap = []
            for node in current_heap:
                self.__populate_nodes(next_heap, node, source, target)
            current_heap = Aligner.__prune(next_heap, self.beam_size)

        return Alignment(current_heap[0], source, target)

    def __populate_nodes(self, next_heap, previous_node, source, target):
        source_x = previous_node.sourcePos
        target_x = previous_node.targetPos
        source_finished = source_x >= len(source) - 1
        target_finished = target_x >= len(target) - 1

        def insertion():
            return AlignmentNode(AlignmentType.INS, previous_node, source_x, target_x + 1,
                                 previous_node.cost + self.ins_cost)

        def deletion():
            return AlignmentNode(AlignmentType.DEL, previous_node, source_x + 1, target_x,
                                 previous_node.cost + self.del_cost)

        def match():
            return AlignmentNode(AlignmentType.MATCH, previous_node, source_x + 1, target_x + 1,
                                 previous_node.cost)

        def substitution():
            return AlignmentNode(AlignmentType.SUB, previous_node, source_x + 1, target_x + 1,
                                 previous_node.cost + self.sub_cost)

        # we're at the end of the alignment already
        if source_finished and target_finished:
            Aligner.__add_new_node(next_heap, previous_node)
            return

        # we're at the end of the source sequence, this must be an insertion
        if source_finished:
            Aligner.__add_new_node(next_heap, insertion())
            # print insertion().pretty_print(source, target)
            return

        # we're at the end of the target sequence, this must be a deletion
        if target_finished:
            Aligner.__add_new_node(next_heap, deletion())
            # print deletion().pretty_print(source, target)
            return

        # match
        if source[source_x + 1] == target[target_x + 1]:
            Aligner.__add_new_node(next_heap, match())
        # sub
        else:
            Aligner.__add_new_node(next_heap, substitution())

        # always allow for insertions
        Aligner.__add_new_node(next_heap, insertion())
        # and deletions
        Aligner.__add_new_node(next_heap, deletion())


def construct_reasonable_aligner(source, target):
    return Aligner(200)


def align(source, target):
    return construct_reasonable_aligner(source, target).align(source, target)
