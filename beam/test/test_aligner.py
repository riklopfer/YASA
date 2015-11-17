from beam import beam_aligner


def test(beam, source, target):
    aligner = beam_aligner.Aligner(beam, 1, 2, 2)
    alignment = aligner.align(source, target)
    print alignment
    return alignment


def test_all():
    test(1, "ax", "abc")
    test(5, "args", "largo")
    test(4, "this is a test".split(" "), "that is a very large test cat".split(" "))


if __name__ == '__main__':
    test_all()
