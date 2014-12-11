"""
Module for running a bunch of simple unit tests. Should be expanded more in
the future.

:author: Nitin Madnani (nmadnani@ets.org)
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import glob
import itertools
import os

from io import open
from os.path import abspath, dirname, exists, join

from zpar import ZPar

_my_dir = abspath(dirname(__file__))

z = None
tagger = None
parser = None
depparser = None


def setUp():
    """
    set up things we need for the tests
    """
    global z, tagger, parser, depparser

    assert 'ZPAR_MODEL_DIR' in os.environ

    model_dir = os.environ['ZPAR_MODEL_DIR']

    z = ZPar(model_dir)
    tagger = z.get_tagger()
    parser = z.get_parser()
    depparser = z.get_depparser()


def tearDown():
    """
    Clean up after the tests
    """
    global z, tagger, parser, depparser

    if z:
        z.close()
        del tagger
        del parser
        del depparser
        del z

    # delete all the files we may have created
    data_dir = abspath(join(_my_dir, '..', 'examples'))
    for f in glob.glob(join(data_dir, 'test*.tag')):
        os.unlink(f)
    for f in glob.glob(join(data_dir, 'test*.parse')):
        os.unlink(f)
    for f in glob.glob(join(data_dir, 'test*.dep')):
        os.unlink(f)
