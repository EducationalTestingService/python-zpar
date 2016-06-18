# License: MIT
'''
:author: Nitin Madnani (nmadnani@ets.org)
:organization: ETS
'''

import ctypes as c
import logging
import os

# do we have nltk installed and if so, do we have its
# wordnet corpus installed?
try:
    import nltk
    nltk.data.find('corpora/wordnet')
except (ImportError, LookupError):
    _HAS_LEMMATIZER = False
else:
    _HAS_LEMMATIZER = True
    from nltk.stem.wordnet import WordNetLemmatizer


class DepParser(object):
    """The ZPar English Dependency Parser"""

    def __init__(self, modelpath, libptr, zpar_session_obj):
        super(DepParser, self).__init__()

        # save the zpar session object
        self._zpar_session_obj = zpar_session_obj

        # set up a logger
        self.logger = logging.getLogger(__name__)

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

        # set up the wordnet lemmatizer if we have it
        if _HAS_LEMMATIZER:
            self.lemmatizer = WordNetLemmatizer()
        else:
            self.lemmatizer = None

    def annotate_parse_with_lemmas(self, parse):
        if not parse.strip():
            return parse
        else:
            new_parse_lines = []
            for line in parse.strip().split('\n'):
                fields = line.strip().split('\t')
                word, pos = fields[:2]
                if pos.startswith('J'):
                    param = 'a'
                elif pos.startswith('R'):
                    param = 'r'
                elif pos.startswith('V'):
                    param = 'v'
                else:
                    param = 'n'
                lemma = self.lemmatizer.lemmatize(word, param)
                new_parse_line = '\t'.join(fields + [lemma])
                new_parse_lines.append(new_parse_line)
            return '\n'.join(new_parse_lines) + '\n'

    def dep_parse_sentence(self,
                           sentence,
                           tokenize=True,
                           with_lemmas=False):
        if not sentence.strip():
            # return empty string if the input is empty
            ans = ""
        else:
            zpar_compatible_sentence = sentence.strip() + "\n "
            zpar_compatible_sentence = zpar_compatible_sentence.strip() + "\n "
            zpar_compatible_sentence = zpar_compatible_sentence.encode('utf-8')
            parsed_sent = self._dep_parse_sentence(self._zpar_session_obj,
                                                   zpar_compatible_sentence,
                                                   tokenize)
            ans = parsed_sent.decode('utf-8')

            # if we are asked to add lemma information, then we need
            # to add another field to each of the lines in the
            # parse returned from zpar
            if with_lemmas:
                if self.lemmatizer:
                    ans = self.annotate_parse_with_lemmas(ans)
                else:
                    self.logger.warning('No lemmatizer available. Please '
                                        'install NLTK and its Wordnet corpus.')
        return ans

    def dep_parse_file(self,
                       inputfile,
                       outputfile,
                       tokenize=True,
                       with_lemmas=False):


        if not os.path.exists(inputfile):
            raise OSError('File {} does not exist.'.format(inputfile))
        else:
            parsed = False

            # if we want lemmas, we have to individually parse
            # each sentence and then annotate its parse with lemmas
            if with_lemmas:
                if self.lemmatizer:
                    with open(inputfile, 'r') as inputf, open(outputfile, 'w') as outf:
                        for sentence in inputf:
                            outf.write(self.dep_parse_sentence(sentence,
                                                                tokenize=tokenize,
                                                                with_lemmas=True) + '\n')
                    parsed = True
                else:
                    self.logger.warning('No lemmatizer available. Please '
                                        'install NLTK and its Wordnet corpus.')

            # otherwise we can just parse the whole file in C++ space
            if not parsed:
                    self._dep_parse_file(self._zpar_session_obj,
                                         inputfile.encode('utf-8'),
                                         outputfile.encode('utf-8'),
                                         tokenize)

    def dep_parse_tagged_sentence(self,
                                  tagged_sentence,
                                  sep='/',
                                  with_lemmas=False):
        if not tagged_sentence.strip():
            # return empty string if the input is empty
            ans = ""
        else:
            zpar_compatible_sentence = tagged_sentence.strip().encode('utf-8')
            parsed_sent = self._dep_parse_tagged_sentence(self._zpar_session_obj,
                                                          zpar_compatible_sentence,
                                                          sep.encode('utf-8'))
            ans = parsed_sent.decode('utf-8')

        # if we are asked to add lemma information, then we need
        # to add another field to each of the lines in the
        # parse returned from zpar
        if with_lemmas:
            if self.lemmatizer:
                ans = self.annotate_parse_with_lemmas(ans)
            else:
                self.logger.warning('No lemmatizer available. Please '
                                    'install NLTK and its Wordnet corpus.')
        return ans

    def dep_parse_tagged_file(self, inputfile, outputfile, sep='/', with_lemmas=False):

        if not os.path.exists(inputfile):
            raise OSError('File {} does not exist.'.format(inputfile))
        else:

            parsed = False

            # if we want lemmas, we have to individually parse
            # each sentence and then annotate its parse with lemmas
            if with_lemmas:
                if self.lemmatizer:
                    with open(inputfile, 'r') as inputf, open(outputfile, 'w') as outf:
                        for sentence in inputf:
                            outf.write(self.dep_parse_tagged_sentence(sentence,
                                                                      sep=sep,
                                                                      with_lemmas=with_lemmas) + '\n')

                    parsed = True
                else:
                    self.logger.warning('No lemmatizer available. Please '
                                        'install NLTK and its Wordnet corpus.')

            # otherwise we can just parse the whole file in C++ space
            if not parsed:
                self._dep_parse_tagged_file(self._zpar_session_obj,
                                            inputfile.encode('utf-8'),
                                            outputfile.encode('utf-8'),
                                            sep.encode('utf-8'))

    def cleanup(self):
        self._load_depparser = None
        self._dep_parse_sentence = None
        self._dep_parse_file = None
        self._dep_parse_tagged_sentence = None
        self._dep_parse_tagged_file = None
        self._zpar_session_obj = None
