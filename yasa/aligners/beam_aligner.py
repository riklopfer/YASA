"""
beam_aligner
Author: Russell Klopfer
"""
import itertools


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
        # self.__nodes.reverse()

        self.source_seq = source_seq
        self.target_seq = target_seq
        self.cost = final_node.cost

    def size(self):
        return len(self.__nodes)

    def node_at(self, align_x):
        return self.__nodes[align_x]

    def errors(self):
        """
        Get all the errors in the alignment
        :return:
        """

        def is_error(node):
            return (node.align_type == AlignmentType.SUB or
                    node.align_type == AlignmentType.INS or
                    node.align_type == AlignmentType.DEL)

        return filter(is_error, self.__nodes)

    def error_counts(self):
        """
        Count errors.
        :return: (error, count) pairs
        :rtype: tuple
        """
        # strings = map(lambda e: e.pretty_print(self.source_seq, self.target_seq), self.errors())
        errors = map(lambda n: SortableNode(n, self.source_seq, self.target_seq), self.errors())
        errors.sort()
        error_counts = map(lambda (k, g): (k, len(list(g))), itertools.groupby(errors))
        error_counts.sort(key=lambda (e, c): -c)
        return error_counts

    def errors_n(self):
        """
        Get the total number of errors in the alignment; i.e. the total number of substitutions, insertions, and
        deletions

        :return: total errors
        :rtype: int
        """
        return len(self.errors())

    def correct_n(self):
        """
        Get the total number of matches in the alignment.

        :return:
        :rtype: int
        """
        return len(filter(lambda n: n.align_type == AlignmentType.MATCH, self.__nodes))

    def wer(self):
        """
        Get the Word Error Rate for this alignment. Naturally, you can do this even if the alignment
        doesn't consist of words.

        :return: word error rate
        :rtype: float
        """
        err_n = float(self.errors_n())
        return err_n / (err_n + self.correct_n())

    def as_tuples(self):
        return [(node.source_token(self.source_seq), node.target_token(self.target_seq)) for node in self.__nodes]

    def __str__(self):
        return ("size={} len(source)={}, len(target)={}, cost={}, WER={}"
                .format(self.size(), len(self.source_seq), len(self.target_seq), self.cost, self.wer())
                )

    @staticmethod
    def normalize_for_logging(s):
        return s.replace("\n", "\\n").replace(' ', '<sp>')

    def pretty_print(self):
        pretty = self.__str__() + "\n"
        for node in self.__nodes:
            pretty += node.pretty_print(self.source_seq, self.target_seq) + "\n"
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
            flat.insert(0, current)
            # flat.append(current)
            current = current.previous
        return flat

    def is_source_end(self, source):
        return self.sourcePos >= len(source) - 1

    def is_target_end(self, target):
        return self.targetPos >= len(target) - 1

    def source_token(self, source_seq, empty=''):
        if self.align_type == AlignmentType.INS:
            return empty
        return source_seq[self.sourcePos]

    def target_token(self, target_seq, empty=''):
        if self.align_type == AlignmentType.DEL:
            return empty
        return target_seq[self.targetPos]

    def pretty_print(self, source_seq, target_seq):
        return ("{:<30}{:^10}{:>30}"
                .format(Alignment.normalize_for_logging(self.source_token(source_seq)),
                        self.align_type,
                        Alignment.normalize_for_logging(self.target_token(target_seq)))
                )

    def __eq__(self, other):
        if other is None:
            return False
        return (
            self.previous == other.previous and
            self.cost == other.cost and
            self.sourcePos == other.sourcePos and
            self.targetPos == other.targetPos
        )

    def __str__(self):
        return "{type: %s, source_pos: %d, target_pos: %d, cost: %d}" % (
            self.align_type, self.sourcePos, self.targetPos, self.cost)


class SortableNode(object):
    def __init__(self, alignment_node, source, target):
        """
        Constructor
        :param alignment_node:
        :type alignment_node: AlignmentNode
        :return:
        """
        self.source = alignment_node.source_token(source)
        self.target = alignment_node.target_token(target)
        self._pp = alignment_node.pretty_print(source, target)
        self.delegate = alignment_node

    def pretty_print(self, source, target):
        return self._pp

    def _key(self):
        return '{}{}{}'.format(self.source, self.target, self.delegate.align_type)

    def __str__(self):
        return self._pp

    def __lt__(self, other):
        """
        Less than comparison
        :param other:
        :type other: SortableNode
        :return:
        """
        return self._key() < other._key()

    def __eq__(self, other):
        """
        Equals
        :param other:
        :type other: SortableNode
        :return:
        """
        if other is None:
            return False

        return (self.delegate.align_type == other.delegate.align_type and
                self.source == other.source and
                self.target == other.target
                )


