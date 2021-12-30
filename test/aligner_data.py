# coding=utf-8
import os.path

_THIS_LOC = os.path.dirname(__file__)


def load_declaration() -> str:
    with open(os.path.join(_THIS_LOC, 'data', 'declaration.txt'), 'r') as ifp:
        return ifp.read().strip()


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
