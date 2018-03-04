#!/usr/bin/python
import re
import nltk
import sys
import getopt
import nltk
from nltk.stem.porter import *

DOC_LIST = "CORPUS"

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

def new_document(flag, docID):
    return pack_bytes(flag,1) + pack_bytes(docID,8)

def new_pointer(ptr):
    return  pack_bytes(ptr,8)

# Link: https://stackoverflow.com/questions/1063319/reversible-dictionary-for-python
class BidirectionalDict(dict): 
    def __setitem__(self, key, val):
        dict.__setitem__(self, key, val)
        dict.__setitem__(self, val, key)

    def __delitem__(self, key):
        dict.__delitem__(self, self[key])
        dict.__delitem__(self, key)