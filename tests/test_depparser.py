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


def check_dep_parse_sentence(tokenize=False):
    """
    Check dep_parse_sentence method with and without tokenization
    """
    from tests import depparser

    sentence = "I'm going to the market." if tokenize else "I 'm going to the market ."
    correct_output = "I\tPRP\t1\tSUB\n'm\tVBP\t-1\tROOT\ngoing\tVBG\t1\tVC\nto\tTO\t2\tVMOD\nthe\tDT\t5\tNMOD\nmarket\tNN\t3\tPMOD\n.\t.\t1\tP\n"
    parsed_sentence = depparser.dep_parse_sentence(sentence, tokenize=tokenize)
    assert_equal(parsed_sentence, correct_output)


def test_dep_parse_sentence():
    yield check_dep_parse_sentence, False
    yield check_dep_parse_sentence, True


def check_dep_parse_file(tokenize=False):
    """
    Check parse_file method with and without tokenization
    """

    from tests import depparser

    prefix = 'test' if tokenize else 'test_tokenized'

    correct_output = ['I\tPRP\t1\tSUB', 'am\tVBP\t-1\tROOT',
                      'going\tVBG\t1\tVC', 'to\tTO\t2\tVMOD',
                      'the\tDT\t5\tNMOD', 'market\tNN\t3\tPMOD',
                      '.\t.\t1\tP', '', 'Are\tVBP\t-1\tROOT',
                      'you\tPRP\t0\tSUB', 'going\tVBG\t0\tVMOD',
                      'to\tTO\t4\tVMOD', 'come\tVB\t2\tVMOD',
                      'with\tIN\t4\tVMOD', 'me\tPRP\t5\tPMOD',
                      '?\t.\t0\tP', '']

    input_file = abspath(join(_my_dir, '..', 'examples', '{}.txt'.format(prefix)))
    output_file = abspath(join(_my_dir, '..', 'examples', '{}.dep'.format(prefix)))

    # dependency parse the file
    depparser.dep_parse_file(input_file, output_file, tokenize=tokenize)

    # read the output file and make sure we have the expected output
    with open(output_file, 'r') as outf:
        output = [l.strip() for l in outf.readlines()]

    assert_equal(output, correct_output)


def test_dep_parse_file():
    yield check_dep_parse_file, False
    yield check_dep_parse_file, True
