import aligner
import summary

from aligner import NestedLevinshteinAligner, LevinshteinAligner, Aligner, Scoring

from summary import ClassifierErrorRate, LabelErrorRate, error_counts

def __mk_aligner(heap, beam, scoring):
  """
  :type beam: int
  :type heap: int
  :type scoring: basestring
  :rtype: _core.Aligner

  :param beam:
  :param heap:
  :param scoring:
  :return:
  """
  scoring = scoring.lower()
  if scoring == 'levinshtein':
    return LevinshteinAligner(heap, beam)
  elif scoring == 'nested':
    return NestedLevinshteinAligner(heap, beam)
  else:
    raise ValueError(u"Unknown scoring type: '{}'".format(scoring))


def align(source, target, heap=100, beam=0, scoring='levinshtein'):
  """
  :type source: list
  :type target: list
  :type beam: int
  :type heap: int
  :type scoring: basestring
  :rtype: _core.Alignment

  :param source:
  :param target:
  :param beam:
  :param heap:
  :param scoring:
  :return:
  """
  return __mk_aligner(heap, beam, scoring).align(source, target)
