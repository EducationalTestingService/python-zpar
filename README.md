### Introduction

**python-zpar** is a python wrapper around the [ZPar parser](http://www.sutd.edu.sg/cmsresource/faculty/yuezhang/zpar.html). ZPar was written by [Yue Zhang](http://www.sutd.edu.sg/yuezhang.aspx) while he was at Cambridge University. According to its home page: *ZPar is a statistical natural language parser, which performs syntactic analysis tasks including word segmentation, part-of-speech tagging and parsing. ZPar supports multiple languages and multiple grammar formalisms. ZPar has been most heavily developed for Chinese and English, while it provides generic support for other languages. ZPar is fast, processing above 50 sentences per second using the standard Penn Teebank (Wall Street Journal) data.*

I wrote this wrapper since I needed a fast and efficient parser for my NLP work which is primarily done in Python and not C++. I wanted to be able to use this parser directly from Python without having to create a bunch of files and running them through subprocesses. python-zpar not only provides a simply python wrapper but also provides an XML-RPC ZPar server to make batch-processing of large files easier.

python-zpar` uses [ctypes](https://docs.python.org/3.3/library/ctypes.html), a very cool foreign function library bundled with Python that allows calling functions in C DLLs or shared libraries directly.


### Installation
In order for python-zpar to work, it requires C functions that can be called directly. Since the only user-exposed entry point in ZPar is the command line client, I needed to write a new file that would have functions built on top of the ZPar functionality but expose them in a way that ctypes could understand.

Therefore, in order to build python-zpar from scratch, you need to download the ZPar source and patch it with the patch that I provide. Here's how to do that:

1. Download the ZPar source from [sourceforge](http://www.sourceforge.net/projects/zpar).
2. Unzip the source.
3. Change into the `zpar` directory that is created and type: `patch -p1 < [path to zpar.lib.patch]`, where `zpar.lib.patch` is the patch file included in this repository.
4. Now type `make zpar.so`. This will compile the shared library module that python-zpar requires under `dist/zpar.so`.

I have included pre-compiled 64-bit shared library modules for both linux and mac (the two platforms python-zpar was tested on) in the repository. The linux version was compiled on an x86_64 machine running RHEL 6.5. The mac version was compiled on a Late 2013 Macbook Pro running OS X Mavericks 10.9.3. Although I have recommended the modules for convenience, I strongly recommend that you take the time compile a native module for your machine.

If you are curious about what the C functions in the shared library module look like, the source file is included in the repository.

### Usage

To use python-zpar, you need the English models for ZPar. They can be downloaded from where. There are three models: a part-of-speech tagger, a constituency parser, and a dependency parser. For the purpose of the examples below, the models are in the `english-models` directory under the `zpar` directory.

Here's a small example of how to use python-zpar:

```python
import ctypes as c
import sys

from six import print_

# load the shared library
zpar = c.cdll.LoadLibrary("dist/zpar.so")

# expose the function to load the ZPar tagger
# and define its argument and return types
load_tagger = zpar.load_tagger
load_tagger.restype = c.c_int
load_tagger.argtypes = [c.c_char_p]

# expose the function to tag a sentence
tag_sentence = zpar.tag_sentence
tag_sentence.restype = c.c_char_p
tag_sentence.argtypes = [c.c_char_p]

# load the tagger from the models directory
if load_tagger(b"english-models"):
    sys.stderr.write("Error: no tagger model found.\n")
    # we do not really need to unload since this example
    # is only loading a single model. However, python-zpar
    # allows selective loading of models and it's a good idea
    # to unload any other models that might have successfully
    # loaded before exiting to prevent any memory leaks.
    zpar.unload_models()
    sys.exit(1)
else:
    # we need to pass in bytes since the function expects
    # a const char * and we need to include a newline
    # and a space at the end given how ZPar's word
    # tokenizer works.
    tagged_sent = zpar.tag_sentence(b"I am going to the market.\n ")
    # the output of the function is also bytes
    # so we need to convert it to string
    print_(tagged_sent.decode('utf-8'))


```

The above code sample produces the following output:

```
Loading tagger from english-models/tagger
Loading model... done.
I/PRP am/VBP going/VBG to/TO the/DT market/NN ./.
```

Detailed usage with comments is shown in the included file `zpar_example.py`. Run `python zpar_example.py -h` to see a list of all available options.


### ZPar Server
The repository provides an python XML-RPC implementation of a ZPar server that makes it easier to process multiple sentences and files by loading the models just once (via the ctypes interface) and allowing clients to connect and request analyses. The implementation is in the file `zpar_server.py`. The server is quite flexible and allows loading only the models that you need. In addition, it takes care of any and all conversions that are needed to communicate with the ctypes interface. Here's an example of how to start the server with only the tagger and the dependency parser models loaded:

```bash
$> python zpar_server.py --zpar dist --modeldir english-models --models tagger depparser  /scratch/nmadnani/zpar-new
INFO:Initializing server ...
Loading tagger from english-models/tagger
Loading model... done.
Loading dependency parser from english-models/depparser
Loading scores... done. (14.9623s)
INFO:Registering introspection ...
INFO:Starting server on port 8859...
```

Run `python zpar_server.py -h` to see a list of all options.


Once the server is running, you can connect to it using a client. An example client is included in the file `zpar_client.py` which can be run as follows:

```bash
$> python zpar_client.py
INFO:Attempting connection to http://localhost:8859
INFO:Tagging "I am going to the market."
INFO:Output: I/PRP am/VBP going/VBG to/TO the/DT market/NN ./.
INFO:Dep Parsing "I am going to the market."
INFO:Output: I  PRP 1   SUB
am  VBP -1  ROOT
going   VBG 1   VC
to  TO  2   VMOD
the DT  5   NMOD
market  NN  3   PMOD
.   .   1   P

INFO:Tagging file test.txt into test.tag
INFO:Dep Parsing file test.txt into

```

Note that python-zpar and all of the example scripts should work with both Python 2.7 and Python 3.3.

### ToDo

1. Improve error handling on both the python and C side.
2. Expose more functionality via ctypes, e.g., Chinese word segmentation, parsing etc.
