"""
Scoring / Aligner Implementations
"""


class Scoring(object):
    def insertion(self, token):
        raise NotImplementedError

    def deletion(self, token):
        raise NotImplementedError

    def substitution(self, source, target):
        raise NotImplementedError

    def match(self, token):
        raise NotImplementedError


class FixedScoring(Scoring):
    def __init__(self, ins_cost: float, del_cost: float, sub_cost: float, match_cost: float):
        super(Scoring, self).__init__()
        self.ins_cost = ins_cost
        self.del_cost = del_cost
        self.sub_cost = sub_cost
        self.match_cost = match_cost

    def substitution(self, source, target):
        return self.sub_cost

    def deletion(self, token):
        return self.del_cost

    def insertion(self, token):
        return self.ins_cost

    def match(self, token):
        return self.match_cost


class LevinshteinScoring(FixedScoring):
    """
    Standard Levinshtein distance
    """

    def __init__(self):
        super(LevinshteinScoring, self).__init__(1, 1, 1, 0)
