import aligners.beam_aligner
import time
import random
import re


random.seed(98723432)


def test_aligner_params(beam_size, source, target, pretty=True):
    test_aligner(aligners.beam_aligner.Aligner(beam_size, .9, 1, 1), source, target, pretty)


def test_aligner(aligner, source, target, pretty=True):
    print aligner
    t0 = time.clock()
    alignment = aligner.align(source, target)
    print "Finished alignment in {}ms".format((time.clock() - t0) * 1000)
    print alignment.pretty_print() if pretty else alignment
    print
    return alignment


def test_default_aligner(source, target, pretty=True):
    aligner = aligners.beam_aligner.construct_reasonable_aligner(source, target)
    test_aligner(aligner, source, target, pretty)


def jumble(tokens):
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
            # print "deleting", tokens[i]
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

    test_default_aligner(source, target)
    # __param_search(source, target)


def big_char_test():
    __announce_test("Big Char Test")
    text = __load_declaration()
    source = [c for c in text]
    target = [c for c in text]
    jumble(source)

    __param_search(source, target)


def __param_search(source, target, pretty=False):
    for beam_size in xrange(0, 55, 10):
        beam_size = beam_size if beam_size > 0 else 1
        test_aligner_params(beam_size, source, target, pretty)


def short_prefix_test():
    __announce_test("Short Prefix Test")
    source = __get_words("this is a test")
    target = __get_words("sailing upwind is difficult") + source

    beam_size = 3 ** int(max(len(source), len(target)) / 2)
    test_aligner_params(beam_size, source, target, True)

    aligner = aligners.beam_aligner.construct_reasonable_aligner(source, target)
    test_aligner(aligner, source, target, True)


def default_aligner_tests():
    __announce_test("Default Aligner Tests")
    st_pairs = [
        ("how many chucks could a wood chuck",
         "wood chucks are nice animals -- although they will dig holes in your garden. " +
         "how many chucks could a wood chuck if a wood chuck could chuck wood"),
        ("this is a test", "i will not align at all"),
        ("bad alignments are bad", "on the other hand, good alignments are good"),
        ("no alignment is better than a horrible one?", "i had a horrible headache")
    ]

    for (source, target) in st_pairs:
        test_default_aligner(__get_words(source), __get_words(target))


def known_weirdness():
    __announce_test("KNOWN WEIRDNESS")
    st_pairs = [
        ("I think this test is fairly reasonable", "I stink this test is fairly unreasonable"),
        # TODO why does this produce INS + DEL instead of SUB???
        ("I think this test is fairly reasonable", "I stink this test is fairly unreasonable right???"),
    ]

    for (source, target) in st_pairs:
        test_default_aligner(__get_words(source), __get_words(target))


def test_all():
    known_weirdness()

    # default_aligner_tests()
    # short_prefix_test()

    # big_word_test()
    # big_char_test()


if __name__ == '__main__':
    test_all()
