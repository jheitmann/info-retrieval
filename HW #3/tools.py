#!/usr/bin/python
import re
import nltk
import sys
import getopt
import math
import tempfile
import nltk
from nltk.stem.porter import *

DOC_LIST = "CORPUS" # Special word, to store the entire list of docIDs
FLAG_SIZE = 1 # Flag indicates whether or not a node containing a docID has a skip pointer
ELEM_SIZE = 8 # Elem is either a docID or a pointer, that is a position in a posting list
NODE_SIZE = FLAG_SIZE+ELEM_SIZE # A node is a flag and a docID
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
def new_node(flag, docID):
    return pack_bytes(flag,FLAG_SIZE) + pack_bytes(docID,ELEM_SIZE)

# Returns a new pointer
def new_pointer(ptr):
    return  pack_bytes(ptr,ELEM_SIZE)

# Returns the address (position in a string) of the (n+1)th node that has a skip pointer
def node_addr(n, skip_ptr_length):
    return n*(skip_ptr_length*NODE_SIZE + ELEM_SIZE) 

# Returns the pointer value of a given node
def ptr_value(node_addr, skip_ptr_length):
    return node_addr + ELEM_SIZE + skip_ptr_length*NODE_SIZE 

# This value will be used to insert a skip pointer
def skip_value(length):
    return int(math.floor(math.sqrt(length/NODE_SIZE)))

"""
In order to replace a specific line in a file, the subsequent lines must be 
overwritten. Hence this method stores the new line (that replaces the old one)
and the subsequent lines in a temporary file, then overwrites the initial file, 
starting at the line to be replaced.
"""
def replace_line(file, line_number, new_line):
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