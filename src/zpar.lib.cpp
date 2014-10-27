/****************************************************************
 *                                                              *
 * zpar.lib.cpp - a library that can be used by python          *
 *                                                              *
 * Author: Nitin Madnani                                        *
 * Educational Testing Service, Princeton, NJ                   *
 *                                                              *
 ****************************************************************/

#define SIMPLE_HASH

#include "definitions.h"
#include "options.h"
#include "tagger.h"
#include "conparser.h"
#include "depparser.h"
#include "reader.h"
#include "writer.h"
#include "stdlib.h"
#include <cstring>
#include <iterator>
#include <sstream>

using namespace english;

#define MAX_SENTENCE_SIZE 512


// define a container structure with a container and a destructor
struct zparModel_t
{
    void *tagger;
    void *conparser;
    void *depparser;
    char *output_buffer;

    zparModel_t() {
        tagger = NULL;
        conparser = NULL;
        depparser = NULL;
        output_buffer = NULL;
    };

    ~zparModel_t() {
        if (tagger)
            delete (CTagger *)tagger;
        if (conparser)
            delete (CConParser *)conparser;
        if (depparser)
            delete (CDepParser *)depparser;
        if (output_buffer) {
            delete output_buffer;
        }
    };
};

// instantiate the container
zparModel_t *zpm = new zparModel_t();

// a utility function to output tagged data in the usual
// "WORD/TAG" format as expected
std::string format_tagged_vector(CTwoStringVector *tagged_sent)
{

    CTwoStringVector::const_iterator it;
    CStringVector formatted_tagged_sent[1];
    for (it = tagged_sent->begin(); it != tagged_sent->end(); ++it)
    {
        std::stringstream tmpss;
        tmpss << it->first << "/" << it->second;
        std::string tmpstr(tmpss.str());
        formatted_tagged_sent->push_back(tmpstr);
    }

    int i;
    std::stringstream oss;
    for (i = 0; i < formatted_tagged_sent->size(); ++i)
    {
        oss << formatted_tagged_sent->at(i);
        if (i != formatted_tagged_sent->size() - 1)
        {
            oss << " ";
        }
    }

    std::string outstr(oss.str());
    return outstr;

}

// A utility function to format the dependncy output
// in CoNLL format
std::string format_dependency_tree(CDependencyParse *parsed_sent)
{

    int i;
    std::stringstream oss;
    std::copy(parsed_sent->begin(), parsed_sent->end(), std::ostream_iterator<CLabeledDependencyTreeNode>(oss, "\n"));

    std::string outstr(oss.str());
    return outstr;

}

// The function to load the tagger model
extern "C" int load_tagger(const char *sFeaturePath) {

    CTagger *tagger;
    std::string sTaggerFeatureFile = std::string(sFeaturePath) + "/tagger";
    std::cerr << "Loading tagger from " << sTaggerFeatureFile << std::endl;
    if (!FileExists(sTaggerFeatureFile)) {
        return 1;
    }
    tagger = new CTagger(sTaggerFeatureFile, false);
    zpm->tagger = (void *)tagger;
    return 0;

}

// The function to load the constituency parser model
extern "C" int load_parser(const char *sFeaturePath) {

    // If the tagger is not already loaded, then we need to load
    // it since the parser requires the tagger
    if (!zpm->tagger) {
        if (load_tagger(sFeaturePath)) {
            return 1;
        }
    }

    CConParser *conparser;
    std::string sConParserFeatureFile = std::string(sFeaturePath) + "/conparser";
    std::cerr << "Loading constituency parser from " << sConParserFeatureFile << std::endl;
    if (!FileExists(sConParserFeatureFile)) {
        return 1;
    }
    conparser = new CConParser(sConParserFeatureFile, false);
    zpm->conparser = (void *)conparser;
    return 0;
}

// The function to load the dependency parser model
extern "C" int load_depparser(const char *sFeaturePath) {

    // If the tagger is not already loaded, then we need to load
    // it since the parser requires the tagger
    if (!zpm->tagger) {
        if (load_tagger(sFeaturePath)) {
            return 1;
        }
    }

    CDepParser *depparser;
    std::string sDepParserFeatureFile = std::string(sFeaturePath) + "/depparser";
    std::cerr << "Loading dependency parser from " << sDepParserFeatureFile << std::endl;
    if (!FileExists(sDepParserFeatureFile)) {
        return 1;
    }
    depparser = new CDepParser(sDepParserFeatureFile, false);
    zpm->depparser = (void *)depparser;
    return 0;
}

