#!/usr/bin/python
import re
import nltk
import sys
import getopt
from tools import *
try:
   import cPickle as pickle
except:
   import pickle
import time
from math import log10

def prepare_queries(queries_file_name):
    # output list of queries
    queries = []

    raw_queries = open(queries_file_name, "r")

    # each query in the queries_file is traversed
    for line in raw_queries.read().splitlines():
        split = line.split(' ')
        queries.append(split)

    raw_queries.close()
    return queries

def cosine_score(query, postings, dictionnary):
    #TODO IMPLEMENT CACHING METHOD

    scores = dict()
    length = load_length() #TODO IMPLEMENT
    N = len(length) # Already defined

    w_t_q = w_t_q(query, dictionnary, N)
    for term in query:
        posting_list = fetch_posting_list(term, dictionnary, postings)
        for pair in posting_list: #TODO IMPLEMENT TRAVERSAL OF POSTINGS LIST
            document = pair[0]
            tf_t_d = pair[1]
            w_t_d = 1 + log10(tf_t_d)
            scores[document] = scores.get(document, 0) + w_t_d * w_t_q(term) # use td_weight

        for document in scores:
            scores[document] = scores[document] / length[document]

    return top_k(scores) #TODO IMPLEMENT
d
#TF*IDF of each term, return a dictionnary
def w_t_q(query, dictionnary, N): #TODO HOW TO GET N ?
    tf = dict()
    for term in query:
        tf[term] = tf.get(term, 0) + 1

    w_t_q = dict()
    for term in tf:
        df = dictionnary[term][0]
        w_t_q[term] = (1 + log10(tf[term])) * log10(N / df)#TODO take care of float division and non-zero log arg

    return w_t_q



def fetch_posting_list(term, dictionnary, postings):
    offset = dictionnary[term][1]
    postings.seek(offset)
    line = postings.readline()
    line = line[:-1]
    posting_list = Postings(line)
    return posting_list

def load_length():
    length = dict()
    return length

def search(dictionary_file_name, postings_file_name, queries_file_name, file_of_output_name):

    # the dictionary is loaded from file using the pickle library
    serialized_dictionary = open(dictionary_file_name, "r")
    dictionary = pickle.load(serialized_dictionary)
    serialized_dictionary.close()

    # the output file containing the results of the queries, each result on a different line
    output = open(file_of_output_name, "w")

    # queries are prepared using the above defined helper function
    postings = open(postings_file_name, "r")
    queries = prepare_queries(queries_file_name)

    # every query is evaluated and the output written to the output file
    for query in queries:
        output.write(cosine_score(query, postings, dictionary))

    postings.close()
    output.close()

"""
""""""
    Reads the file "queries_file_name" which contains one query at each line and outputs a list containing
    the query in post-fix notation, where the terms have been stemmed and case-folded and then replaced
    by their corresponding posting-list as found from the inverted index.
""""""
def prepare_queries(queries_file_name, postings_file_name, dictionary):
    # output list of queries
    queries = []

    raw_queries = open(queries_file_name, "r")
    postings = open(postings_file_name, "r")

    # the postings cache avoids retrieving the same postings list from disk (costly) multiple times
    postings_cache = {}

    # each query in the queries_file is traversed
    for line in raw_queries.read().splitlines():
        prepared_query = []
        split = line.split(' ')
        # each word in the query is traversed, a word can either be a term (e.g 'bill') or an operator (e.g 'AND')
        for word in split:
            # if the word is an operator, we leave it as it is.
            if is_operator(word):
                operator = word
                prepared_query.append(operator)

            # if the word is a term, we need to reduce it (stemming, case-folding, etc)
            # and replace it by the corresponding posting list
            else:
                term = word
                # we need to separate terms and parenthesis (=add space).
                # for example 'windows and (xp or vista)' should be replaced by 'windows and ( xp or vista )'
                # this is needed to ease the work of the shunting-yard algorithm
                if(term[0] == '('):
                    term = term[1:len(term)]
                    prepared_query.append('(')
                right_parenthesis = False
                if(term[len(term)-1] == ')'):
                    term = term[0:len(term)-1]
                    right_parenthesis = True

                # the term is reduced in the same way as in the indexing part
                term = stem_and_casefold(term)

                # the position in the file of the posting-list corresponding to a term is given by the
                # offset (= pointer) stored in the dictionary (= inverted index)
                if term in dictionary:
                    offset = dictionary[term][1]

                    # this posting list has not already been read from disk thus we cache it for efficiency
                    if offset is not None and not offset in postings_cache:
                        postings.seek(offset)
                        line = postings.readline()
                        line = line[:-1]
                        postings_cache[offset] = posting_list(line)

                    posting = postings_cache[offset]

                # if the term is not in the training corpus the corresponding posting-list is empty
                else:
                    posting = posting_list([])

                # we append the term to the query
                prepared_query.append(posting)

                # if there is a right parenthesis we separate it from the term (= add space)
                if right_parenthesis:
                    prepared_query.append(")")

        # we perform the shunting-yard algorithm on the query to transform it from an
        # in-fix expression to a post-fix expression
        post_fixed_prepared_query = shunting_yard(prepared_query)

        # the query is appended to the list of queries
        queries.append(post_fixed_prepared_query)

    raw_queries.close()
    postings.close()

    return queries
"""




"""
""""""
    This function performs the queries given in the queries_file_name file using the given
    dictionary_file_name file and the posting_file_name file and outputs the result in the
    file_of_output_name file
""""""
def search(dictionary_file_name, postings_file_name, queries_file_name, file_of_output_name):

    # the dictionary is loaded from file using the pickle library
    serialized_dictionary = open(dictionary_file_name, "r")
    dictionary = pickle.load(serialized_dictionary)
    serialized_dictionary.close()

    # queries are prepared using the above defined helper function
    queries = prepare_queries(queries_file_name, postings_file_name, dictionary)


    # the output file containing the results of the queries, each result on a different line
    output = open(file_of_output_name, "w")


    # the corpus (= posting list containing every document) is retrieved to be used for NOT operations.
    postings = open(postings_file_name, "r")
    postings.seek(dictionary[DOC_LIST][1])
    corpus = postings.readline()
    corpus = corpus[:-1]  # TODO DO MANUALLY
    postings.close()

    # every query is evaluated and the output written to the output file
    for query in queries:
        output.write(str(evaluate(query, corpus).to_string())+"\n")

    output.close()
"""

"""""
def usage():
    print
    "usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results"


dictionary_file = postings_file = file_of_queries = output_file_of_results = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError, err:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-d':
        dictionary_file = a
    elif o == '-p':
        postings_file = a
    elif o == '-q':
        file_of_queries = a
    elif o == '-o':
        file_of_output = a
    else:
        assert False, "unhandled option"

if dictionary_file == None or postings_file == None or file_of_queries == None or file_of_output == None:
    usage()
    sys.exit(2)

start = time.time()
search(dictionary_file, postings_file, file_of_queries, file_of_output)
end = time.time()
print("Query time : "+str(end - start))
"""""