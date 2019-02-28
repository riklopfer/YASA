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
from __future__ import print_function
import yasa

source = "this is a test of the beam aligner".split()
target = "that was a test of the bean aligner".split()

# create the aligner
aligner = yasa.LevinshteinAligner(1, 50)
# do the alignment
word_alignment = aligner.align(source, target)
# pretty print
print(word_alignment.pretty_print())

"""
size=8 len(source)=8, len(target)=8, cost=3.0, WER=0.375
Source                        Operation                         Target
------                        ---------                         ------
this                             SUB                              that
is                               SUB                               was
a                               MATCH                                a
test                            MATCH                             test
of                              MATCH                               of
the                             MATCH                              the
beam                             SUB                              bean
aligner                         MATCH                          aligner
"""


# iterate over source-target pairs
for src, tgt in word_alignment:
  print("SRC: '{}' TGT: '{}'".format(src, tgt))
  
"""
SRC: 'this' TGT: 'that'
SRC: 'is' TGT: 'was'
SRC: 'a' TGT: 'a'
SRC: 'test' TGT: 'test'
SRC: 'of' TGT: 'of'
SRC: 'the' TGT: 'the'
SRC: 'beam' TGT: 'bean'
SRC: 'aligner' TGT: 'aligner'
"""
```
