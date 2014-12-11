# License: MIT
'''
:author: Nitin Madnani (nmadnani@ets.org)
:organization: ETS
'''

import ctypes as c
import os

class DepParser(object):
    """The ZPar English Dependency Parser"""

    def __init__(self, modelpath, libptr, zpar_session_obj):
        super(DepParser, self).__init__()

        # save the zpar session object
        self._zpar_session_obj = zpar_session_obj

        # get the library method that loads the parser models
        self._load_depparser = libptr.load_depparser
        self._load_depparser.restype = c.c_int
        self._load_depparser.argtypes = [c.c_void_p, c.c_char_p]

        # get the library methods that parse sentences and files
        self._dep_parse_sentence = libptr.dep_parse_sentence
        self._dep_parse_sentence.restype = c.c_char_p
        self._dep_parse_sentence.argtypes = [c.c_void_p, c.c_char_p, c.c_bool]

        self._dep_parse_file = libptr.dep_parse_file
        self._dep_parse_file.restype = None
        self._dep_parse_file.argtypes = [c.c_void_p, c.c_char_p, c.c_char_p, c.c_bool]

        self._dep_parse_tagged_sentence = libptr.dep_parse_tagged_sentence
        self._dep_parse_tagged_sentence.restype = c.c_char_p
        self._dep_parse_tagged_sentence.argtypes = [c.c_void_p, c.c_char_p, c.c_char]

        self._dep_parse_tagged_file = libptr.dep_parse_tagged_file
        self._dep_parse_tagged_file.restype = None
        self._dep_parse_tagged_file.argtypes = [c.c_void_p, c.c_char_p, c.c_char_p, c.c_char]

        if self._load_depparser(self._zpar_session_obj, modelpath.encode('utf-8')):
            raise OSError('Cannot find dependency parser model at {}\n'.format(modelpath))

    def dep_parse_sentence(self, sentence, tokenize=True):
        if not sentence.strip():
            # return empty string if the input is empty
            ans = ""
        else:
            zpar_compatible_sentence = sentence.strip() + "\n "
            zpar_compatible_sentence = zpar_compatible_sentence.encode('utf-8')
            parsed_sent = self._dep_parse_sentence(self._zpar_session_obj, zpar_compatible_sentence, tokenize)
            ans = parsed_sent.decode('utf-8')

        return ans

    def dep_parse_file(self, inputfile, outputfile, tokenize=True):
        if os.path.exists(inputfile):
            self._dep_parse_file(self._zpar_session_obj, inputfile.encode('utf-8'), outputfile.encode('utf-8'), tokenize)
        else:
            raise OSError('File {} does not exist.'.format(inputfile))

    def dep_parse_tagged_sentence(self, tagged_sentence, sep='/'):
        if not tagged_sentence.strip():
            # return empty string if the input is empty
            ans = ""
        else:
            zpar_compatible_sentence = tagged_sentence.strip().encode('utf-8')
            parsed_sent = self._dep_parse_tagged_sentence(self._zpar_session_obj, zpar_compatible_sentence, sep.encode('utf-8'))
            ans = parsed_sent.decode('utf-8')
        return ans

    def dep_parse_tagged_file(self, inputfile, outputfile, sep='/'):
        if os.path.exists(inputfile):
            self._dep_parse_tagged_file(self._zpar_session_obj, inputfile.encode('utf-8'), outputfile.encode('utf-8'), sep.encode('utf-8'))
        else:
            raise OSError('File {} does not exist.'.format(inputfile))

    def cleanup(self):
        self._load_depparser = None
        self._dep_parse_sentence = None
        self._parse_file = None
        self._zpar_session_obj = None
