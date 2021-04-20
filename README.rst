NOTE
~~~~
This project is no longer under active development since there are now
really nice pure Python parsers such as `Stanza <https://stanfordnlp.github.io/stanza/index.html>`__ and `Spacy <https://spacy.io>`__. The repository will remain here for archival purposes and the `PyPI <https://pypi.org/project/python-zpar/>`__ package will continue to be available.

Introduction
~~~~~~~~~~~~

.. image:: https://circleci.com/gh/EducationalTestingService/python-zpar.svg?style=shield
   :alt: CircleCI Build status
   :target: https://circleci.com/gh/EducationalTestingService/python-zpar

**python-zpar** is a python wrapper around the `ZPar
parser <http://www.sutd.edu.sg/cmsresource/faculty/yuezhang/zpar.html>`__.
ZPar was written by `Yue Zhang <http://www.sutd.edu.sg/yuezhang.aspx>`__
while he was at Oxford University. According to its home page: *ZPar is
a statistical natural language parser, which performs syntactic analysis
tasks including word segmentation, part-of-speech tagging and parsing.
ZPar supports multiple languages and multiple grammar formalisms. ZPar
has been most heavily developed for Chinese and English, while it
provides generic support for other languages. ZPar is fast, processing
above 50 sentences per second using the standard Penn Teebank (Wall
Street Journal) data.*

I wrote python-zpar since I needed a fast and efficient parser for my
NLP work which is primarily done in Python and not C++. I wanted to be
able to use this parser directly from Python without having to create a
bunch of files and running them through subprocesses. python-zpar not
only provides a simply python wrapper but also provides an XML-RPC ZPar
server to make batch-processing of large files easier.

python-zpar uses
`ctypes <https://docs.python.org/3.4/library/ctypes.html>`__, a very
cool foreign function library bundled with Python that allows calling
functions in C DLLs or shared libraries directly.

**IMPORTANT**: As of now, python-zpar only works with the English zpar models
since the interface to the Chinese models is different than the English ones.
Pull requests are welcome!

Installation
~~~~~~~~~~~~

Currently, python-zpar only works on 64-bit linux and OS X systems.
Those are the two platforms I use everyday. I am happy to try to get
python-zpar working on other platforms over time. Pull requests are
welcome!

Please make sure that ``make`` and ``wget`` are installed as they are both needed to properly build python-zpar.

In order for python-zpar to work, it requires C functions that can be
called directly. Since the only user-exposed entry point in ZPar is the
command line client, I needed to write a shared library that would have
functions built on top of the ZPar functionality but expose them in a
way that ctypes could understand.

Therefore, in order to build python-zpar from scratch, we need to
download the ZPar source, patch it with new functionality and compile
the shared library. All of this happens automatically when you install
with pip:

.. code-block:: bash

    pip install python-zpar


IF YOU ARE USING macOS
======================

1. On macOS, the installation will only work with ``gcc`` installed using either `macports <http://www.macports.org>`__ or `homebrew <http://brew.sh/>`__. The zpar source cannot be compiled with ``clang``. If you are having trouble compiling the code after cloning the repository or installing the package using pip, you can try to explicitly override the C++ compiler:

    .. code-block:: bash

        CXX=<path to c++ compiler> make -e

    or

    .. code-block:: bash

        CXX=<path to c++ compiler> pip install python-zpar


    If you are curious about what the C functions in the shared library
    module look like, see ``src/zpar.lib.cpp``.

2. If you are using macOS Mojave, you will need an extra step before running the ``pip`` install command above. Starting with Mojave, Apple has stopped installing the C/C++ system header files into ``/usr/include``. As a workaround, they have provided the package ``/Library/Developer/CommandLineTools/Packages/macOS_SDK_headers_for_macOS_10.14.pkg`` that you must install to get the system headers back in the usual place before python-zpar can be compiled. For more details, please read the Command Line Tools section of the `Xcode 10 release notes <https://developer.apple.com/documentation/xcode_release_notes/xcode_10_release_notes>`__

3. If you are using macOS Catalina, python-zpar is currently `broken <https://github.com/EducationalTestingService/python-zpar/issues/29>`__. I have not yet upgraded to Catalina on my production machine and cannot figure out a fix yet. If you have a suggested fix, please reply in the issue. 

Usage
~~~~~

To use python-zpar, you need the English models for ZPar. They can be
downloaded from the ZPar release page `here <https://github.com/frcchang/zpar/releases/tag/v0.7.5>`__.
There are three models: a part-of-speech tagger, a constituency parser, and a
dependency parser. For the purpose of the examples below, the models are
in the ``english-models`` directory in the current directory.

Here's a small example of how to use python-zpar:

.. code-block:: python

    from six import print_
    from zpar import ZPar

    # use the zpar wrapper as a context manager
    with ZPar('english-models') as z:

        # get the parser and the dependency parser models
        tagger = z.get_tagger()
        depparser = z.get_depparser()

        # tag a sentence
        tagged_sent = tagger.tag_sentence("I am going to the market.")
        print_(tagged_sent)

        # tag an already tokenized sentence
        tagged_sent = tagger.tag_sentence("Do n't you want to come with me to the market ?", tokenize=False)
        print_(tagged_sent)

        # get the dependency parse of an already tagged sentence
        dep_parsed_sent = depparser.dep_parse_tagged_sentence("I/PRP am/VBP going/VBG to/TO the/DT market/NN ./.")
        print_(dep_parsed_sent)

        # get the dependency parse of an already tokenized sentence
        dep_parsed_sent = depparser.dep_parse_sentence("Do n't you want to come with me to the market ?", tokenize=False)
        print_(dep_parsed_sent)

        # get the dependency parse of an already tokenized sentence
        # and include lemma information (assuming you have NLTK as well
        # as its WordNet corpus installed)
        dep_parsed_sent = depparser.dep_parse_sentence("Do n't you want to come with me to the market ?", tokenize=False, with_lemmas=True)
        print_(dep_parsed_sent)


