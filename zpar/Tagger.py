# License: MIT
'''
:author: Nitin Madnani (nmadnani@ets.org)
:organization: ETS
'''
import ctypes as c
import os

class Tagger(object):
    """The ZPar English POS Tagger"""

    def __init__(self, modelpath, libptr, zpar_session_obj):
        super(Tagger, self).__init__()

        # save the zpar session object
        self._zpar_session_obj = zpar_session_obj

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
            zpar_compatible_sentence = sentence.strip() + "\n "
            zpar_compatible_sentence = zpar_compatible_sentence.encode('utf-8')
            tagged_sent = self._tag_sentence(self._zpar_session_obj, zpar_compatible_sentence, tokenize)
            ans = tagged_sent.decode('utf-8')

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

