from __future__ import division

__all__ = ['ErrorRate', 'AlignmentErrorRate', 'ERROR_RATE_HEADER']

_error_rate_header_format = '{:<32}{:<12}{:<12}{:<12}{:<12}'
ERROR_RATE_HEADER = _error_rate_header_format.format('Token', 'Precision', 'Recall', 'F1', 'Accuracy')
_error_rate_format = '{:<32}{:<12.3f}{:<12.3f}{:<12.3f}{:<12.3f}'


class ErrorRate(object):
    def __init__(self, token):
        self.token = token

        self.false_positives = 0
        self.false_negatives = 0
        self.true_positives = 0

    def accu_tuple(self, ref, hyp):
        if ref == hyp:
            if ref == self.token:
                self.true_positives += 1
        elif ref == self.token:
            self.false_negatives += 1
        elif hyp == self.token:
            self.false_positives += 1

    def sum(self, other):
        """
        Return a new error rate which is the sum of this one and the next.
        :param other:
        :return:

        :type other: ErrorRate
        :rtype: ErrorRate
        """
        merged = ErrorRate(self.token)
        merged.false_positives = self.false_positives + other.false_positives
        merged.false_negatives = self.false_negatives + other.false_negatives
        merged.true_positives = self.true_positives + other.true_positives
        return merged

    @property
    def precision(self):
        denominator = self.true_positives + self.false_positives
        return self.true_positives / denominator if denominator > 0 else float('NaN')

    @property
    def recall(self):
        denominator = self.true_positives + self.false_negatives
        return self.true_positives / denominator if denominator > 0 else float('NaN')

    @property
    def f1(self):
        denominator = self.precision + self.recall
        return 2 * (self.precision * self.recall) / denominator if denominator > 0 else 0.

    @property
    def accuracy(self):
        # num correct / number of occurrences (either ref or hyp)
        return self.true_positives / (self.true_positives + self.false_negatives + self.false_positives)

    def __str__(self):
        return _error_rate_format.format(self.token, self.precision,
                                         self.recall, self.f1,
                                         self.accuracy)


class AlignmentErrorRate(object):
    def __init__(self):
        self.token_error_rates = dict()
        self.overall = ErrorRate(None)

    def accu_alignment(self, alignment):
        for ref, hyp in alignment.as_tuples():
            self.overall.accu_tuple(ref, hyp)
            self.accu_tuple(ref, hyp)

    def accu_tuple(self, ref, hyp):
        if ref is not None:
            if ref not in self.token_error_rates:
                self.token_error_rates[ref] = ErrorRate(ref)
            self.token_error_rates[ref].accu_tuple(ref, hyp)

        if hyp is not None:
            if hyp not in self.token_error_rates:
                self.token_error_rates[hyp] = ErrorRate(hyp)
            self.token_error_rates[hyp].accu_tuple(ref, hyp)

    def get_error_rate(self, token):
        return self.token_error_rates.get(token)

    def __str__(self):
        return self.as_string()

    def as_string(self, tokens=None):
        s = "{:-^80}\n".format("Overall")
        s += str(self.overall) + "\n"

        s += ERROR_RATE_HEADER + '\n'
        if tokens is not None:
            for key in tokens:
                if key not in self.token_error_rates:
                    s += '{:<32}{}\n'.format(key, 'NOT OBSERVED')
                else:
                    error_rate = self.token_error_rates[key]
                    s += '{}\n'.format(error_rate)
        else:
            for key, error_rate in self.token_error_rates.items():
                if error_rate.accuracy < 1:
                    s += '{}\n'.format(error_rate)
        return s
