#!/usr/bin/env python3

import argparse
import os
from six import print_

from zpar import ZPar

def main():
    # set up an argument parser
    parser = argparse.ArgumentParser(prog='zpar_example.py')
    parser.add_argument('--modeldir', dest='modeldir',
                        help="Path to directory containing zpar English models",
                        required=True)

    # parse given command line arguments
    args = parser.parse_args()

    # use the zpar wrapper as a context manager
    with ZPar(args.modeldir) as z:

        # get the parser and the dependency parser models
        tagger = z.get_tagger()
        depparser = z.get_depparser()

        # tag a sentence
        tagged_sent = tagger.tag_sentence("I am going to the market.")
        print_(tagged_sent)

        # tag an already tokenized sentence
        tagged_sent = tagger.tag_sentence("Do n't you want to come with me to the market ?", tokenize=False)
        print_(tagged_sent)

        # get the dependency parse of an already tagged sentence
        dep_parsed_sent = depparser.dep_parse_tagged_sentence("I/PRP am/VBP going/VBG to/TO the/DT market/NN ./.")
        print_(dep_parsed_sent)

        # get the dependency parse of an already tokenized sentence
        dep_parsed_sent = depparser.dep_parse_sentence("Do n't you want to come with me to the market ?", tokenize=False)
        print_(dep_parsed_sent)

        # get the dependency parse of an already tokenized sentence
        # and include lemma information (assuming you have NLTK as well
        # as its WordNet corpus installed)
        dep_parsed_sent = depparser.dep_parse_sentence("Do n't you want to come with me to the market ?", tokenize=False, with_lemmas=True)
        print_(dep_parsed_sent)

        # compute POS tags for all sentences in "test.txt"
        # and write the output to "test.tag". Note that the
        # file contains a single sentence per line.
        # The sentences need not be word tokenized
        test_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test.txt')
        tagger.tag_file(test_file, "test.tag")

        # compute dependency parses for all sentences in "test_tokenized.txt"
        tokenized_test_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_tokenized.txt')
        depparser.dep_parse_file(tokenized_test_file, "test.dep")

if __name__ == '__main__':
    main()
