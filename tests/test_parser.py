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


def check_parse_sentence(tokenize=False):
    """
    Check parse_sentence method with and without tokenization
    """
    from tests import parser

    sentence = "I'm going to the market." if tokenize else "I 'm going to the market ."
    correct_output = "(S (NP (PRP I)) (VP (VBP 'm) (VP (VBG going) (PP (TO to) (NP (DT the) (NN market))))) (. .))"
    parsed_sentence = parser.parse_sentence(sentence, tokenize=tokenize)

    assert_equal(parsed_sentence, correct_output)


def test_parse_sentence():
    yield check_parse_sentence, False
    yield check_parse_sentence, True


def test_zpar_bugfix_parse():
    from tests import parser

    sentences = ['REBELLION',
                 'I am going away .',
                 'The rebellion is just another word for change and change is necessary to live .',
                 'REBELLION',
                 'REBELLION',
                 'The rebellion is just another word for change and change is necessary to live .',
                 'REBELLION',
                 'This is just another sentence .',
                 'REBELLION']

    # tag the above sentences
    parsed_sentences = [parser.parse_sentence(s) for s in sentences]

    # get the parses for all of the all-caps single-word sentences
    # and make sure they are all the same
    indices_to_check = [0, 3, 4, 6, 8]
    parses_to_check = [parsed_sentences[i] for i in indices_to_check]
    assert_equal(set(parses_to_check), {'(NP (NNP REBELLION))'})


def check_parse_file(tokenize=False):
    """
    Check parse_file method with and without tokenization
    """

    from tests import parser

    prefix = 'test' if tokenize else 'test_tokenized'

    correct_output = ["(S (NP (PRP I)) (VP (VBP am) (VP (VBG going) (PP (TO to) (NP (DT the) (NN market))))) (. .))",
                      "(SQ (VBP Are) (NP (PRP you)) (VP (VBG going) (S (VP (TO to) (VP (VB come) (PP (IN with) (NP (PRP me))))))) (. ?))"]

    input_file = abspath(join(_my_dir, '..', 'examples', '{}.txt'.format(prefix)))
    output_file = abspath(join(_my_dir, '..', 'examples', '{}.parse'.format(prefix)))

    # parse the file
    parser.parse_file(input_file, output_file, tokenize=tokenize)

    # read the output file and make sure we have the expected output
    with open(output_file, 'r') as outf:
        output = [l.strip() for l in outf.readlines()]

    assert_equal(output, correct_output)


def test_parse_file():
    yield check_parse_file, False
    yield check_parse_file, True


def test_parse_tagged_sentence():
    from tests import parser

    tagged_sentence = "I/PRP 'm/VBP going/VBG to/TO the/DT market/NN ./."
    correct_output = "(S (NP (PRP I)) (VP (VBP 'm) (VP (VBG going) (PP (TO to) (NP (DT the) (NN market))))) (. .))"
    parsed_sentence = parser.parse_tagged_sentence(tagged_sentence)

    assert_equal(parsed_sentence, correct_output)


def test_parse_tagged_file():

    from tests import parser

    correct_output = ["(S (NP (PRP I)) (VP (VBP am) (VP (VBG going) (PP (TO to) (NP (DT the) (NN market))))) (. .))",
                      "(SQ (VBP Are) (NP (PRP you)) (VP (VBG going) (S (VP (TO to) (VP (VB come) (PP (IN with) (NP (PRP me))))))) (. ?))"]

    input_file = abspath(join(_my_dir, '..', 'examples', 'test_tagged.txt'))
    output_file = abspath(join(_my_dir, '..', 'examples', 'test_tagged.parse'))

    # parse the file
    parser.parse_tagged_file(input_file, output_file)

    # read the output file and make sure we have the expected output
    with open(output_file, 'r') as outf:
        output = [l.strip() for l in outf.readlines()]

    assert_equal(output, correct_output)
