from functools import lru_cache

from yasa.aligner import Aligner
from yasa.scoring import Scoring, LevinshteinScoring


class NestedLevinshteinScoring(Scoring):
    def __init__(self, heap_size: int = 10, beam_width: int = 0):
        super(NestedLevinshteinScoring, self).__init__()
        self._aligner = Aligner(LevinshteinScoring(), heap_size, beam_width)

    def deletion(self, token):
        return len(token)

    def insertion(self, token):
        return len(token)

    def match(self, token):
        # we really like matches
        return -len(token) * 1.2

    @lru_cache(10000)
    def substitution(self, source, target):
        return self._aligner.align(source, target).cost

