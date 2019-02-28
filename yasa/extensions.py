from __future__ import absolute_import
from __future__ import division

from yasa.core import Aligner
from yasa.core import Scoring

__all__ = ['LevinshteinAligner',
           'NestedLevinshteinAligner',
           ]


class LevinshteinScoring(Scoring):
  """
  Levinshtein distance
  """

  def __init__(self, ins_cost=1, del_cost=1, sub_cost=1):
    super(LevinshteinScoring, self).__init__()
    self.ins_cost = ins_cost
    self.del_cost = del_cost
    self.sub_cost = sub_cost

  def substitution(self, source, target):
    return self.sub_cost

  def deletion(self, token):
    return self.del_cost

  def insertion(self, token):
    return self.ins_cost


class LevinshteinAligner(Aligner):
  """
  Aligner that that produces alignments with cost equal to the Levinshtein
  distance
  """

  def __init__(self, beam_width, heap_size):
    """
    Constructor
    :param beam_width:
    :param heap_size: equivalent
    """
    super(LevinshteinAligner, self).__init__(beam_width, heap_size,
                                             LevinshteinScoring())


class NestedAlignmentScoring(Scoring):
  """
  Cost of deletions and insertions will be equal to the length of the token.
  Cost of substitutions will be the cost of the alignment according to the
  nested aligner.
  """

  def __init__(self, aligner):
    """
    :param aligner: aligner to determine the cost of substitutions
    :type aligner: Aligner
    """
    super(NestedAlignmentScoring, self).__init__()
    self._aligner = aligner

  def deletion(self, token):
    return len(token)

  def insertion(self, token):
    return len(token)

  def substitution(self, source, target):
    return self._aligner.align(source, target).cost


class NestedLevinshteinScoring(Scoring):
  def __init__(self, beam_width, heap_size):
    super(NestedLevinshteinScoring, self).__init__()
    self._aligner = LevinshteinAligner(beam_width, heap_size)

  def deletion(self, token):
    return len(token)

  def insertion(self, token):
    return len(token)

  def match(self, token):
    # we really like matches
    return -len(token) * 1.5

  def substitution(self, source, target):
    return self._aligner.align(source, target).cost


class NestedLevinshteinAligner(Aligner):
  """
  Aligner which produces alignments with cost determined by the Levinshtein
  distance between individual tokens.
  """

  def __init__(self, beam_width, heap_size):
    """
    Constructor
    :param beam_width:
    :param heap_size:
    """
    super(NestedLevinshteinAligner,
          self).__init__(beam_width, heap_size,
                         NestedLevinshteinScoring(5, 10))
