import random
import time
from yasa.aligners import beam_aligner
import re

# do we want randomized results to be reproducible?
random.seed(98723432)


def test_aligner(aligner, source, target, pretty=True):
    print aligner
    t0 = time.clock()
    alignment = aligner.align(source, target)
    t1 = time.clock()
    if pretty:
        print "+" * 10, "  Alignment Time = {} ms  ".format((t1 - t0) * 1000), "+" * 10
        print alignment.pretty_print()
        print alignment
        print "+" * 10, "  Alignment Time = {} ms  ".format((t1 - t0) * 1000), "+" * 10
        print
    else:
        print alignment
    print
    return alignment


def __jumble(tokens):
    for i in xrange(len(tokens) - 1):
        if random.random() < 0.1:
            # only let the sapping take place N tokens apart
            swapx = random.randint(i + 1, min(i + 1 + 5, len(tokens) - 1))
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
    print "Loading declaration...",
    fp = open('declaration.txt')
    text = fp.read()
    fp.close()
    print "Done"
    return text * n


def __del_some(tokens, del_prob=0.1, m_del_prob=0.4):
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


def __get_words(text):
    return re.split("\s+", text)


def __get_chars(text):
    return [c for c in text]


def big_word_test():
    __announce_test("Big Word Test")
    # TODO there is something strange going on here.
    # If you run the big word test with one copy of the declaration everything works fine. But, if you use 2
    # copies the alignment become horrible.

    copies_of_declaration = 1
    text = __load_declaration(copies_of_declaration)
    target = __get_words(text)
    source = __get_words(text)
    source = __del_some(source)
    target = __del_some(target)

    print "SOURCE"
    print " ".join(source)
    print "TARGET"
    print " ".join(target)

    aligner = beam_aligner.Aligner(20, 1, 1, 1)
    test_aligner(aligner, source, target, True)
    # __param_search(source, target, True)


def big_char_test():
    __announce_test("Big Char Test")
    text = __load_declaration()
    source = [c for c in text]
    target = [c for c in text]
    __jumble(source)

    aligner = beam_aligner.Aligner(20, 1, 1, 1)
    test_aligner(aligner, source, target, True)


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
        source = __get_words(source)
        target = __get_words(target)
        aligner = beam_aligner.construct_reasonable_aligner(source, target)
        test_aligner(aligner, source, target, True)


def known_weirdness():
    __announce_test("KNOWN WEIRDNESS")
    st_pairs = [

    ]

    aligner = beam_aligner.Aligner(20, 1, 1, 1)
    for (source, target) in st_pairs:
        test_aligner(aligner, __get_words(source), __get_words(target))


def as_tuples_ins_test():
    __announce_test(as_tuples_ins_test.__name__)
    aligner = beam_aligner.Aligner(20, 1, 1, 1)
    source = "a test".split(" ")
    target = "not a test".split(" ")

    tuples = aligner.align(source, target).as_tuples()
    print tuples
    assert tuples == [('', 'not'), ('a', 'a'), ('test', 'test')]


def as_tuples_del_test():
    __announce_test(as_tuples_del_test.__name__)
    aligner = beam_aligner.Aligner(20, 1, 1, 1)
    source = "not a test".split(" ")
    target = "a test".split(" ")

    tuples = aligner.align(source, target).as_tuples()
    print tuples
    assert tuples == [('not', ''), ('a', 'a'), ('test', 'test')]


def as_tuples_sub_test():
    __announce_test(as_tuples_sub_test.__name__)
    aligner = beam_aligner.Aligner(20, 1, 1, 1)
    source = "snot a test".split(" ")
    target = "not a test".split(" ")

    tuples = aligner.align(source, target).as_tuples()
    print tuples
    assert tuples == [('snot', 'not'), ('a', 'a'), ('test', 'test')]


def test_all():
    # known_weirdness()
    #
    # default_aligner_tests()
    as_tuples_ins_test()
    as_tuples_del_test()
    as_tuples_sub_test()

    # big_word_test()
    # big_char_test()


if __name__ == '__main__':
    test_all()
