SequenceAlignment
=================

Beam Aligner
------------

Created to solve the problem of aligning long, *relatively* similar sequences. Long sequences of insertions or deletions 
will not be well modeled at the moment.

### Basic Usage

```python
from aligners import beam_aligner

aligner = beam_aligner.Aligner(beam_size=20, sub_cost=.9, ins_cost=1, del_cost=1)
source = "this is a test of the beam aligner"
target = "that was a test of the bean aligner"

word_alignment = aligner.align(source.split(" "), target.split(" "))
print word_alignment.pretty_print()

char_alignment = aligner.align(source, target)
print char_alignment.pretty_print()
```

### Run some tests

```bash
python -c 'import aligners.test; aligners.test.run()'
```
