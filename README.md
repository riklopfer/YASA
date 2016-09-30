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
#!/usr/bin/env python
import yasa

source = "this is a test of the beam aligner"
target = "that was a test of the bean aligner"

aligner = yasa.NestedLevinshteinAligner(1, 50)
word_alignment = aligner.align(source.split(" "), target.split(" "))
print word_alignment.pretty_print()

aligner = yasa.LevinshteinAligner(1, 50)
char_alignment = aligner.align(source, target)
print char_alignment.pretty_print()
```
