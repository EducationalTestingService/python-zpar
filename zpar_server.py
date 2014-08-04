#!/usr/bin/env python3
import argparse
import ctypes as c
import logging
import os
import six
import sys

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

    def __init__(self, addr, zpar_ref, zpar_model_path, model_list, *args, **kwds):

        # store the hostname and port number
        self.myhost, self.myport = addr

        # store the link to the loaded zpar object
        self.zpar_ref = zpar_ref

        # define the argument and return types for all
        # the functions we want to expose to the client
        self.zpar_ref.load_models.restype = c.c_int
        self.zpar_ref.load_models.argtypes = [c.c_char_p]

        self.zpar_ref.load_tagger.restype = c.c_int
        self.zpar_ref.load_tagger.argtypes = [c.c_char_p]

        self.zpar_ref.load_parser.restype = c.c_int
        self.zpar_ref.load_parser.argtypes = [c.c_char_p]

        self.zpar_ref.load_depparser.restype = c.c_int
        self.zpar_ref.load_depparser.argtypes = [c.c_char_p]

        self.zpar_ref.tag_sentence.restype = c.c_char_p
        self.zpar_ref.tag_sentence.argtypes = [c.c_char_p]

        self.zpar_ref.parse_sentence.restype = c.c_char_p
        self.zpar_ref.parse_sentence.argtypes = [c.c_char_p]

        self.zpar_ref.dep_parse_sentence.restype = c.c_char_p
        self.zpar_ref.dep_parse_sentence.argtypes = [c.c_char_p]

        self.zpar_ref.tag_file.restype = None
        self.zpar_ref.tag_file.argtypes = [c.c_char_p, c.c_char_p]

        self.zpar_ref.parse_file.restype = None
        self.zpar_ref.parse_file.argtypes = [c.c_char_p, c.c_char_p]

        self.zpar_ref.dep_parse_file.restype = None
        self.zpar_ref.dep_parse_file.argtypes = [c.c_char_p, c.c_char_p]

        self.zpar_ref.unload_models.restype = None

        # initialize the parent class
        _baseclass.__init__(self, addr, *args, **kwds)

        # load the models we were asked to. If the list of
        # given models is empty or if it contains all the models
        # then call the function that loads all the models and
        # registers all the functions
        if not model_list or sorted(model_list) == ['depparser',
                                                    'parser',
                                                    'tagger']:
            if self.zpar_ref.load_models(zpar_model_path):
                raise ModelNotFoundError("all", zpar_model_path.decode('utf-8'))
            else:
                self.register_function(self.tag_sentence)
                self.register_function(self.parse_sentence)
                self.register_function(self.dep_parse_sentence)
                self.register_function(self.tag_file)
                self.register_function(self.parse_file)
                self.register_function(self.dep_parse_file)

        # otherwise call the individual loading functions
        # and only register the appropriate methods
        else:
            if 'tagger' in model_list:
                if self.zpar_ref.load_tagger(zpar_model_path):
                    raise ModelNotFoundError("tagger", zpar_model_path.decode('utf-8'))
                else:
                    self.register_function(self.tag_sentence)
                    self.register_function(self.tag_file)
            if 'parser' in model_list:
                if self.zpar_ref.load_parser(zpar_model_path):
                    raise ModelNotFoundError("parser", zpar_model_path.decode('utf-8'))
                else:
                    self.register_function(self.parse_sentence)
                    self.register_function(self.parse_file)
            if 'depparser' in model_list:
                if self.zpar_ref.load_depparser(zpar_model_path):
                    raise ModelNotFoundError("depparser", zpar_model_path.decode('utf-8'))
                else:
                    self.register_function(self.dep_parse_sentence)
                    self.register_function(self.dep_parse_file)

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
        self.zpar_ref.unload_models()
        self.server_close()

    def tag_sentence(self, sentence):
        # We need to add a newline to the sentence
        # given how zpar's tokenization works
        out = self.zpar_ref.tag_sentence(sentence.encode('utf-8') + b'\n ')
        return out.decode('utf-8')

    def parse_sentence(self, sentence):
        # We need to add a newline to the sentence
        # given how zpar's tokenization works
        out = self.zpar_ref.parse_sentence(sentence.encode('utf-8') + b'\n ')
        return out.decode('utf-8')

    def dep_parse_sentence(self, sentence):
        # We need to add a newline to the sentence
        # given how zpar's tokenization works
        out = self.zpar_ref.dep_parse_sentence(sentence.encode('utf-8') + b'\n ')
        return out.decode('utf-8')

    def tag_file(self, input_filename, output_filename):
        self.zpar_ref.tag_file(input_filename.encode('utf-8'),
                               output_filename.encode('utf-8'))

    def parse_file(self, input_filename, output_filename):
        self.zpar_ref.parse_file(input_filename.encode('utf-8'),
                                 output_filename.encode('utf-8'))

    def dep_parse_file(self, input_filename, output_filename):
        self.zpar_ref.dep_parse_file(input_filename.encode('utf-8'),
                                     output_filename.encode('utf-8'))

    def stop_server(self):
        self.quit = True
        return 0, "Server terminated on host %r, port %r" % (self.myhost, self.myport)


if __name__ == '__main__':

    # set up an argument parser
    parser = argparse.ArgumentParser(prog='zpar_server.py')
    parser.add_argument('--zpar', dest='zpar',
                        help="Path to the zpar library file zpar.so",
                        required=False, default=os.getcwd())

    parser.add_argument('--modeldir', dest='modeldir',
                        help="Path to directory containing zpar English models",
                        required=True)

    parser.add_argument('--models', dest='models', nargs='+',
                        help="Load only these models",
                        default=None)

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
    if args.models:
        if set(args.models).difference(['tagger', 'parser', 'depparser']):
            sys.stderr.write('Error: invalid model(s) specified. Choices are: "tagger", "parser", and "depparser".\n')
            sys.exit(1)

    # set up the logging
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

    # link to the zpar library
    zpar_library_path = os.path.join(args.zpar, 'zpar.so')

    # Create a wrapper data structure that the functionality as methods
    zparobj = c.cdll.LoadLibrary(zpar_library_path)

    # Create a server that is built on top of this ZPAR data structure
    logging.info('Initializing server ...')
    try:
        server = StoppableServer((args.hostname, args.port),
                                 zparobj, args.modeldir.encode('utf-8'),
                                 args.models, logRequests=args.log,
                                 allow_none=True)
    except ModelNotFoundError as err:
        sys.stderr.write("{}\n".format(err))
        zparobj.unload_models()
        sys.exit(1)
    except:
        sys.stderr.write('Error: Could not create server\n')
        zparobj.unload_models()
        sys.exit(1)


    # Register introspection functions with the server
    logging.info('Registering introspection ...')
    server.register_introspection_functions()

    # Start the server
    logging.info('Starting server on port {}...'.format(args.port))
    server.serve_forever()
