import aligner
import summary

from aligner import NestedLevinshteinAligner, LevinshteinAligner, Aligner, Scoring

from summary import ClassifierErrorRate, LabelErrorRate

def __mk_aligner(beam, heap, scoring):
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
    return LevinshteinAligner(beam, heap)
  elif scoring == 'nested':
    return NestedLevinshteinAligner(beam, heap)
  else:
    raise ValueError(u"Unknown scoring type: '{}'".format(scoring))


def align(source, target, beam=5, heap=100, scoring='levinshtein'):
  """
  :type source: list[basestring]
  :type target: list[basestring]
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
  return __mk_aligner(beam, heap, scoring).align(source, target)
