#!/usr/bin/env python
from __future__ import print_function

import random
import re
import unittest

import aligner_data
import yasa

# do we want randomized results to be reproducible?
random.seed(98723432)


class TestNonStringAlignment(unittest.TestCase):
    def test_non_string_alignment(self):
        yasa.align([1, 2, 3], [2, 2, 3, 3], scoring='levinshtein')


def jumble(tokens):
    for i in range(len(tokens) - 1):
        if random.random() < 0.1:
            # only let the sapping take place N tokens apart
            swapx = random.randint(i + 1, min(i + 1 + 5, len(tokens) - 1))
            if swapx < len(tokens):
                swap = tokens[swapx]
                tokens[swapx] = tokens[i]
                tokens[i] = swap


def del_some(tokens, del_prob=0.1, m_del_prob=0.4):
    new_tokens = []
    for i in range(len(tokens)):
        if random.random() > del_prob:
            # match here
            new_tokens.append(tokens[i])
        else:
            # maybe this deletion is a multiple deletion
            while random.random() < m_del_prob:
                i += 1
    return new_tokens


def get_words(text):
    return re.findall(r"[\w']+|[.,!?;]", text)


def get_chars(text):
    return [c for c in text]


def test_big_text():
    text = aligner_data.load_declaration()
    text = (text + u" ") * 3
    target = del_some(get_words(text))
    source = del_some(get_words(text))
    alignment = yasa.align(source, target, heap_size=100)
    print(alignment.pretty_print("source", "target"))
    # since the default cost per error is 1, this should hold
    assert alignment.cost == alignment.errors_n()


def test_default():
    for (source, target) in aligner_data.WORD_SOURCE_TARGET_PAIRS:
        result = yasa.align(get_words(source), get_words(target), scoring='nested')
        pass


def test_basic():
    source = "this is a test of the beam aligner".split()
    target = "that was a test of the bean aligner".split()

    word_alignment = yasa.align(source, target, 50, 1)
    print(word_alignment.pretty_print())


def test_basic_nested():
    source = "this is a test of the beam aligner".split() * 2
    target = "that was a test of the bean".split() * 2

    word_alignment = yasa.align(source, target, 100, scoring='nested')
    print(word_alignment.pretty_print())


def test_error_itr():
    for (source, target) in aligner_data.WORD_SOURCE_TARGET_PAIRS:
        source = get_words(source)
        target = get_words(target)

        alignment = yasa.align(source, target, 100, 1)
        print(alignment)
        for node in alignment.errors():
            print(node.pretty_print(source, target))


def test_error_counts_1():
    source = get_words("a b b a")
    target = get_words("a x x i s")

    alignment = yasa.align(source, target, 100, 1)
    print(alignment)
    error_counts = yasa.error_counts(alignment)
    for (error, count) in error_counts:
        print('{}\t{}'.format(error, count))

    assert 2 == len(error_counts)


def test_error_counts_2():
    source = get_words("a b b a")
    target = get_words("a x x i s s s s s")

    alignment = yasa.align(source, target, 10, 1)
    error_counts = yasa.error_counts(alignment)
    for (error, count) in error_counts:
        print('{}\t{}'.format(error, count))

    assert 2 == len(error_counts)
