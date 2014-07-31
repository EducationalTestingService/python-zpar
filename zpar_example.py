#!/usr/bin/env python3

import argparse
import ctypes as c
import logging
import os
import sys

from six import print_

if __name__ == '__main__':
    # set up an argument parser
    parser = argparse.ArgumentParser(prog='zpar_example.py')
    parser.add_argument('--zpar', dest='zpar',
                        help="Path to the zpar library file zpar.so",
                        required=False, default=os.getcwd())

    parser.add_argument('--modeldir', dest='modeldir',
                        help="Path to directory containing zpar English models",
                        required=True)

    # parse given command line arguments
    args = parser.parse_args()

    # set up the logging
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

    # link to the zpar library
    zpar_library_path = os.path.join(args.zpar, 'zpar.so')

    # Create a wrapper data structure that the functionality as methods
    zpar = c.cdll.LoadLibrary(zpar_library_path)

    # define the argument and return types for all
    # the functions we want to expose to the client
    load_models = zpar.load_models
    load_models.restype = c.c_int
    load_models.argtypes = [c.c_char_p]

    load_tagger = zpar.load_tagger
    load_tagger.restype = c.c_int
    load_tagger.argtypes = [c.c_char_p]

    load_parser = zpar.load_parser
    load_parser.restype = c.c_int
    load_parser.argtypes = [c.c_char_p]

    load_depparser = zpar.load_depparser
    load_depparser.restype = c.c_int
    load_depparser.argtypes = [c.c_char_p]

    tag_sentence = zpar.tag_sentence
    tag_sentence.restype = c.c_char_p
    tag_sentence.argtypes = [c.c_char_p]

    parse_sentence = zpar.parse_sentence
    parse_sentence.restype = c.c_char_p
    parse_sentence.argtypes = [c.c_char_p]

    dep_parse_sentence = zpar.dep_parse_sentence
    dep_parse_sentence.restype = c.c_char_p
    dep_parse_sentence.argtypes = [c.c_char_p]

    tag_file = zpar.tag_file
    tag_file.restype = None
    tag_file.argtypes = [c.c_char_p, c.c_char_p]

    parse_file = zpar.parse_file
    parse_file.restype = None
    parse_file.argtypes = [c.c_char_p, c.c_char_p]

    dep_parse_file = zpar.dep_parse_file
    dep_parse_file.restype = None
    dep_parse_file.argtypes = [c.c_char_p, c.c_char_p]

    unload_models = zpar.unload_models
    unload_models.restype = None

    # Load just the tagger and the dependency parser.
    # To load the constituency parser, use load_parser().
    # If you want to load all three models, use
    # load_models() instead.
    if load_tagger(args.modeldir.encode('utf-8')):
        sys.stderr.write('Cannot find tagger model at {}\n'.format(args.modeldir))
        zpar.unload_models()
        sys.exit(1)
    if load_parser(args.modeldir.encode('utf-8')):
        sys.stderr.write('Cannot find parser model at {}\n'.format(args.modeldir))
        zpar.unload_models()
        sys.exit(1)
    if load_depparser(args.modeldir.encode('utf-8')):
        sys.stderr.write('Cannot find depparser model at {}\n'.format(args.modeldir))
        zpar.unload_models()
        sys.exit(1)

    # Tag a sentence. Note that the sentence does not need to be tokenized
    # but needs to have a newline and a space after it because of the
    # way that zpar word tokenizer is written. We also need
    # to convert the output back from bytes to strings.
    tagged_sent = tag_sentence("I am going to the market.\n ".encode("utf-8"))
    print_(tagged_sent.decode('utf-8'))

    parsed_sent = parse_sentence("I am going to the market.\n ".encode("utf-8"))
    print_(parsed_sent.decode('utf-8'))

    parsed_sent = parse_sentence("Would you like to come with me?\n ".encode("utf-8"))
    print_(parsed_sent.decode('utf-8'))

    # Compute the dependency parse of the sentence
    dep_parsed_sent = dep_parse_sentence("I am going to the market.\n ".encode("utf-8"))
    print_(dep_parsed_sent.decode('utf-8'))

    # compute POS tags for all sentences in a file
    # note that the file contains a single sentence
    # per line. The sentences need not be word tokenized
    tag_file(b"test.txt", b"test.tag")

    # compute dependency parses for all sentences in a file
    dep_parse_file(b"test.txt", b"test.dep")

    # unload all the models from memory once you are done
    unload_models()