The above code sample produces the following output:

.. code-block::

    I/PRP am/VBP going/VBG to/TO the/DT market/NN ./.

    Do/VBP n't/RB you/PRP want/VBP to/TO come/VB with/IN me/PRP to/TO the/DT market/NN ?/.

    I       PRP   1    SUB
    am      VBP   -1   ROOT
    going   VBG   1    VC
    to      TO    2    VMOD
    the     DT    5    NMOD
    market  NN    3    PMOD
    .       .     1    P

    Do      VBP  -1  ROOT
    n't     RB   0   VMOD
    you     PRP  0   SUB
    want    VBP  0   VMOD
    to      TO   5   VMOD
    come    VB   3   VMOD
    with    IN   5   VMOD
    me      PRP  6   PMOD
    to      TO   5   VMOD
    the     DT   10  NMOD
    market  NN   8   PMOD
    ?       .    0   P

    Do      VBP  -1  ROOT   do
    n't     RB   0   VMOD   n't
    you     PRP  0   SUB    you
    want    VBP  0   VMOD   want
    to      TO   5   VMOD   to
    come    VB   3   VMOD   come
    with    IN   5   VMOD   with
    me      PRP  6   PMOD   me
    to      TO   5   VMOD   to
    the     DT   10  NMOD   the
    market  NN   8   PMOD   market
    ?       .    0   P      ?


Detailed usage with comments is shown in the included file
``examples/zpar_example.py``. Run ``python zpar_example.py -h`` to see a
list of all available options.

ZPar Server
~~~~~~~~~~~

The package also provides an python XML-RPC implementation of a ZPar
server that makes it easier to process multiple sentences and files by
loading the models just once (via the ctypes interface) and allowing
clients to connect and request analyses. The implementation is in the
executable ``zpar_server`` that is installed when you install the
package. The server is quite flexible and allows loading only the
models that you need. Here's an example of how to start the server
with only the tagger and the dependency parser models loaded:

.. code-block::

    $> zpar_server --modeldir english-models --models tagger parser depparser
    INFO:Initializing server ...
    Loading tagger from english-models/tagger
    Loading model... done.
    Loading constituency parser from english-models/conparser
    Loading scores... done. (65.9334s)
    Loading dependency parser from english-models/depparser
    Loading scores... done. (14.9623s)
    INFO:Registering introspection ...
    INFO:Starting server on port 8859...

Run ``zpar_server -h`` to see a list of all options.

Once the server is running, you can connect to it using a client. An
example client is included in the file ``examples/zpar_client.py`` which
can be run as follows (note that if you specified a custom host and port
when running the server, you'd need to specify the same here):

.. code-block::

    $> cd examples
    $> python zpar_client.py

    INFO:Attempting connection to http://localhost:8859
    INFO:Tagging "Don't you want to come with me to the market?"
    INFO:Output: Do/VBP n't/RB you/PRP want/VBP to/TO come/VB with/IN me/PRP to/TO the/DT market/NN ?/.
    INFO:Tagging "Do n't you want to come to the market with me ?"
    INFO:Output: Do/VBP n't/RB you/PRP want/VBP to/TO come/VB to/TO the/DT market/NN with/IN me/PRP ?/.
    INFO:Parsing "Don't you want to come with me to the market?"
    INFO:Output: (SQ (VBP Do) (RB n't) (NP (PRP you)) (VP (VBP want) (S (VP (TO to) (VP (VB come) (PP (IN with) (NP (PRP me))) (PP (TO to) (NP (DT the) (NN market))))))) (. ?))
    INFO:Dep Parsing "Do n't you want to come to the market with me ?"
    INFO:Output: Do VBP -1  ROOT
    n't RB  0   VMOD
    you PRP 0   SUB
    want    VBP 0   VMOD
    to  TO  5   VMOD
    come    VB  3   VMOD
    to  TO  5   VMOD
    the DT  8   NMOD
    market  NN  6   PMOD
    with    IN  5   VMOD
    me  PRP 9   PMOD
    ?   .   0   P

    INFO:Tagging file /Users/nmadnani/work/python-zpar/examples/test.txt into test.tag
    INFO:Parsing file /Users/nmadnani/work/python-zpar/examples/test_tokenized.txt into test.parse


Note that python-zpar and all of the example scripts should work with
both Python 2.7 and Python 3.4. I have tested python-zpar on both Linux
and Mac but not on Windows.

Node.js version
~~~~~~~~~~~~~~~

If you want to use ZPar in your node.js app, check out my other project
`node-zpar <http://github.com/EducationalTestingService/node-zpar>`__.

License
~~~~~~~

Although python-zpar is licensed under the MIT license - which means
that you can do whatever you want with the wrapper code - ZPar itself is
licensed under GPL v3.

ToDo
~~~~

1. Improve error handling on both the python and C side.
2. Expose more functionality, e.g., Chinese word segmentation, parsing
   etc.
3. May be look into using `CFFI <https://cffi.readthedocs.org/>`__
   instead of ctypes.

