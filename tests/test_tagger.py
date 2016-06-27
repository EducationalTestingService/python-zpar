"""
Run unit tests for the ZPar tagger.

:author: Nitin Madnani (nmadnani@ets.org)
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import glob
import os

from io import open
from os.path import abspath, dirname, join

from nose.tools import assert_equal
from zpar import ZPar

_my_dir = abspath(dirname(__file__))

z = None
tagger = None

def setUp():
    """
    set up things we need for the tests
    """
    global z, tagger

    assert 'ZPAR_MODEL_DIR' in os.environ

    model_dir = os.environ['ZPAR_MODEL_DIR']

    z = ZPar(model_dir)
    tagger = z.get_tagger()

def tearDown():
    """
    Clean up after the tests
    """
    global z, tagger

    if z:
        z.close()
        del tagger
        del z

    # delete all the files we may have created
    data_dir = abspath(join(_my_dir, '..', 'examples'))
    for f in glob.glob(join(data_dir, 'test*.tag')):
        os.unlink(f)


def check_tag_sentence(tokenize=False):
    """
    Check tag_sentence method with and without tokenization
    """
    global tagger

    sentence = "I'm going to the market." if tokenize else "I 'm going to the market ."
    correct_output = "I/PRP 'm/VBP going/VBG to/TO the/DT market/NN ./."
    tagged_sentence = tagger.tag_sentence(sentence, tokenize=tokenize)

    assert_equal(tagged_sentence, correct_output)


def test_tag_sentence():
    yield check_tag_sentence, False
    yield check_tag_sentence, True


def check_tag_file(tokenize=False):
    """
    Check tag_file method with and without tokenization
    """

    global tagger

    prefix = 'test' if tokenize else 'test_tokenized'

    correct_output = ['I/PRP am/VBP going/VBG to/TO the/DT market/NN ./.',
                      'Are/VBP you/PRP going/VBG to/TO come/VB with/IN me/PRP ?/.']

    input_file = abspath(join(_my_dir, '..', 'examples', '{}.txt'.format(prefix)))
    output_file = abspath(join(_my_dir, '..', 'examples', '{}.tag'.format(prefix)))

    # tag the file
    tagger.tag_file(input_file, output_file, tokenize=tokenize)

    # read the output file and make sure we have the expected output
    with open(output_file, 'r') as outf:
        output = [l.strip() for l in outf.readlines()]

    assert_equal(output, correct_output)


def test_tag_file():
    yield check_tag_file, False
    yield check_tag_file, True
