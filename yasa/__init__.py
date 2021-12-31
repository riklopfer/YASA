from typing import List

from yasa.aligner import Aligner
from yasa.nested import NestedLevinshteinScoring
from yasa.scoring import LevinshteinScoring
from yasa.summary import *


def __mk_aligner(heap_size: int, beam_size: int, scoring: str):
    """
    :type beam_size: int
    :type heap_size: int
    :type scoring: basestring
    :rtype: _core.Aligner

    :param beam_size:
    :param heap_size:
    :param scoring:
    :return:
    """
    scoring = scoring.lower()
    if scoring == 'levinshtein':
        scoring_obj = LevinshteinScoring()
    elif scoring == 'nested':
        scoring_obj = NestedLevinshteinScoring(heap_size=10, beam_width=0)
    else:
        raise ValueError(u"Unknown scoring type: '{}'".format(scoring))

    return Aligner(scorer=scoring_obj, heap_size=heap_size, beam_width=beam_size)


def align(source: List, target: List, heap_size: int = 100, beam: int = 0, scoring: str = 'levinshtein'):
    """
    :type source: list
    :type target: list
    :type beam: int
    :type heap_size: int
    :type scoring: basestring
    :rtype: _core.Alignment

    :param source:
    :param target:
    :param beam:
    :param heap_size:
    :param scoring:
    :return:
    """
    return __mk_aligner(heap_size, beam, scoring).align(source, target)
