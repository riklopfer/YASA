"""
beam_aligner
Author: Russell Klopfer
"""
from __future__ import division

__all__ = ['Aligner', ]

from typing import List


class AlignmentType:
    def __init__(self):
        raise AssertionError("Cannot instantiate this 'enum' type")

    START = "START"
    MATCH = "MATCH"
    SUB = "SUB"
    INS = "INS"
    DEL = "DEL"


def _normalize_for_logging(s):
    if not s:
        return s

    return s.replace(u"\n", u"\\n").replace(u' ', 'u<sp>')


class AlignmentNode(object):
    def __init__(self, align_type, previous, source_pos, target_pos, cost):
        """

        :rtype: AlignmentNode
        """
        self.align_type = align_type
        self.previous = previous
        self.cost = cost
        self.source_pos = source_pos
        self.target_pos = target_pos

    def _trace_back(self):
        current = self
        while current != Aligner.START_NODE:
            yield current
            current = current.previous

    def flatten(self):
        """
        Flatten the linked nodes into a list.
        :return:
        :rtype: list
        """
        return list(self._trace_back())[::-1]

    def is_source_end(self, source):
        return self.source_pos >= len(source) - 1

    def is_target_end(self, target):
        return self.target_pos >= len(target) - 1

    def source_token(self, source_seq, empty=None):
        if self.align_type == AlignmentType.INS:
            return empty
        return source_seq[self.source_pos]

    def target_token(self, target_seq, empty=None):
        if self.align_type == AlignmentType.DEL:
            return empty
        return target_seq[self.target_pos]

    def pretty_print(self, source_seq, target_seq):
        return u"{:<30}{:^10}{:>30}".format(
            _normalize_for_logging(str(self.source_token(source_seq))),
            self.align_type,
            _normalize_for_logging(str(self.target_token(target_seq))))

    def __eq__(self, other):
        if other is None:
            return False
        return (
                self.previous == other.previous and
                self.cost == other.cost and
                self.source_pos == other.source_pos and
                self.target_pos == other.target_pos
        )

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "{type: %s, source_pos: %d, target_pos: %d, cost: %d}" % (
            self.align_type, self.source_pos, self.target_pos, self.cost)


class Insertion(AlignmentNode):
    def __init__(self, previous, cost):
        super(Insertion, self).__init__(AlignmentType.INS, previous,
                                        previous.source_pos,
                                        previous.target_pos + 1,
                                        previous.cost + cost)


class Deletion(AlignmentNode):
    def __init__(self, previous, cost):
        super(Deletion, self).__init__(AlignmentType.DEL, previous,
                                       previous.source_pos + 1,
                                       previous.target_pos,
                                       previous.cost + cost)


class Substitution(AlignmentNode):
    def __init__(self, previous, cost):
        super(Substitution, self).__init__(AlignmentType.SUB, previous,
                                           previous.source_pos + 1,
                                           previous.target_pos + 1,
                                           previous.cost + cost)


class Match(AlignmentNode):
    def __init__(self, previous, cost):
        super(Match, self).__init__(AlignmentType.MATCH, previous,
                                    previous.source_pos + 1,
                                    previous.target_pos + 1,
                                    previous.cost + cost)


class Alignment(object):
    def __init__(self, final_node: AlignmentNode, source_seq: List, target_seq: List):
        """
        Construct a new alignment from the given parameters.

        :param final_node:
        :param source_seq:
        :param target_seq:
        :return:
        :rtype: Alignment
        """
        self.__nodes = final_node.flatten()

        self.source_seq = source_seq
        self.target_seq = target_seq
        self.cost = final_node.cost

    def size(self) -> int:
        return len(self.__nodes)

    def node_at(self, align_x) -> AlignmentNode:
        return self.__nodes[align_x]

    def errors(self) -> List[AlignmentNode]:
        """
        Get all the errors in the alignment
        :return:
        :rtype: list[AlignmentNode]
        """

        def is_error(node):
            return (node.align_type == AlignmentType.SUB or
                    node.align_type == AlignmentType.INS or
                    node.align_type == AlignmentType.DEL)

        return [n for n in self.__nodes if is_error(n)]

    def errors_n(self) -> int:
        """
        Get the total number of errors in the alignment; i.e. the total number of substitutions, insertions, and
        deletions

        :return: total errors
        :rtype: int
        """
        return len(self.errors())

    def matches(self) -> List[Match]:
        return [n for n in self.__nodes if n.align_type == AlignmentType.MATCH]

    def correct_n(self) -> int:
        """
        Get the total number of matches in the alignment.

        :return:
        :rtype: int
        """
        return len(self.matches())

    def wer(self) -> float:
        """
        Get the Word Error Rate for this alignment. Naturally, you can do this even if the alignment
        doesn't consist of words.

        :return: word error rate
        :rtype: float
        """
        err_n = self.errors_n()
        if err_n:
            return err_n / (err_n + self.correct_n())
        else:
            return 0.

    def __iter__(self):
        for node in self.__nodes:
            yield (node.source_token(self.source_seq),
                   node.target_token(self.target_seq))

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.pretty_print()

    def pretty_print(self, source_title='Source', target_title='Target') -> str:
        pretty = ("size={} len(source)={}, len(target)={}, cost={}, WER={}\n"
                  .format(self.size(), len(self.source_seq), len(self.target_seq),
                          self.cost, self.wer())
                  )
        pretty += "{:<30}{:^10}{:>30}\n".format(source_title, 'Operation',
                                                target_title)
        pretty += "{:<30}{:^10}{:>30}\n".format('-' * len(source_title), '-' * 9,
                                                '-' * len(target_title))
        for node in self.__nodes:
            pretty += node.pretty_print(self.source_seq, self.target_seq) + "\n"
        return pretty


