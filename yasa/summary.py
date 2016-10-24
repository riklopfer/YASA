from __future__ import division

__all__ = ['ErrorRate', 'AlignmentErrorRate']

_error_rate_header_format = '{:<32}{:<12}{:<12}{:<12}{:<12}\n'
_align_error_header = _error_rate_header_format.format('Token', 'Precision', 'Recall', 'F1', 'Accuracy')
_error_rate_format = '{:<32}{:<12.3f}{:<12.3f}{:<12.3f}{:<12.3f}'


class ErrorRate(object):
    def __init__(self, token):
        self.token = token

        self.false_positives = 0
        self.false_negatives = 0
        self.true_positives = 0

    def accu_tuple(self, source, target):
        if source == target:
            if source == self.token:
                self.true_positives += 1
        elif source == self.token:
            self.false_negatives += 1
        elif target == self.token:
            self.false_positives += 1

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
        return self.true_positives / (self.true_positives + self.false_negatives + self.false_positives)

    def __str__(self):
        return _error_rate_format.format(self.token, self.precision,
                                         self.recall, self.f1,
                                         self.accuracy)


class AlignmentErrorRate(object):
    def __init__(self):
        self.token_error_rates = dict()

    def accu_alignment(self, alignment):
        for source, target in alignment.as_tuples():
            self.accu_tuple(source, target)

    def accu_tuple(self, source, target):
        if source is not None:
            if source not in self.token_error_rates:
                self.token_error_rates[source] = ErrorRate(source)
            self.token_error_rates[source].accu_tuple(source, target)

        if target is not None:
            if target not in self.token_error_rates:
                self.token_error_rates[target] = ErrorRate(target)
            self.token_error_rates[target].accu_tuple(source, target)

    def get_error_rate(self, token):
        return self.token_error_rates.get(token)

    def __str__(self):
        return self.as_string()

    def as_string(self, tokens=None):
        s = _align_error_header
        if tokens is not None:
            for key in tokens:
                if key not in self.token_error_rates:
                    s += '{:<32}{}'.format(key, 'TOKEN NOT OBSERVED')
                else:
                    error_rate = self.token_error_rates[key]
                    s += '{}\n'.format(error_rate)
        else:
            for key, error_rate in self.token_error_rates.items():
                if error_rate.accuracy < 1:
                    s += '{}\n'.format(error_rate)
        return s
