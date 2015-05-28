# License: MIT
'''
:author: Nitin Madnani (nmadnani@ets.org)
:organization: ETS
'''

import ctypes as c
import logging
import os
import re

# set up the logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

class Parser(object):
    """The ZPar English Constituency Parser"""

    def __init__(self, modelpath, libptr, zpar_session_obj):
        super(Parser, self).__init__()

        # save the zpar session object
        self._zpar_session_obj = zpar_session_obj

        # set up a logger
        self.logger = logging.getLogger(__name__)

        # get the library method that loads the parser models
        self._load_parser = libptr.load_parser
        self._load_parser.restype = c.c_int
        self._load_parser.argtypes = [c.c_void_p, c.c_char_p]

        # get the library methods that parse sentences and files
        self._parse_sentence = libptr.parse_sentence
        self._parse_sentence.restype = c.c_char_p
        self._parse_sentence.argtypes = [c.c_void_p, c.c_char_p, c.c_bool]

        self._parse_file = libptr.parse_file
        self._parse_file.restype = None
        self._parse_file.argtypes = [c.c_void_p, c.c_char_p, c.c_char_p, c.c_bool]

        self._parse_tagged_sentence = libptr.parse_tagged_sentence
        self._parse_tagged_sentence.restype = c.c_char_p
        self._parse_tagged_sentence.argtypes = [c.c_void_p, c.c_char_p, c.c_char]

        self._parse_tagged_file = libptr.parse_tagged_file
        self._parse_tagged_file.restype = None
        self._parse_tagged_file.argtypes = [c.c_void_p, c.c_char_p, c.c_char_p, c.c_char]

        if self._load_parser(self._zpar_session_obj, modelpath.encode('utf-8')):
            raise OSError('Cannot find parser model at {}\n'.format(modelpath))

    def parse_sentence(self, sentence, tokenize=True):
        if not sentence.strip():
            # return empty string if the input is empty
            ans = ""
        else:
            zpar_compatible_sentence = sentence
            all_caps_word = ''
            # detect if we are processing a sentence with a single word in all caps
            # because that is a known bug. This is a hack for now and will be removed
            # once the underlying bug is fixed in ZPar.
            m = re.match(r'^([A-Z]+)$', zpar_compatible_sentence.strip())
            if m:
                all_caps_word = m.group(1)
                fixed_word = all_caps_word.title()
                self.logger.warning('Encountered sentence with all caps single word '
                                    'which triggers a known bug in ZPar. Title-casing '
                                    'to avoid buggy behavior.')
                zpar_compatible_sentence = sentence.title()
            zpar_compatible_sentence = zpar_compatible_sentence.strip() + "\n "
            zpar_compatible_sentence = zpar_compatible_sentence.encode('utf-8')
            parsed_sent = self._parse_sentence(self._zpar_session_obj, zpar_compatible_sentence, tokenize)
            # replace the title-cased word with the original all-caps word if we need to
            parsed_sent = parsed_sent.decode('utf-8')
            ans = parsed_sent if not all_caps_word else parsed_sent.replace(fixed_word, all_caps_word)

        return ans

    def parse_file(self, inputfile, outputfile, tokenize=True):
        if os.path.exists(inputfile):
            self._parse_file(self._zpar_session_obj, inputfile.encode('utf-8'), outputfile.encode('utf-8'), tokenize)
        else:
            raise OSError('File {} does not exist.'.format(inputfile))

    def parse_tagged_sentence(self, tagged_sentence, sep='/'):
        if not tagged_sentence.strip():
            # return empty string if the input is empty
            ans = ""
        else:
            zpar_compatible_sentence = tagged_sentence.strip().encode('utf-8')
            parsed_sent = self._parse_tagged_sentence(self._zpar_session_obj, zpar_compatible_sentence, sep.encode('utf-8'))
            ans = parsed_sent.decode('utf-8')
        return ans

    def parse_tagged_file(self, inputfile, outputfile, sep='/'):
        if os.path.exists(inputfile):
            self._parse_tagged_file(self._zpar_session_obj, inputfile.encode('utf-8'), outputfile.encode('utf-8'), sep.encode('utf-8'))
        else:
            raise OSError('File {} does not exist.'.format(inputfile))

    def cleanup(self):
        self._load_parser = None
        self._parse_sentence = None
        self._parse_file = None
        self._parse_tagged_sentence = None
        self._parse_tagged_file = None
        self._zpar_session_obj = None