// The function to load all three models
extern "C" int load_models(const char *sFeaturePath) {
    if (load_tagger(sFeaturePath)) {
        return 1;
    }
    if (load_parser(sFeaturePath)) {
        return 1;
    }
    if (load_depparser(sFeaturePath)) {
        return 1;
    }
    return 0;
}

// Function to tag a sentence
extern "C" char* tag_sentence(const char *input_sentence, bool tokenize)
{

    // create a temporary string stream from the input char *
    CSentenceReader input_reader(std::string(input_sentence), false);

    // tokenize the sentence
    CStringVector input_sent[1];
    if (tokenize) {
        input_reader.readSegmentedSentenceAndTokenize(input_sent);
    }
    else {
        input_reader.readSegmentedSentence(input_sent);
    }

    // initialize the variable that will hold the tagged sentence
    CTwoStringVector tagged_sent[1];

    // get the tagger that was stored earlier
    CTagger *tagger = (CTagger *)zpm->tagger;

    // tag the sentence
    tagger->tag(input_sent, tagged_sent);

    // format the tagged sentence properly and return
    std::string tagvec = format_tagged_vector(tagged_sent);
    int tagveclen = tagvec.length();

    if (zpm->output_buffer != NULL) {
        delete zpm->output_buffer;
        zpm->output_buffer = NULL;
    }
    zpm->output_buffer = new char[tagveclen + 1];
    strcpy(zpm->output_buffer, tagvec.c_str());
    return zpm->output_buffer;
}

// Function to constituency parse a sentence
extern "C" char* parse_sentence(const char *input_sentence, bool tokenize)
{

    // create a temporary string stream from the input char *
    CSentenceReader input_reader(std::string(input_sentence), false);

    // tokenize the sentence
    CStringVector tokenized_sent[1];
    if (tokenize) {
        input_reader.readSegmentedSentenceAndTokenize(tokenized_sent);
    }
    else {
        input_reader.readSegmentedSentence(tokenized_sent);
    }

    if (zpm->output_buffer != NULL) {
        delete zpm->output_buffer;
        zpm->output_buffer = NULL;
    }

    if(tokenized_sent->size() >= MAX_SENTENCE_SIZE){
        // The ZPar code asserts that length < MAX_SENTENCE_SIZE...
        std::cerr << "Sentence too long. Returning empty string. Sentence: " << input_sentence << std::endl;
        zpm->output_buffer = new char[1];
        strcpy(zpm->output_buffer, "");
    } else {
        // initialize the variable that will hold the tagged sentence
        CTwoStringVector tagged_sent[1];
        english::CCFGTree parsed_sent[1];

        // get the tagger that was stored earlier
        CTagger *tagger = (CTagger *)zpm->tagger;
        CConParser *conparser = (CConParser *)zpm->conparser;

        // tag the sentence
        tagger->tag(tokenized_sent, tagged_sent);
        conparser->parse(*tagged_sent, parsed_sent);

        // now put the tagged_sent into a string stream
        std::string parse = parsed_sent->str_unbinarized();
        int parselen = parse.length();
        zpm->output_buffer = new char[parselen + 1];
        strcpy(zpm->output_buffer, parse.c_str());
    }

    return zpm->output_buffer;
}

