#!/usr/bin/env python
from __future__ import print_function

import random
import re
import time
import unittest

import yasa

# do we want randomized results to be reproducible?
random.seed(98723432)


def run_aligner(source, target, scoring='levinshtein', pretty=True):
  print(scoring)
  t0 = time.clock()
  alignment = yasa.align(source, target, beam=10, heap=100, scoring=scoring)
  t1 = time.clock()
  if pretty:
    print("+" * 10, "  Alignment Time = {} ms  ".format(
        (t1 - t0) * 1000), "+" * 10)
    print(alignment.pretty_print())
    print(alignment)
    print("+" * 10, "  Alignment Time = {} ms  ".format(
        (t1 - t0) * 1000), "+" * 10)
    print()
    summary = yasa.ClassifierErrorRate()
    summary.accu_alignment(alignment)
    print(summary)
  else:
    print(alignment)

  print()
  return alignment


class TestNonStringAlignment(unittest.TestCase):
  def test_non_string_alignment(self):
    run_aligner([1, 2, 3], [2, 2, 3, 3], 'levinshtein')


def run_wer_aligner(source, target, pretty=True):
  """
  Test Word Error Rate aligner

  :param source:
  :param target:
  :param pretty:
  :return:
  :rtype: None
  """
  run_aligner(source, target, pretty=pretty)


def jumble(tokens):
  for i in xrange(len(tokens) - 1):
    if random.random() < 0.1:
      # only let the sapping take place N tokens apart
      swapx = random.randint(i + 1, min(i + 1 + 5, len(tokens) - 1))
      if swapx < len(tokens):
        swap = tokens[swapx]
        tokens[swapx] = tokens[i]
        tokens[i] = swap


def load_declaration():
  """
  Load the declaration of independence repeated n times.
  :return:
  """
  print("Loading declaration...", end=' ')
  with open('declaration.txt', 'rb') as fp:
    text = fp.read()
  print("Done")
  return text


WORD_SOURCE_TARGET_PAIRS = [
  # disproportionately long target
  ("how many chucks could a wood chuck",
   "wood chucks are nice animals -- although they will dig holes in your garden. " +
   "how many chucks could a wood chuck if a wood chuck could chuck wood"),
  # disproportionately long source
  (
    "wood chucks are nice animals -- although they will dig holes in your garden. " +
    "how many chucks could a wood chuck if a wood chuck could chuck wood",
    "how many chucks could a wood chuck"),
  # this will not align
  ("this is a test", "sailing up wind is hard"),
  # poor alignment
  ("bad alignments are bad", "on the other hand, good alignments are good"),
  # reasonable alignment
  ("I think this test is fairly reasonable",
   "I stink this test is fairly unreasonable"),
  # reasonable alignment + 1
  ("I think this test is fairly reasonable",
   "I stink this test is fairly unreasonable right???"),
  # poor-ish alignment
  ("no alignment is better than a horrible one?", "i had a horrible headache"),
  ("this is a little bit tricky", "fishes are a very sticky animal"),
  ("this is very crappy and this is a little bit tricky",
   "this is a little bit tricky")
]


def del_some(tokens, del_prob=0.1, m_del_prob=0.4):
  new_tokens = []
  for i in xrange(len(tokens)):
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


class WordAlignmentTests(unittest.TestCase):

  def test_big_text(self):
    text = load_declaration() * 3
    target = del_some(get_words(text))
    source = del_some(get_words(text))
    alignment = yasa.align(source, target, beam=10, heap=100)
    print(alignment.pretty_print("source", "target"))
    # since the default cost per error is 1, this should hold
    self.assertEqual(alignment.cost, alignment.errors_n())


  def test_default(self):
    for (source, target) in WORD_SOURCE_TARGET_PAIRS:
      run_aligner(get_words(source), get_words(target), 'nested')

  def test_basic(self):
    source = "this is a test of the beam aligner".split()
    target = "that was a test of the bean aligner".split()

    aligner = yasa.LevinshteinAligner(1, 50)
    word_alignment = aligner.align(source, target)
    print(word_alignment.pretty_print())

  def test_basic_nested(self):
    source = "this is a test of the beam aligner".split() * 2
    target = "that was a test of the bean".split() * 2

    aligner = yasa.NestedLevinshteinAligner(0, 100)
    word_alignment = aligner.align(source, target)
    print(word_alignment.pretty_print())


class TestErrorRates(unittest.TestCase):
  def test_wer_aligner(self):
    for (source, target) in WORD_SOURCE_TARGET_PAIRS:
      run_wer_aligner(get_words(source), get_words(target))

  def test_error_rates(self):

    aligner = yasa.NestedLevinshteinAligner(1, 100)

    for (source, target) in WORD_SOURCE_TARGET_PAIRS:
      source = get_words(source)
      target = get_words(target)

      alignment = aligner.align(source, target)
      print(alignment)
      for node in alignment.errors():
        print(node.pretty_print(source, target))

  def test_error_counts_1(self):
    source = get_words("a b b a")
    target = get_words("a x x i s")

    alignment = yasa.LevinshteinAligner(1, 10).align(source, target)
    print(alignment)
    error_counts = yasa.error_counts(alignment)
    for (error, count) in error_counts:
      print('{}\t{}'.format(error, count))

    self.assertEqual(3, len(error_counts))

  def test_error_counts_2(self):
    source = get_words("a b b a")
    target = get_words("a x x i s s s s s")

    alignment = yasa.LevinshteinAligner(1, 10).align(source, target)
    error_counts = yasa.error_counts(alignment)
    for (error, count) in error_counts:
      print('{}\t{}'.format(error, count))

    self.assertEqual(3, len(error_counts))

  def test_bad_error_key(self):
    source = get_words("a b b a")
    target = get_words("a x x i s s s s s")

    alignment = yasa.LevinshteinAligner(1, 10).align(source, target)

    err = yasa.ClassifierErrorRate()
    err.accu_alignment(alignment)

    print(err.as_string(labels=['a', 'b', 'x', 'bad', 'poopy']))
