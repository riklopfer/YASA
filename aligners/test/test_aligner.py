import aligners.beam_aligner


def test(beam_size, source, target):
    aligner = aligners.beam_aligner.Aligner(beam_size, 1, 2, 2)
    alignment = aligner.align(source, target)
    print alignment
    return alignment


def test_all():
    test(1, "ax", "abc")
    test(5, "args", "largo")
    test(4, "this is a test".split(" "), "that is a very large test cat".split(" "))
    test(200, "how many chucks could a wood chuck".split(" "), "if a wood chuck could chuck wood".split(" "))


if __name__ == '__main__':
    test_all()
