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
import yasa

source = "this is a test of the beam aligner"
target = "that was a test of the bean aligner"

aligner = yasa.LevinshteinAligner(1, 50)
word_alignment = aligner.align(source.split(" "), target.split(" "))
print(word_alignment.pretty_print())

```

which will produce

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
  
