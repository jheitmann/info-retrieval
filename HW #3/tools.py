#!/usr/bin/python
import re
import nltk
import sys
import getopt
import math
import tempfile
import nltk
from nltk.stem.porter import *

DOC_LIST = "CORPUS" # Special word, to store the entire list of docIDs -> not needed anymore
ELEM_SIZE = 8 # Elem is either a docID or a pointer, that is a position in a posting list
NODE_SIZE = 2*ELEM_SIZE # A node is a flag and a docID
stemmer = PorterStemmer() # stem_and_casefold(word_to_process) uses this stemmer

# Applies the Porter Stemming algorithm, then case-folding
def stem_and_casefold(word_to_process):
    word = stemmer.stem(word_to_process)
    word = word.lower()
    return word

# Returns the hexadecimal string of an int, using nbr_chars characters
def pack_bytes(n, nbr_chars):
    return format(n, "0"+ str(nbr_chars) + "x")

# Returns the int value of the hexadecimal string s
def unpack_string(s):
    return int(s,16) 

# Returns a new node
def new_node(docID):
    return pack_bytes(docID,ELEM_SIZE) + pack_bytes(1,ELEM_SIZE)

# Returns the docID of a node
def get_docID(node):
    return unpack_string(node[:ELEM_SIZE])

# Returns the term frequency of a node
def get_tf(node):
    return unpack_string(node[ELEM_SIZE:])

"""
Given a node with a term frequency tf, returns a new node with identical 
docID and term frequency tf+1
"""
def updated_tf(node):
    incr_tf = get_tf(node)+1
    return pack_bytes(get_docID(node),ELEM_SIZE) + pack_bytes(incr_tf,ELEM_SIZE)

# Explain
def td_weight(term_frequency, doc_frequency, nbr_docs):
    return (1+math.log10(term_frequency))*math.log10(nbr_docs/doc_frequency)

"""
Explain this method, change replace_line to append node?
"""
def update_last_node(file, line_number):
    with open(file, 'r+') as outfile:
        for i in range(0, line_number+1): # Explain +1
            next_posting_list = outfile.readline()

        last_node = Postings(next_posting_list).value_at(-1)
        outfile.seek(-(NODE_SIZE+1),1) # +1: '\n' at the end of a line
        outfile.write(updated_tf(last_node))

"""
In order to replace a specific line in a file, the subsequent lines must be 
overwritten. Hence this method stores the new line (that replaces the old one)
and the subsequent lines in a temporary file, then overwrites the initial file, 
starting at the line to be replaced.
"""
def update_posting_list(file, line_number, new_line):
    with open(file, 'r+') as outfile:
        fp = tempfile.TemporaryFile() 
        fp.write(new_line)

        offset = 0 # Offset represents the position of the line to be replaced
        for i, line in enumerate(outfile):
            if i < line_number:
                offset += len(line)
            elif i > line_number:
                fp.write(line)

        fp.seek(0) 
        outfile.seek(offset) 
        for pl in fp:
            outfile.write(pl)
        fp.close()

"""
    This class encapsulates a raw posting-list and offers a convenient interface 
    to interact with it. A node in the posting-list has the following internal
    structure: [ docID (8 chars) | term_frequency (8 chars) ]
"""
class Postings(object):

    def __init__(self, posting_list):
        if(posting_list[-1:] == "\n"):
            posting_list = posting_list[:-1] # [:-1]: '\n' ignored
        self.postings = posting_list
        self.nbr_nodes = len(posting_list)/NODE_SIZE # Explain
        self.pointer = 0
        return

    # jumps to the specified position in the list (relative position)
    def jump(self, position): 
        if(position < nbr_nodes):
            pointer = position*NODE_SIZE

    # jumps to the first element in the list
    def rewind(self):
        self.jump(0)

    # Explain
    def value_at(self, position):
        if position == -1:
            node = self.postings[-NODE_SIZE:]
            return node
        elif -nbr_nodes <= position < nbr_nodes:
            node = self.postings[position*NODE_SIZE:(position+1)*NODE_SIZE]
            return node 
        else:
            return None

    # next jumps to the next element (or None if no element) and returns it.
    def next(self):
        if not self.pointer < (self.nbr_nodes*NODE_SIZE):
            return None

        next_node = self.postings[self.pointer:self.pointer+NODE_SIZE]
        self.pointer += NODE_SIZE
        return next_node

    # iterates through the posting_list to output a string version of it
    def to_string(self):
        return self.postings

""" 
Taken from: stackoverflow.com/questions/1063319/reversible-dictionary-for-python
A bidirectional dictionary (need to have bijective mapping)
"""
class BidirectionalDict(dict): 
    def __setitem__(self, key, val):
        dict.__setitem__(self, key, val)
        dict.__setitem__(self, val, key)

    def __delitem__(self, key):
        dict.__delitem__(self, self[key])
        dict.__delitem__(self, key)