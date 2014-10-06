# License: MIT
'''
:author: Nitin Madnani (nmadnani@ets.org)
:organization: ETS
'''

import _ctypes
import ctypes as c
import os

from .Tagger import Tagger
from .Parser import Parser
from .DepParser import DepParser

__all__ = ['Tagger', 'Parser', 'DepParser']

class ZPar(object):
    """The ZPar wrapper object"""

    def __init__(self, modelpath):
        super(ZPar, self).__init__()

        # get a pointer to the zpar shared library
        base_path = os.path.dirname(os.path.abspath(__file__))
        zpar_path = os.path.join(base_path, 'dist', 'zpar.so')
        self.libptr = c.cdll.LoadLibrary(zpar_path)
        self.modelpath = modelpath
        self.tagger = None
        self.parser = None
        self.depparser = None

    def close(self):
        # unload the models on the C++ side
        self.libptr.unload_models()

        # clean up the data structures on the python side
        if self.tagger:
            self.tagger.cleanup()

        if self.parser:
            self.parser.cleanup()

        if self.depparser:
            self.depparser.cleanup()

        # set all the fields to none to enable clean reuse
        self.tagger = None
        self.parser = None
        self.depparser = None
        self.modelpath = None

        # clean up the CDLL object too so that upon reuse, we get a new one
        _ctypes.dlclose(self.libptr._handle)
        # pretty sure once the old object libptr was pointed to should
        # get garbage collected at some point after this
        self.libptr = None

    def __enter__(self):
        """Enable ZPar to be used as a ContextManager"""
        return self

    def __exit__(self, type, value, traceback):
        """Clean up when done"""
        self.close()

    def get_tagger(self):
        if not self.libptr:
            raise Exception('Cannot get tagger from uninitialized ZPar environment.')
            return None
        else:
            self.tagger = Tagger(self.modelpath, self.libptr)
            return self.tagger

    def get_parser(self):
        if not self.libptr:
            raise Exception('Cannot get parser from uninitialized ZPar environment.')
            return None
        else:
            self.parser = Parser(self.modelpath, self.libptr)
            return self.parser

    def get_depparser(self):
        if not self.libptr:
            raise Exception('Cannot get parser from uninitialized ZPar environment.')
            return None
        else:
            self.depparser = DepParser(self.modelpath, self.libptr)
            return self.depparser

