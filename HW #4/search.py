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
from nltk.corpus import wordnet as wn #TODO how to correctly import for submission ?

def query_expansion(queries_file_name):
    # output list of queries
    query = []
    raw_query = open(queries_file_name, "r")
    line = raw_query.readline()
    # delete the line return that comes with readline()
    line = line[:-1]
    print("Query before expansion : "+line)
    for term in line.split():
        hypernym = ""
        synsets = wn.synsets(term.lower())
        if len(synsets) != 0:
            hypernyms = synsets[0].hypernyms()
            if len(hypernyms) != 0:
                hypernym = hypernyms[0].lemmas()[0].name().replace('_', ' ')
        query.append(term)
        if hypernym != "":
            query.append(hypernym)
    print("Query after expansion : "+' '.join(query))
    raw_query.close()
    return query

"""
    Helper function that takes the name of a text file with free text queries, in which there is one query by line
    and returns a list of queries. (a query is also a list, thus the function returns a list of lists)
"""
def prepare_queries(queries_file_name):
    # output list of queries
    queries = []

    raw_queries = open(queries_file_name, "r")

    # each query in the queries_file is traversed
    for line in raw_queries:
        terms = nltk.word_tokenize(line)
        queries.append([stem_and_casefold(term) for term in terms])
    raw_queries.close()
    return queries

"""
    Helper function that finds the top 10 documents based on the cosine similarity based on the pseudo code provided
    in class.
"""
def cosine_score(query, postings, dictionary, length):

    scores = dict()
    N = len(length) #Already defined
    w_t_q = compute_w_t_q(query, dictionary, N)
    for term in query:
        if term in dictionary:
            posting_list = fetch_posting_list(term, dictionary, postings)
            for pair in posting_list:
                document = get_docID(pair)
                tf_t_d = get_tf(pair)
                w_t_d = 1 + log10(tf_t_d)
                scores[document] = scores.get(document, 0) + w_t_d * w_t_q[term] # use td_weight
    for document in scores:
        scores[document] = scores[document] / length[document]

    return top_k(scores)

"""
    returns a map from the terms in the query given in parameter to their corresponding weights in the query (tfxidf)
"""
def compute_w_t_q(query, dictionary, N):
    # PHASE 1 : count the number of occurrences of each term in the query (i.e compute the term frequency)
    tf = dict()
    for term in query:
        tf[term] = tf.get(term, 0) + 1

    # PHASE 2 : for each term, compute the log TF * IDF score.
    w_t_q = dict()
    for term in tf:
        w_t_q[term] = 0
        if term in dictionary:
            w_t_q[term] = td_weight(tf[term], dictionary[term][0], N)

    return w_t_q


"""
    Reads a posting list from file given a term and the dictionary
"""
def fetch_posting_list(term, dictionary, postings):
    offset = dictionary[term][1]
    postings.seek(offset)
    posting_list = Postings(postings.readline())
    return posting_list

"""
    Actual search function that finds the top k documents for each query and writes the results in a filte
"""
def search(dictionary_file_name, postings_file_name, queries_file_name, file_of_output_name):

    # the dictionary is loaded from file using the pickle library
    serialized = open(dictionary_file_name, "r")
    dictionary = pickle.load(serialized)
    length = pickle.load(serialized)
    serialized.close()

    # the output file containing the results of the queries, each result on a different line
    output = open(file_of_output_name, "w")

    # queries are prepared using the above defined helper function
    postings = open(postings_file_name, "r")
    queries = prepare_queries(queries_file_name)

    # every query is evaluated and the output written to the output file
    for query in queries:
        output.write(cosine_score(query, postings, dictionary, length) + '\n')#GET RID OF LAST LINE RETURN

    postings.close()
    output.close()


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
# search(dictionary_file, postings_file, file_of_queries, file_of_output)
query_expansion(file_of_queries)
end = time.time()
print("Query time : "+str(end - start))