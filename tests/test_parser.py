"""
Run unit tests for the ZPar constituency parser.

:author: Nitin Madnani (nmadnani@ets.org)
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import glob
import os

from io import open
from itertools import product
from os.path import abspath, dirname, join

from nose.tools import assert_equal
from zpar import ZPar

_my_dir = abspath(dirname(__file__))

z = None
parser = None


def setUp():
    """
    set up things we need for the tests
    """
    global z, parser

    assert 'ZPAR_MODEL_DIR' in os.environ

    model_dir = os.environ['ZPAR_MODEL_DIR']

    z = ZPar(model_dir)
    parser = z.get_parser()


def tearDown():
    """
    Clean up after the tests
    """
    global z, parser

    if z:
        z.close()
        del parser
        del z

    # delete all the files we may have created
    data_dir = abspath(join(_my_dir, '..', 'examples'))
    for f in glob.glob(join(data_dir, 'test*.parse')):
        os.unlink(f)


def check_parse_sentence(tokenize=False, tagged=False):
    """
    Check parse_sentence method with and without tokenization
    and with and without pre-tagged output.
    """
    global parser

    if tagged:
        sentence = "I/PRP 'm/VBP going/VBG to/TO the/DT market/NN ./."
    else:
        if tokenize:
            sentence = "I'm going to the market."
        else:
            sentence = "I 'm going to the market ."

    correct_output = "(S (NP (PRP I)) (VP (VBP 'm) (VP (VBG going) (PP (TO to) (NP (DT the) (NN market))))) (. .))"

    if not tagged:
        parsed_sentence = parser.parse_sentence(sentence, tokenize=tokenize)
    else:
        parsed_sentence = parser.parse_tagged_sentence(sentence)

    assert_equal(parsed_sentence, correct_output)


def test_parse_sentence():
    for (tokenize, tagged) in product([True, False], [True, False]):
        yield check_parse_sentence, tokenize, tagged


def check_parse_file(tokenize=False, tagged=False):
    """
    Check parse_file method with and without tokenization
    and with and without pre-tagged output
    """
    global parser

    if tagged:
        prefix = 'test_tagged'
    else:
        if tokenize:
            prefix = 'test'
        else:
            prefix = 'test_tokenized'

    correct_output = ["(S (NP (PRP I)) (VP (VBP am) (VP (VBG going) (PP (TO to) (NP (DT the) (NN market))))) (. .))",
                      "(SQ (VBP Are) (NP (PRP you)) (VP (VBG going) (S (VP (TO to) (VP (VB come) (PP (IN with) (NP (PRP me))))))) (. ?))"]

    input_file = abspath(join(_my_dir, '..', 'examples', '{}.txt'.format(prefix)))
    output_file = abspath(join(_my_dir, '..', 'examples', '{}.parse'.format(prefix)))

    # parse the file
    if not tagged:
        parser.parse_file(input_file, output_file, tokenize=tokenize)
    else:
        parser.parse_tagged_file(input_file, output_file)

    # read the output file and make sure we have the expected output
    with open(output_file, 'r') as outf:
        output = [l.strip() for l in outf.readlines()]

    assert_equal(output, correct_output)


def test_parse_file():
    for (tokenize, tagged) in product([True, False], [True, False]):
        yield check_parse_file, tokenize, tagged

