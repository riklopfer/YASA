import aligners.beam_aligner
import time
import random
import re

# random.seed(98723432)


def test_aligner(beam_size, source, target, pretty=True):
    print "beam_size={}".format(beam_size)
    aligner = aligners.beam_aligner.Aligner(beam_size)
    t0 = time.clock()
    alignment = aligner.align(source, target)
    print "Finished alignment in {}ms".format((time.clock() - t0) * 1000)
    print alignment.pretty_print() if pretty else alignment
    print
    return alignment


def jumble(tokens):
    for i in xrange(len(tokens) - 1):
        if random.random() < 0.1:
            swapx = random.randint(i + 1, len(tokens) - 1)
            if swapx < len(tokens):
                swap = tokens[swapx]
                tokens[swapx] = tokens[i]
                tokens[i] = swap


def __load_declaration(n=1):
    """
    Load the declaration of independence repeated n times.
    :param n:
    :return:
    """
    fp = open('declaration.txt')
    text = fp.read()
    fp.close()
    return text*n


def __del_some(tokens, frac=0.1):
    i = 0
    while i < len(tokens):
        if random.random() < frac:
            # print "deleting", tokens[i]
            del tokens[i]
            i += 1


def big_word_test():
    text = __load_declaration(100)
    target = __get_words(text)
    source = __get_words(text)
    # random.shuffle(source)
    __del_some(source)
    # __del_some(target)

    for beam_size in xrange(0, 50, 10):
        beam_size = beam_size if beam_size > 0 else 1
        test_aligner(beam_size, source, target, False)


def big_char_test():
    text = __load_declaration()
    source = [c for c in text]
    target = [c for c in text]
    jumble(source)

    for beam_size in xrange(0, 50, 10):
        test_aligner(beam_size, source, target, False)


def __get_words(text):
    return re.split("\s+", text)


def __get_chars(text):
    return [c for c in text]


def test_all():
    test_aligner(1, "ax", "abc")
    test_aligner(5, "args", "largo")
    test_aligner(4, __get_chars("this are an test"), __get_chars("this is a test"))
    test_aligner(200, "how many chucks could a wood chuck".split(" "), "if a wood chuck could chuck wood".split(" "))
    big_word_test()
    # big_char_test()


if __name__ == '__main__':
    test_all()
