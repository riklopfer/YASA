import aligners.beam_aligner
import time
import random
import re

random.seed(98723432)


def __param_search(source, target, pretty=False):
    for beam_size in xrange(0, 55, 10):
        beam_size = beam_size if beam_size > 0 else 1
        __test_aligner_params(beam_size, source, target, pretty)


def __test_aligner_params(beam_size, source, target, pretty=True):
    test_aligner(aligners.beam_aligner.Aligner(beam_size, .9, 1, 1), source, target, pretty)


def test_aligner(aligner, source, target, pretty=True):
    print aligner
    t0 = time.clock()
    alignment = aligner.align(source, target)
    print "Finished alignment in {}ms".format((time.clock() - t0) * 1000)
    print alignment.pretty_print() if pretty else alignment
    print
    return alignment


def test_reasonable_aligner(source, target, pretty=True):
    aligner = aligners.beam_aligner.construct_reasonable_aligner(source, target)
    test_aligner(aligner, source, target, pretty)


def test_wer_aligner(source, target, pretty=True):
    """
    Test Word Error Rate aligner

    :param source:
    :param target:
    :param pretty:
    :return:
    :rtype: None
    """
    aligner = aligners.beam_aligner.Aligner(200, 1, 1, 1)
    test_aligner(aligner, source, target, pretty)


def __jumble(tokens):
    for i in xrange(len(tokens) - 1):
        if random.random() < 0.1:
            swapx = random.randint(i + 1, len(tokens) - 1)
            if swapx < len(tokens):
                swap = tokens[swapx]
                tokens[swapx] = tokens[i]
                tokens[i] = swap


def __announce_test(test_name):
    print "-" * 20
    print test_name
    print "-" * 20


def __load_declaration(n=1):
    """
    Load the declaration of independence repeated n times.
    :param n:
    :return:
    """
    fp = open('declaration.txt')
    text = fp.read()
    fp.close()
    return text * n


def __del_some(tokens, frac=0.1):
    i = 0
    while i < len(tokens):
        if random.random() < frac:
            del tokens[i]
            i += 1


def __get_words(text):
    return re.split("\s+", text)


def __get_chars(text):
    return [c for c in text]


def big_word_test():
    __announce_test("Big Word Test")
    text = __load_declaration(100)
    target = __get_words(text)
    source = __get_words(text)
    __del_some(source)

    test_reasonable_aligner(source, target, False)
    # __param_search(source, target)


def big_char_test():
    __announce_test("Big Char Test")
    text = __load_declaration()
    source = [c for c in text]
    target = [c for c in text]
    __jumble(source)

    test_reasonable_aligner(source, target)
    # __param_search(source, target)


WORD_SOURCE_TARGET_PAIRS = [
    # disproportionately long target
    ("how many chucks could a wood chuck",
     "wood chucks are nice animals -- although they will dig holes in your garden. " +
     "how many chucks could a wood chuck if a wood chuck could chuck wood"),
    # disproportionately long source
    ("wood chucks are nice animals -- although they will dig holes in your garden. " +
     "how many chucks could a wood chuck if a wood chuck could chuck wood",
     "how many chucks could a wood chuck"),
    # this will not align
    ("this is a test", "sailing up wind is hard"),
    # poor alignment
    ("bad alignments are bad", "on the other hand, good alignments are good"),
    # reasonable alignment
    ("I think this test is fairly reasonable", "I stink this test is fairly unreasonable"),
    # reasonable alignment + 1
    ("I think this test is fairly reasonable", "I stink this test is fairly unreasonable right???"),
    # poor-ish alignment
    ("no alignment is better than a horrible one?", "i had a horrible headache")
]


def default_aligner_tests():
    __announce_test("Default Aligner Tests")

    for (source, target) in WORD_SOURCE_TARGET_PAIRS:
        test_reasonable_aligner(__get_words(source), __get_words(target))


def wer_aligner_tests():
    __announce_test("WER Aligner Tests")

    for (source, target) in WORD_SOURCE_TARGET_PAIRS:
        test_wer_aligner(__get_words(source), __get_words(target))


def known_weirdness():
    __announce_test("KNOWN WEIRDNESS")
    st_pairs = [

    ]

    for (source, target) in st_pairs:
        test_reasonable_aligner(__get_words(source), __get_words(target))


def test_all():
    known_weirdness()

    default_aligner_tests()
    wer_aligner_tests()

    big_word_test()
    # big_char_test()


if __name__ == '__main__':
    test_all()
