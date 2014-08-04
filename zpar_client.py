#!/usr/bin/env python3

import argparse
import logging
import six
import socket
import sys

if __name__ == '__main__':

    # set up an argument parser
    parser = argparse.ArgumentParser(prog='zpar_client.py')

   # set up the logging
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

    parser.add_argument('--host', dest='hostname',
                        help="Hostname or IP address",
                        default="localhost",
                        required=False)

    parser.add_argument('--port', dest='port', type=int,
                        help="Port number",
                        default=8859,
                        required=False)

    # parse given command line arguments
    args = parser.parse_args()

    # set up the logging
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

    # instantiate the client appropriately and connect
    logging.info('Attempting connection to http://{}:{}'.format(args.hostname,
                                                                args.port))
    if six.PY2:
        import xmlrpclib
        proxy = xmlrpclib.ServerProxy('http://{}:{}'.format(args.hostname,
                                                            args.port),
                                      allow_none=True)
        fault = xmlrpclib.Fault
    else:
        import xmlrpc.client
        proxy = xmlrpc.client.ServerProxy('http://{}:{}'.format(args.hostname,
                                                                args.port),
                                          use_builtin_types=True,
                                          allow_none=True)
        fault = xmlrpc.client.Fault

    # Make the remote procedure calls on the server
    try:

        test_sentence = 'I am going to the market.'
        test_file = 'test.txt'
        tag_outfile = 'test.tag'
        dep_outfile = 'test.dep'

        logging.info('Tagging "{}"'.format(test_sentence))
        tagged_sent = proxy.tag_sentence(test_sentence)
        logging.info("Output: {}".format(tagged_sent))

        logging.info('Dep Parsing "{}"'.format(test_sentence))
        dep_parsed_sent = proxy.dep_parse_sentence(test_sentence)
        logging.info("Output: {}".format(dep_parsed_sent))

        logging.info('Tagging file {} into {}'.format(test_file, tag_outfile))
        proxy.tag_file(test_file, tag_outfile)

        logging.info('Dep Parsing file {} into {}'.format(test_file, dep_outfile))
        proxy.dep_parse_file(test_file, dep_outfile)

    except socket.error as err:
        sys.stderr.write("{}\n".format(err))
        sys.exit(1)
    except fault as flt:
        sys.stderr.write("Fault {}: {}\n".format(flt.faultCode,
                                                 flt.faultString))
        sys.exit(1)

    # Stop the server
    # NOTE: You will probably do this in the last client (if you know
    # which one that is) or in a clean-up script when you are absolutely sure
    # that all clients are finished.
    proxy.stop_server()