// Function to dependency parse a sentence
extern "C" char* dep_parse_sentence(const char *input_sentence, bool tokenize)
{

    // create a temporary string stream from the input char *
    CSentenceReader input_reader(std::string(input_sentence), false);

    // tokenize the sentence
    CStringVector tokenized_sent[1];
    if (tokenize) {
        input_reader.readSegmentedSentenceAndTokenize(tokenized_sent);
    }
    else {
        input_reader.readSegmentedSentence(tokenized_sent);
    }

    // initialize the variable that will hold the tagged sentence
    CTwoStringVector tagged_sent[1];
    CDependencyParse parsed_sent[1];

    if (zpm->output_buffer != NULL) {
        delete zpm->output_buffer;
        zpm->output_buffer = NULL;
    }

    if(tokenized_sent->size() >= MAX_SENTENCE_SIZE){
        // The ZPar code asserts that length < MAX_SENTENCE_SIZE...
        std::cerr << "Sentence too long. Returning empty string. Sentence: " << input_sentence << std::endl;
        zpm->output_buffer = new char[1];
        strcpy(zpm->output_buffer, "");
    } else {
        // get the tagger that was stored earlier
        CTagger *tagger = (CTagger *)zpm->tagger;
        CDepParser *depparser = (CDepParser *)zpm->depparser;

        // tag the sentence
        tagger->tag(tokenized_sent, tagged_sent);
        depparser->parse(*tagged_sent, parsed_sent);

        // now output the formatted dependency tree
        std::string deptree = format_dependency_tree(parsed_sent);
        int deptreelen = deptree.length();
        zpm->output_buffer = new char[deptreelen + 1];
        strcpy(zpm->output_buffer, deptree.c_str());
    }

    return zpm->output_buffer;
}

// Function to tag all sentence in the given input file
// and write tagged sentences to the given output file
extern "C" void tag_file(const char *sInputFile, const char *sOutputFile, bool tokenize)
{

    std::cerr << "Processing file " <<  sInputFile << std::endl;

    // initialize the input reader
    CSentenceReader input_reader(sInputFile);

    // open the output file
    FILE *outfp = NULL;
    outfp = fopen(sOutputFile, "w");

    // initialize the temporary sentence variables
    CStringVector tokenized_sent[1];
    CTwoStringVector tagged_sent[1];

    // get the tagger and the parser that were stored earlier
    CTagger *tagger = (CTagger *)zpm->tagger;

    // read in and tokenize the given input file if asked
    bool readSomething;
    if (tokenize) {
        readSomething = input_reader.readSegmentedSentenceAndTokenize(tokenized_sent);
    }
    else {
        readSomething = input_reader.readSegmentedSentence(tokenized_sent);
    }
    while ( readSomething )
    {
        if ( tokenized_sent->back() == "\n" )
        {
            tokenized_sent->pop_back();
        }

        // tag the sentence
        tagger->tag(tokenized_sent, tagged_sent);

        // write the formatted sentence to the output file
        std::string tagvec = format_tagged_vector(tagged_sent);
        fprintf(outfp, "%s\n", tagvec.c_str());

        if (tokenize) {
            readSomething = input_reader.readSegmentedSentenceAndTokenize(tokenized_sent);
        }
        else {
            readSomething = input_reader.readSegmentedSentence(tokenized_sent);
        }
    }

    // close the output file
    std::cerr << "Wrote output to " << sOutputFile << std::endl;
    fclose(outfp);
}

// Function to constituency parse all sentence in the given input file
// and write parsed sentences to the given output file
extern "C" void parse_file(const char *sInputFile, const char *sOutputFile, bool tokenize)
{

    std::cerr << "Processing file " <<  sInputFile << std::endl;

    // initialize the input reader
    CSentenceReader input_reader(sInputFile);

    // open the output file
    FILE *outfp = NULL;
    outfp = fopen(sOutputFile, "w");

    // initialize the temporary sentence variables
    CStringVector tokenized_sent[1];
    CTwoStringVector tagged_sent[1];
    english::CCFGTree parsed_sent[1];

    // get the tagger and the parser that were stored earlier
    CTagger *tagger = (CTagger *)zpm->tagger;
    CConParser *conparser = (CConParser *)zpm->conparser;

    // read in and tokenize the given input file if asked
    bool readSomething;
    if (tokenize) {
        readSomething = input_reader.readSegmentedSentenceAndTokenize(tokenized_sent);
    }
    else {
        readSomething = input_reader.readSegmentedSentence(tokenized_sent);
    }

    while ( readSomething )
    {
        if ( tokenized_sent->back() == "\n" )
        {
            tokenized_sent->pop_back();
        }

        std::string parse = "";
        if(tokenized_sent->size() < MAX_SENTENCE_SIZE){
            tagger->tag(tokenized_sent, tagged_sent);
            conparser->parse(*tagged_sent, parsed_sent);
            parse = parsed_sent->str_unbinarized();
        } else {
            std::cerr << "Sentence too long. Writing empty string. Sentence: " << tokenized_sent << std::endl;
        }

        fprintf(outfp, "%s\n", parse.c_str());

        if (tokenize) {
            readSomething = input_reader.readSegmentedSentenceAndTokenize(tokenized_sent);
        }
        else {
            readSomething = input_reader.readSegmentedSentence(tokenized_sent);
        }
    }

    // close the output file
    std::cerr << "Wrote output to " << sOutputFile << std::endl;
    fclose(outfp);
}

