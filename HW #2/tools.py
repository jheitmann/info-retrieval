#!/usr/bin/python
import re
import nltk
import sys
import getopt
import math
import tempfile
import nltk
from nltk.stem.porter import *

DOC_LIST = "CORPUS"
FLAG_SIZE = 1 # Flag indicates wheter or not a node containing a DOCID has a skip pointer
ELEM_SIZE = 8 # Elem is either a DOCID or a pointer, that is a position in a posting list
NODE_SIZE = FLAG_SIZE+ELEM_SIZE

def stem_and_casefold(word_to_process):
    #TODO may want to initialize stemer outside function
    stemmer = PorterStemmer()
    word = stemmer.stem(word_to_process)
    word = word.lower()
    return word

def pack_bytes(n, nbr_chars):
    return format(n, "0"+ str(nbr_chars) + "x")

def unpack_string(s):
    return int(s,16) # explain 16

def new_node(flag, docID):
    return pack_bytes(flag,FLAG_SIZE) + pack_bytes(docID,ELEM_SIZE)

def new_pointer(ptr):
    return  pack_bytes(ptr,ELEM_SIZE)

# Returns the address (position in a string) of the (n+1)th node that has a skip pointer
def node_addr(n, skip_ptr_length):
    return n*(skip_ptr_length*NODE_SIZE + ELEM_SIZE) # 9*(j*skip_ptr_length) + 8*j

# Returns the pointer value of a given node
def ptr_value(node_addr, skip_ptr_length):
    return node_addr + ELEM_SIZE + skip_ptr_length*NODE_SIZE # ptr_addr+9*(skip_ptr_length+1)-1

def skip_value(length):
    return int(math.floor(math.sqrt(length/NODE_SIZE)))

# Explain this method
def replace_line(file, line_number, new_line):
    with open(file, 'r+') as outfile:
        fp = tempfile.TemporaryFile() 
        fp.write(new_line)

        offset = 0
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

# Link: https://stackoverflow.com/questions/1063319/reversible-dictionary-for-python
class BidirectionalDict(dict): 
    def __setitem__(self, key, val):
        dict.__setitem__(self, key, val)
        dict.__setitem__(self, val, key)

    def __delitem__(self, key):
        dict.__delitem__(self, self[key])
        dict.__delitem__(self, key)