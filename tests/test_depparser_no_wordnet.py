""" "
Run unit tests for the ZPar dependency parser.

:author: Nitin Madnani (nmadnani@ets.org)
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from io import open
from itertools import product
from os.path import abspath, dirname, join

from nose.tools import assert_equal

_my_dir = abspath(dirname(__file__))

def check_dep_parse_sentence_no_wordnet(tokenize=False,
                                        with_lemmas=False,
                                        tagged=False):
    """
    Check dep_parse_sentence method with and without tokenization,
    with and without lemmas, and with and without pre-tagged output,
    all under the condition that there is no wordnet corpus
    accessible to nltk.
    """
    from tests import depparser

    if tagged:
        sentence = "I/PRP 'm/VBP going/VBG to/TO the/DT market/NN ./."
    else:
        if tokenize:
            sentence = "I'm going to the market."
        else:
            sentence = "I 'm going to the market ."

    correct_output = "I\tPRP\t1\tSUB\n'm\tVBP\t-1\tROOT\ngoing\tVBG\t1\tVC\nto\tTO\t2\tVMOD\nthe\tDT\t5\tNMOD\nmarket\tNN\t3\tPMOD\n.\t.\t1\tP\n"
    if not tagged:
        parsed_sentence = depparser.dep_parse_sentence(sentence,
                                                       tokenize=tokenize,
                                                       with_lemmas=with_lemmas)
    else:
        parsed_sentence = depparser.dep_parse_tagged_sentence(sentence,
                                                              with_lemmas=with_lemmas)

    assert_equal(parsed_sentence, correct_output)


def test_dep_parse_sentence_no_wordnet():
    for (tokenize, with_lemmas, tagged) in product([True, False],
                                                       [True, False],
                                                       [True, False]):
        yield (check_dep_parse_sentence_no_wordnet,
               tokenize,
               with_lemmas,
               tagged)


def check_dep_parse_file_no_wordnet(tokenize=False,
                                    with_lemmas=False,
                                    tagged=False):
    """
    Check parse_file method with and without tokenization,
    with and without lemmas, and with and without pre-tagged output,
    all under the condition that there is no wordnet corpus
    accessible to nltk.
    """
    from tests import depparser

    if tagged:
        prefix = 'test_tagged'
    else:
        if tokenize:
            prefix = 'test'
        else:
            prefix = 'test_tokenized'

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
    if not tagged:
        depparser.dep_parse_file(input_file,
                                 output_file,
                                 tokenize=tokenize,
                                 with_lemmas=with_lemmas)
    else:
        depparser.dep_parse_tagged_file(input_file,
                                        output_file,
                                        with_lemmas=with_lemmas)

    # read the output file and make sure we have the expected output
    with open(output_file, 'r') as outf:
        output = [l.strip() for l in outf.readlines()]

    assert_equal(output, correct_output)


def test_dep_parse_file_no_wordnet():
    for (tokenize, with_lemmas, tagged) in product([True, False],
                                                   [True, False],
                                                   [True, False]):
        yield (check_dep_parse_file_no_wordnet,
               tokenize,
               with_lemmas,
               tagged)

