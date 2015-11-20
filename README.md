YASA
=================

Yet Another Sequence Aligner

Beam Aligner
------------

Created to solve the problem of aligning long, *relatively* similar sequences. It may work well
on less-similar sequences, but that has not been tested yet. 

### Install

```bash
pip install --upgrade https://github.com/riklopfer/YASA/archive/master.zip
```

### Basic Usage

```python
from yasa.aligners import beam_aligner

source = "this is a test of the beam aligner"
target = "that was a test of the bean aligner"

word_alignment = beam_aligner.align(source.split(" "), target.split(" "))
print word_alignment.pretty_print()

char_alignment = beam_aligner.align(source, target)
print char_alignment.pretty_print()
```

### Run some tests

If you have the project cloned you can do this. Currently the tests are not installed by pip.

```bash
python -c 'from yasa.aligners import test; test.run()'
```
