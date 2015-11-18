import aligners.beam_aligner
import time
import random

random.seed(98723432)


def test_aligner(beam_size, source, target):
    print "beam_size={}".format(beam_size)
    aligner = aligners.beam_aligner.Aligner(beam_size)
    t0 = time.clock()
    alignment = aligner.align(source, target)
    print "Finished alignment in {}ms".format((time.clock() - t0) * 1000)
    print alignment.pretty_print()
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


def load_declaration():
    fp = open('declaration.txt')
    text = fp.read()
    fp.close()
    return text


def big_word_test():
    text = load_declaration()
    target = text.split(" ")
    source = text.split(" ")
    jumble(source)

    test_aligner(1, source, target)


def big_char_test():
    text = load_declaration()
    source = [c for c in text]
    target = [c for c in text]
    jumble(source)

    for beam_size in xrange(1, 51, 10):
        test_aligner(beam_size, source, target)


def __get_words(text):
    return text.split(" ")


def __get_chars(text):
    return [c for c in text]


def test_all():
    test_aligner(1, "ax", "abc")
    test_aligner(5, "args", "largo")
    test_aligner(4, __get_chars("this are an test"), __get_chars("this is a test"))
    test_aligner(200, "how many chucks could a wood chuck".split(" "), "if a wood chuck could chuck wood".split(" "))
    # big_word_test()
    # big_char_test()


if __name__ == '__main__':
    test_all()
