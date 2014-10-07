# License: MIT
'''
:author: Nitin Madnani (nmadnani@ets.org)
:organization: ETS
'''

import ctypes as c
import os

class Parser(object):
    """The ZPar English Constituency Parser"""

    def __init__(self, modelpath, libptr):
        super(Parser, self).__init__()

        # get the library method that loads the parser models
        self._load_parser = libptr.load_parser
        self._load_parser.restype = c.c_int
        self._load_parser.argtypes = [c.c_char_p]

        # get the library methods that parse sentences and files
        self._parse_sentence = libptr.parse_sentence
        self._parse_sentence.restype = c.c_char_p
        self._parse_sentence.argtypes = [c.c_char_p]

        self._parse_file = libptr.parse_file
        self._parse_file.restype = None
        self._parse_file.argtypes = [c.c_char_p, c.c_char_p]

        if self._load_parser(modelpath.encode('utf-8')):
            raise OSError('Cannot find parser model at {}\n'.format(modelpath))

    def parse_sentence(self, sentence):
        zpar_compatible_sentence = sentence.strip() + "\n "
        zpar_compatible_sentence = zpar_compatible_sentence.encode('utf-8')
        parsed_sent = self._parse_sentence(zpar_compatible_sentence)
        return parsed_sent.decode('utf-8')

    def parse_file(self, inputfile, outputfile):
        if os.path.exists(inputfile):
            self._parse_file(inputfile.encode('utf-8'), outputfile.encode('utf-8'))
        else:
            raise OSError('File {} does not exist.'.format(inputfile))

    def cleanup(self):
        self._load_parser = None
        self._parse_sentence = None
        self._parse_file = None
