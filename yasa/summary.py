from __future__ import division

import itertools

__all__ = ['LabelErrorRate', 'ClassifierErrorRate', 'WordErrorRate',
           'ERROR_RATE_HEADER']

_error_rate_header_format = '{:<32}{:<12}{:<12}{:<12}{:<12}'
ERROR_RATE_HEADER = _error_rate_header_format.format('Label', 'Precision',
                                                     'Recall', 'F1', 'Accuracy')
_error_rate_format = '{:<32}{:<12.3f}{:<12.3f}{:<12.3f}{:<12.3f}'


def error_counts(alignment):
    """
    Count errors.
    :type alignment: aligner.Alignment
    :return: (error, count) pairs
    :rtype: list[(str,int)]
    """
    errors = [Error.construct(n, alignment.source_seq, alignment.target_seq)
              for n in alignment.errors()]

    counts = [(errtype, len(list(errs)))
              for errtype, errs
              in itertools.groupby(errors, lambda _: _.align_type)]
    return sorted(counts, key=lambda kv: -kv[1])


class Error(object):
    def __init__(self, source, target, align_type):
        """
        :type source: basestring
        :type target: basestring
        :type align_type: basestring

        :param source:
        :param target:
        :param align_type:
        """
        self._source = source
        self._target = target
        self._align_type = align_type

    @staticmethod
    def construct(alignment_node, source, target):
        """
        Constructor
        :param alignment_node:
        :type alignment_node: AlignmentNode
        :return:
        """
        return Error(alignment_node.source_token(source),
                     alignment_node.target_token(target),
                     alignment_node.align_type)

    @property
    def source(self):
        return self._source

    @property
    def target(self):
        return self._target

    @property
    def align_type(self):
        return self._align_type

    def _key(self):
        return '{}{}{}'.format(self.source, self.target, self.align_type)

    def __str__(self):
        return u"{:30}{:5}{:>30}".format(self.source, self.align_type, self.target)

    def __lt__(self, other):
        """
        Less than comparison
        :param other:
        :type other: Error
        :return:
        """
        return self._key() < other._key()

    def __eq__(self, other):
        """
        Equals
        :param other:
        :type other: Error
        :return:
        """
        if other is None:
            return False

        return (self.align_type == other.align_type and
                self.source == other.source and
                self.target == other.target
                )


class LabelErrorRate(object):
    def __init__(self, label):
        self.label = label

        self.false_positives = 0
        self.false_negatives = 0
        self.true_positives = 0

    def accu_tuple(self, ref, hyp):
        if ref == hyp:
            if ref == self.label:
                self.true_positives += 1
        elif ref == self.label:
            self.false_negatives += 1
        elif hyp == self.label:
            self.false_positives += 1

    @property
    def precision(self):
        denominator = self.true_positives + self.false_positives
        return self.true_positives / denominator if denominator > 0 else float(
            'NaN')

    @property
    def recall(self):
        denominator = self.true_positives + self.false_negatives
        return self.true_positives / denominator if denominator > 0 else float(
            'NaN')

    @property
    def f1(self):
        denominator = self.precision + self.recall
        return 2 * (
                self.precision * self.recall) / denominator if denominator > 0 else 0.

    @property
    def accuracy(self):
        # num correct / number of occurrences (either ref or hyp)
        return self.true_positives / (
                self.true_positives + self.false_negatives + self.false_positives)

    def __str__(self):
        return _error_rate_format.format(self.label, self.precision,
                                         self.recall, self.f1,
                                         self.accuracy)


class ClassifierErrorRate(object):
    def __init__(self):
        self.token_error_rates = dict()
        self.overall = LabelErrorRate(None)

    def accu_alignment(self, alignment):
        for ref, hyp in alignment:
            self.overall.accu_tuple(ref, hyp)
            self.accu_tuple(ref, hyp)

    def accu_tuple(self, ref, hyp):
        if ref is not None:
            if ref not in self.token_error_rates:
                self.token_error_rates[ref] = LabelErrorRate(ref)

            self.token_error_rates[ref].accu_tuple(ref, hyp)

        if hyp is not None:
            if hyp not in self.token_error_rates:
                self.token_error_rates[hyp] = LabelErrorRate(hyp)

            self.token_error_rates[hyp].accu_tuple(ref, hyp)

    def get_error_rate(self, label):
        return self.token_error_rates.get(label)

    def __str__(self):
        return self.as_string()

    def as_string(self, labels=None):
        s = ERROR_RATE_HEADER + '\n'
        if labels is not None:
            for key in labels:
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


class WordErrorRate(object):
    def __init__(self):
        self.correct = 0
        self.incorrect = 0

    def accu_alignment(self, alignment):
        self.correct += alignment.correct_n()
        self.incorrect += alignment.errors_n()

    @property
    def wer(self):
        return self.incorrect / (self.correct + self.incorrect)

    @property
    def wacc(self):
        return 1 - self.wer

    def __str__(self):
        return 'WER: {:.5f} Correct: {} Incorrect: {}'.format(self.wer,
                                                              self.correct,
                                                              self.incorrect)
