from typing import List

from yasa.aligner import *
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
        return LevinshteinAligner(heap_size, beam_size)
    elif scoring == 'nested':
        return NestedLevinshteinAligner(heap_size, beam_size)
    else:
        raise ValueError(u"Unknown scoring type: '{}'".format(scoring))


def align(source: List[str], target: List[str], heap_size: int = 100, beam: int = 0, scoring: str = 'levinshtein'):
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