class NodeHeap(object):
    def __init__(self, beam_size: int, max_size: int):
        """
        :type beam_size: float
        :type max_size: int
        :param beam_size:
        :param max_size:
        """
        self._beam = beam_size
        self._max_size = max_size

        self._node_list: List[AlignmentNode] = []
        self._is_sorted = True

    def __len__(self):
        return len(self._node_list)

    def __iter__(self):
        self._sort_nodes()
        for node in self._node_list:
            yield node

    def to_string(self, source, target, n=None):
        """
        Prints the top-n elements of the heap.

        :param source:
        :param target:
        :param n:

        :rtype: basestring
        """
        n = len(self) if n is None else min(n, len(self))
        heap_string = "************HEAP (size={})**************\n".format(len(self))
        for idx, node in enumerate(self._node_list[:n][::-1]):
            if n and n == idx:
                break
            tmp_align = Alignment(node, source, target)
            heap_string += "{}.) {}\n".format(n - idx, tmp_align.pretty_print())
        return heap_string

    def add(self, node: AlignmentNode):
        """

        :param node:
        :return:
        :rtype: None
        """
        self._is_sorted = False
        self._node_list.append(node)

    def _sort_nodes(self):
        if self._is_sorted:
            return

        self._node_list.sort(key=lambda node: node.cost)
        self._is_sorted = True

    @property
    def top(self) -> AlignmentNode:
        """:rtype: AlignmentNode"""
        self._sort_nodes()
        return self._node_list[0]

    def prune(self) -> None:
        """Prune the list"""
        if not self._node_list:
            return

        self._sort_nodes()
        if self._beam > 0:
            best = self.top.cost
            idx = 1
            while idx < len(self._node_list):
                if self._node_list[idx].cost > best + self._beam:
                    break
                idx += 1
            assert idx > 0
            self._node_list = self._node_list[:idx]

        if self._max_size > 0:
            self._node_list = self._node_list[:min(self._max_size, len(self))]


class Aligner(object):
    # Constants
    START_NODE = AlignmentNode(AlignmentType.START, None, -1, -1, 0.)

    def __init__(self, scorer, heap_size: int, beam_width: int):
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

    def _new_heap(self) -> NodeHeap:
        return NodeHeap(self.beam_width, self.heap_size)

    def __str__(self):
        return ("beam_width: {}, heap_size: {}, scorer: {}".
                format(self.beam_width, self.heap_size, self.scorer))

    def align(self, source: List, target: List):
        """
        Generate alignment between source and target.

        :param source:
        :param target:
        :type source: list
        :type target: list
        :return:
        :rtype: Alignment
        """
        current_heap = self._new_heap()
        current_heap.add(Aligner.START_NODE)

        while (current_heap.top.source_pos < len(source) - 1 or
               current_heap.top.target_pos < len(target) - 1):
            next_heap = self._new_heap()
            for node in current_heap:
                self._expand_from_node(next_heap, node, source, target)
            next_heap.prune()
            current_heap = next_heap

        return Alignment(current_heap.top, source, target)

    def _expand_from_node(self, next_heap: NodeHeap, previous_node: AlignmentNode, source: List, target: List):
        """
        Create new nodes pointing back to previous_node and place them in next_heap.

        :type next_heap: NodeHeap
        :type previous_node: AlignmentNode
        :type source: list
        :type target: list

        :param next_heap:
        :param previous_node:
        :param source:
        :param target:
        """
        source_x = previous_node.source_pos
        target_x = previous_node.target_pos
        source_finished = source_x == len(source) - 1
        target_finished = target_x == len(target) - 1

        def insertion():
            return Insertion(previous_node,
                             self.scorer.insertion(target[target_x]))

        def deletion():
            return Deletion(previous_node,
                            self.scorer.deletion(source[source_x]))

        def match():
            return Match(previous_node,
                         self.scorer.match(source[source_x]))

        def substitution():
            return Substitution(previous_node,
                                self.scorer.substitution(source[source_x + 1],
                                                         target[target_x + 1])
                                )

        # we're at the end of the alignment already. just copy the previous node
        # into the next heap.
        if source_finished and target_finished:
            next_heap.add(previous_node)
            return

        # we're at the end of the source sequence. this must be an insertion.
        if source_finished:
            next_heap.add(insertion())
            return

        # we're at the end of the target sequence. this must be a deletion.
        if target_finished:
            next_heap.add(deletion())
            return

        """
        Now add the all 3 possible next actions, which are:
        (1) Match or Substitution
        (2) Insertion
        (3) Deletion
        """

        if source[source_x + 1] == target[target_x + 1]:
            # match
            next_heap.add(match())
        else:
            # sub
            next_heap.add(substitution())

        # always allow for insertions
        next_heap.add(insertion())
        # and deletions
        next_heap.add(deletion())