// Function to dependency parse all sentence in the given input file
// and write parsed sentences to the given output file
extern "C" void dep_parse_file(const char *sInputFile, const char *sOutputFile, bool tokenize)
{

    std::cerr << "Processing file " <<  sInputFile << std::endl;

    // initialize the input reader
    CSentenceReader input_reader(sInputFile);

    // open the output file
    FILE *outfp = NULL;
    outfp = fopen(sOutputFile, "w");

    // initialize the temporary sentence variables
    CStringVector tokenized_sent[1];
    CTwoStringVector tagged_sent[1];
    CDependencyParse parsed_sent[1];

    // get the tagger and the parser that were stored earlier
    CTagger *tagger = (CTagger *)zpm->tagger;
    CDepParser *depparser = (CDepParser *)zpm->depparser;

    // read in and tokenize the given input file if asked
    bool readSomething;
    if (tokenize) {
        readSomething = input_reader.readSegmentedSentenceAndTokenize(tokenized_sent);
    }
    else {
        readSomething = input_reader.readSegmentedSentence(tokenized_sent);
    }

    while ( readSomething )
    {
        if ( tokenized_sent->back() == "\n" )
        {
            tokenized_sent->pop_back();
        }

        std::string deptree = "";
        if(tokenized_sent->size() < MAX_SENTENCE_SIZE){
            tagger->tag(tokenized_sent, tagged_sent);
            depparser->parse(*tagged_sent, parsed_sent);
            deptree = format_dependency_tree(parsed_sent);
        } else {
            std::cerr << "Sentence too long. Writing empty string. Input:" << tokenized_sent << std::endl;
        }

        fprintf(outfp, "%s\n", deptree.c_str());

        if (tokenize) {
            readSomething = input_reader.readSegmentedSentenceAndTokenize(tokenized_sent);
        }
        else {
            readSomething = input_reader.readSegmentedSentence(tokenized_sent);
        }
    }

    // close the output file
    std::cerr << "Wrote output to " << sOutputFile << std::endl;
    fclose(outfp);
}

// Function to unload all the models
extern "C" void unload_models()
{

    // just delete the container itself and its destructor
    // will take care of everything else
    delete zpm;
}

// // A main function for testing
// extern "C" int main(int argc, char *argv[])
// {
//     load_models("/scratch/nmadnani/zpar-new/english-models");
//     std::cout << std::string(tag_sentence("I said `` I am going to the market . \"", false)) << std::endl;
//     std::cout << std::string(parse_sentence("I said `` I am going to the market . \"", false)) << std::endl;
//     std::cout << std::string(dep_parse_sentence("I said `` I am going to the market . \"", false)) << std::endl;
//     std::cout << std::string(tag_sentence("I said \"I am going to the market .\"", true)) << std::endl;
//     std::cout << std::string(parse_sentence("I said \"I am going to the market .\"", true)) << std::endl;
//     std::cout << std::string(dep_parse_sentence("I said \"I am going to the market .\"", true)) << std::endl;
//     tag_file("/scratch/nmadnani/zpar-new/test.txt", "/scratch/nmadnani/zpar-new/test.tag", false);
//     parse_file("/scratch/nmadnani/zpar-new/test.txt", "/scratch/nmadnani/zpar-new/test.parse", false);
//     dep_parse_file("/scratch/nmadnani/zpar-new/test.txt", "/scratch/nmadnani/zpar-new/test.dep", false);
//     tag_file("/scratch/nmadnani/zpar-new/test2.txt", "/scratch/nmadnani/zpar-new/test2.tag", true);
//     parse_file("/scratch/nmadnani/zpar-new/test2.txt", "/scratch/nmadnani/zpar-new/test2.parse", true);
//     dep_parse_file("/scratch/nmadnani/zpar-new/test2.txt", "/scratch/nmadnani/zpar-new/test2.dep", true);
//     unload_models();

//     return 0;
// }