class Scoring(object):
    def insertion(self, token):
        raise NotImplementedError

    def deletion(self, token):
        raise NotImplementedError

    def substitution(self, source, target):
        raise NotImplementedError

    def match(self, source, target):
        return 0


class Levinshtein(Scoring):
    def __init__(self, ins_cost=1, del_cost=1, sub_cost=1):
        super(Levinshtein, self).__init__()
        self.ins_cost = ins_cost
        self.del_cost = del_cost
        self.sub_cost = sub_cost

    def substitution(self, source, target):
        return self.sub_cost

    def deletion(self, token):
        return self.del_cost

    def insertion(self, token):
        return self.ins_cost


class Aligner(object):
    # Constants
    START_NODE = AlignmentNode(AlignmentType.START, None, -1, -1, 0)
    MAX_BEAM_SIZE = 50000

    def __init__(self, beam_width, heap_size, scorer):
        """
        Construct a new aligner with the given parameters.
        :param beam_width: beam width (0 -> infinite)
        :param heap_size: heap size (0 -> infinite)
        :param scorer: object to determine the cost of operations
        :return: a new Aligner object

        :type beam_width: float
        :type heap_size: int
        :type scorer: Scoring
        :rtype: Aligner
        """
        self.beam_width = beam_width
        self.heap_size = heap_size
        self.scorer = scorer

    def __str__(self):
        return ("beam_width: {}, heap_size: {}, scorer: {}".
                format(self.beam_width, self.heap_size, self.scorer))

    @staticmethod
    def _print_heap(heap, source, target, n=None):
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
    def _add_new_node(node_list, node):
        node_list.append(node)

    @staticmethod
    def _prune(node_list, beam_width, max_size):
        """
        Prune the node list given a beam width and max size
        :param node_list:
        :param beam_width:
        :param max_size:
        :return:
        """
        pruned = sorted(node_list, key=lambda node: node.cost)
        if beam_width > 0 and node_list:
            best = node_list[0].cost
            pruned = filter(lambda _node: _node.cost < best + beam_width, pruned)
        if max_size > 0:
            pruned = pruned[:min(max_size, len(node_list))]
        return pruned

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
                self._populate_nodes(next_heap, node, source, target)
            current_heap = Aligner._prune(next_heap, self.beam_width, self.heap_size)

        return Alignment(current_heap[0], source, target)

    def _populate_nodes(self, next_heap, previous_node, source, target):
        source_x = previous_node.sourcePos
        target_x = previous_node.targetPos
        source_finished = source_x >= len(source) - 1
        target_finished = target_x >= len(target) - 1

        def insertion():
            return AlignmentNode(AlignmentType.INS, previous_node, source_x, target_x + 1,
                                 previous_node.cost + self.scorer.insertion(target[target_x]))

        def deletion():
            return AlignmentNode(AlignmentType.DEL, previous_node, source_x + 1, target_x,
                                 previous_node.cost + self.scorer.deletion(source[source_x]))

        def match():
            return AlignmentNode(AlignmentType.MATCH, previous_node, source_x + 1, target_x + 1,
                                 previous_node.cost + self.scorer.match(source[source_x], target[target_x]))

        def substitution():
            return AlignmentNode(AlignmentType.SUB, previous_node, source_x + 1, target_x + 1,
                                 previous_node.cost + self.scorer.substitution(source[source_x], target[target_x]))

        # we're at the end of the alignment already
        if source_finished and target_finished:
            Aligner._add_new_node(next_heap, previous_node)
            return

        # we're at the end of the source sequence, this must be an insertion
        if source_finished:
            Aligner._add_new_node(next_heap, insertion())
            # print insertion().pretty_print(source, target)
            return

        # we're at the end of the target sequence, this must be a deletion
        if target_finished:
            Aligner._add_new_node(next_heap, deletion())
            # print deletion().pretty_print(source, target)
            return

        # match
        if source[source_x + 1] == target[target_x + 1]:
            Aligner._add_new_node(next_heap, match())
        # sub
        else:
            Aligner._add_new_node(next_heap, substitution())

        # always allow for insertions
        Aligner._add_new_node(next_heap, insertion())
        # and deletions
        Aligner._add_new_node(next_heap, deletion())
