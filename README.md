SequenceAlignment
=================

Beam Aligner
------------

Created to solve the problem of aligning long, *relatively* similar sequences. It may work well
on less-similar sequences, but that has not been tested yet. 

### Basic Usage

```python
from aligners import beam_aligner

source = "this is a test of the beam aligner"
target = "that was a test of the bean aligner"

word_alignment = beam_aligner.align(source.split(" "), target.split(" "))
print word_alignment.pretty_print()

char_alignment = beam_aligner.align(source, target)
print char_alignment.pretty_print()
```

### Run some tests

```bash
python -c 'import aligners.test; aligners.test.run()'
```
