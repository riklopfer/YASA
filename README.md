YASA (Yet Another Sequence Aligner)
=================

Created to solve the problem of aligning long, *relatively* similar sequences. It may work well
on less-similar sequences, but that has not been tested yet. 

Install
-------

```bash
pip install --upgrade git+https://github.com/riklopfer/YASA/
```

Basic Usage
-----------

Starting with an interactive python prompt. 

Import the module
```python
import yasa
```

Define source and target lists
```python
source = "this is a test of the beam aligner".split()
target = "that was a test of the bean aligner".split()
```

Create the aligner and perform the alignment
```python
# create the aligner
aligner = yasa.LevinshteinAligner(heap_size=50, beam_width=5)
# do the alignment
word_alignment = aligner.align(source, target)
# pretty print
print(word_alignment)
```

Iterate over source-target pairs in the alignment
```python
for src, tgt in word_alignment:
  print("SRC: '{}' TGT: '{}'".format(src, tgt))
```

If we alter the input to be more poorly aligned, we can use the nested aligner to get a "better" alignment. 

```python
regular_aligner = yasa.LevinshteinAligner(heap_size=50)
nested_aligner = yasa.NestedLevinshteinAligner(heap_size=50)

source = "this is a test of the beam aligner".split() * 2
target = "that was a test of the bean".split() * 2

print(regular_aligner.align(source, target))
print(nested_aligner.align(source, target))

``` 