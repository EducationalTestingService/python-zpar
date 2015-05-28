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


class Tagger(object):
    """The ZPar English POS Tagger"""

    def __init__(self, modelpath, libptr, zpar_session_obj):
        super(Tagger, self).__init__()

        # save the zpar session object
        self._zpar_session_obj = zpar_session_obj

        # set up a logger
        self.logger = logging.getLogger(__name__)

        # get the library method that loads the tagger models
        self._load_tagger = libptr.load_tagger
        self._load_tagger.restype = c.c_int
        self._load_tagger.argtypes = [c.c_void_p, c.c_char_p]

        # get the library methods that tag sentences and files
        self._tag_sentence = libptr.tag_sentence
        self._tag_sentence.restype = c.c_char_p
        self._tag_sentence.argtypes = [c.c_void_p, c.c_char_p, c.c_bool]

        self._tag_file = libptr.tag_file
        self._tag_file.restype = None
        self._tag_file.argtypes = [c.c_void_p, c.c_char_p, c.c_char_p, c.c_bool]

        if self._load_tagger(self._zpar_session_obj, modelpath.encode('utf-8')):
            raise OSError('Cannot find tagger model at {}\n'.format(modelpath))

    def tag_sentence(self, sentence, tokenize=True):
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
            tagged_sent = self._tag_sentence(self._zpar_session_obj, zpar_compatible_sentence, tokenize)
            # replace the title-cased word with the original all-caps word if we need to
            tagged_sent = tagged_sent.decode('utf-8')
            ans = tagged_sent if not all_caps_word else tagged_sent.replace(fixed_word, all_caps_word)

        return ans

    def tag_file(self, inputfile, outputfile, tokenize=True):
        if os.path.exists(inputfile):
            self._tag_file(self._zpar_session_obj, inputfile.encode('utf-8'), outputfile.encode('utf-8'), tokenize)
        else:
            raise OSError('File {} does not exist.'.format(inputfile))

    def cleanup(self):
        self._load_tagger = None
        self._tag_sentence = None
        self._tag_file = None
        self._zpar_session_obj = None

