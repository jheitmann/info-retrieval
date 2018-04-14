    #!/usr/bin/python
#A0174721H
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

ALPHA = 0.7
BETA = 0.3
def rocchio_algorithm(query):
    relevants = cosine_score(query)
    relevants = relevants.split()
    n_r = len(relevants)
    new_query = {}
    
    for term in query:
        new_query[term] += ALPHA
    
    for docid in relevants:
        for word,tf in most_common[docid]:
            w = (1+log(tf))/length[docid]
            new_query[word] += (BETA*w)/n_r
    
    return new_query



def query_expansion(query):
    query_expanded = []
    print("Query before expansion : "+' '.join(query))
    for term in query:
        hypernym = ""
        synsets = wn.synsets(term.lower())
        if len(synsets) != 0:
            hypernyms = synsets[0].hypernyms()
            if len(hypernyms) != 0:
                hypernym = hypernyms[0].lemmas()[0].name().replace('_', ' ')
        query_expanded.append(term)
        if hypernym != "":
            query_expanded.append(hypernym)
    print("Query after expansion : "+' '.join(query_expanded))
    return query_expanded

# return whether a given query (in a list format) is boolean
# boolean query either contain the "AND" keyword or contain phrasal queries delimited by ""
# the special case of a boolean query with one word only is going to be considered to be a phrasal query
def is_boolean_query(query):
    for term in query:
        if term == 'AND' or term[0] == '"':
            return True
    return False

def read_query_from_file(queries_file_name):
    query_file = open(queries_file_name, "r")
    query = query_file.readline()[:-1].split()
    query_file.close()
    return query

def and_op(postings1, postings2):
    result = ""
    postings1.rewind()
    postings2.rewind()
    element1 = postings1.next_node()
    element2 = postings2.next_node()

    while element1 is not None and element2 is not None:
        if element1 is not None and get_docID(element1) < get_docID(element2):
            element1 = postings1.next_node()
        elif element2 is not None and get_docID(element1) > get_docID(element2):
            element2 = postings2.next_node()
        else:
            result += element1
            element1 = postings1.next_node()
            element2 = postings2.next_node()

    return Postings(result)

def evaluate_boolean_query(query, dictionary, postings):
    parsed_query = parse_boolean_query(query)
    posting_list = fetch_posting_list(parsed_query[0], dictionary, postings)
    for i in range(1, len(query) - 1):
        posting_list_right = fetch_posting_list(parsed_query[i], dictionary, postings)
        posting_list = and_op(posting_list, posting_list_right)
    return posting_list

def number_of_terms_in_phrase(phrase):
    return len(phrase.split(' '))

def parse_boolean_query(query):
    parsed_query = []
    between_quotes = False
    phrase = ""
    for term in query:
        if term.startswith('"'):
            between_quotes = True
            phrase = term[1:]
        elif term.endswith('"'):
            between_quotes = False
            phrase += " "+term[:-1]
            parsed_query.append(tokenize(phrase))
        else:
            if between_quotes == True:
                phrase += " "+term
            elif term != 'AND':
                parsed_query.append(tokenize(term))
    return parsed_query

def tokenize(phrase):
    terms = nltk.word_tokenize(phrase)
    return ' '.join([stem_and_casefold(term) for term in terms])

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
    if term in dictionary:
        offset = dictionary[term][1]
        postings.seek(offset)
        posting_list = Postings(postings.readline())
    else:
        posting_list = Postings("")
    return posting_list

"""
    Actual search function that finds the top k documents for each query and writes the results in a filte
"""
def search(dictionary_file_name, postings_file_name, queries_file_name, file_of_output_name):

    #the dictionary is loaded from file using the pickle library
    serialized = open(dictionary_file_name, "r")
    dictionary = pickle.load(serialized)
    length = pickle.load(serialized)
    serialized.close()

    # the output file containing the results of the queries, each result on a different line
    output = open(file_of_output_name, "w")

    # queries are prepared using the above defined helper function
    postings = open(postings_file_name, "r")
    query = read_query_from_file(queries_file_name)

    if(is_boolean_query(query)):
        resulting_posting_list = evaluate_boolean_query(query, dictionary, postings)
        result = ""
        node = resulting_posting_list.next_node()
        while(node is not None):
            result = result + " " + str(get_docID(node))
            node = resulting_posting_list.next_node()
        if result != "":
            result = result[1:]
        output.write(result)

    else:
        prepared_query = [tokenize(term) for term in query]

        #uncomment for query expansion using synonyms
        #prepared_query = query_expansion(prepared_query)
        
        output.write(cosine_score(prepared_query, postings, dictionary, length))

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
search(dictionary_file, postings_file, file_of_queries, file_of_output)

"""
query = read_query_from_file(file_of_queries)
if is_boolean_query(query):
    print("The query is boolean")
    parsed_query = parse_boolean_query(query)
    print("The parsed boolean query is :")
    print(parsed_query)
else:
    print("The query is not boolean")
    query_expansion(query)
"""

end = time.time()
print("Query time : "+str(end - start))
