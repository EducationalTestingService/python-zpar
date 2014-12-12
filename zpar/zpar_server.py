#!/usr/bin/env python

import argparse
import logging
import os
import six
import sys

from zpar import ZPar

if six.PY2:
    from SimpleXMLRPCServer import SimpleXMLRPCServer
else:
    from xmlrpc.server import SimpleXMLRPCServer

class ModelNotFoundError(Exception):

    def __init__(self, model_name, model_path):
        Exception.__init__(self)
        self.model_name = model_name
        self.model_path = model_path

    def __str__(self):
        if self.model_name != 'all':
            return "No {} model could be found at {}".format(self.model_name,
                                                             self.model_path)
        else:
            return "No models could be found at {}".format(self.model_path)


_baseclass = SimpleXMLRPCServer
class StoppableServer(_baseclass):

    allow_reuse_address = True

    def __init__(self, addr, zpar_model_path, model_list, *args, **kwds):

        # store the hostname and port number
        self.myhost, self.myport = addr

        # store the link to the loaded zpar object
        self.z = ZPar(zpar_model_path)

        # initialize the parent class
        _baseclass.__init__(self, addr, *args, **kwds)

        # Call the individual loading functions
        # and only register the appropriate methods
        if 'tagger' in model_list:
            tagger = self.z.get_tagger()
            self.register_function(tagger.tag_sentence)
            self.register_function(tagger.tag_file)
        if 'parser' in model_list:
            parser = self.z.get_parser()
            self.register_function(parser.parse_sentence)
            self.register_function(parser.parse_file)
            self.register_function(parser.parse_tagged_sentence)
            self.register_function(parser.parse_tagged_file)
        if 'depparser' in model_list:
            parser = self.z.get_depparser()
            self.register_function(parser.dep_parse_sentence)
            self.register_function(parser.dep_parse_file)
            self.register_function(parser.dep_parse_tagged_sentence)
            self.register_function(parser.dep_parse_tagged_file)

        # register the function to remotely stop the server
        self.register_function(self.stop_server)

        self.quit = False

    def serve_forever(self):
        while not self.quit:
            try:
                self.handle_request()
            except KeyboardInterrupt:
                print("\nKeyboard interrupt received, exiting.")
                break
        self.z.close()
        self.server_close()

    def stop_server(self):
        self.quit = True
        return 0, "Server terminated on host %r, port %r" % (self.myhost, self.myport)


def main():
    # set up an argument parser
    parser = argparse.ArgumentParser(prog='zpar_server.py', \
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--modeldir', dest='modeldir',
                        help="Path to directory containing zpar English models",
                        required=True)

    parser.add_argument('--models', dest='models', nargs='+',
                        help="Load only these models",
                        required=True)

    parser.add_argument('--host', dest='hostname',
                        help="Hostname or IP address",
                        default="localhost",
                        required=False)

    parser.add_argument('--port', dest='port', type=int,
                        help="Port number",
                        default=8859,
                        required=False)

    parser.add_argument('--log', dest='log', action="store_true",
                        default=False,
                        help="Log server requests")


    # parse given command line arguments
    args = parser.parse_args()

    # check to make sure that the specified models
    # are those we know about
    if set(args.models).difference(['tagger', 'parser', 'depparser']):
        sys.stderr.write('Error: invalid model(s) specified. Choices are: "tagger", "parser", and "depparser".\n')
        sys.exit(1)

    # set up the logging
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

    # Create a server that is built on top of this ZPAR data structure
    logging.info('Initializing server ...')
    server = StoppableServer((args.hostname, args.port),
                             args.modeldir, args.models,
                             logRequests=args.log,
                             allow_none=True)

    # Register introspection functions with the server
    logging.info('Registering introspection ...')
    server.register_introspection_functions()

    # Start the server
    logging.info('Starting server on port {}...'.format(args.port))
    server.serve_forever()


if __name__ == '__main__':
    main()
