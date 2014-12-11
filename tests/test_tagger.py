"""
Module for running a bunch of simple unit tests. Should be expanded more in
the future.

:author: Nitin Madnani (nmadnani@ets.org)
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import itertools
import os

from io import open
from os.path import abspath, dirname, exists, join

import numpy as np
from nose.tools import eq_, raises, assert_equal, assert_not_equal

_my_dir = abspath(dirname(__file__))


def check_tag_sentence(tokenize=False):
    """
    Check tag_sentence method with and without tokenization
    """
    from tests import tagger

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

    from tests import tagger

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
