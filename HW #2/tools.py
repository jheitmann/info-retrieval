#!/usr/bin/python
import re
import nltk
import sys
import getopt
import nltk
from nltk.stem.porter import *

def stem_and_casefold(word_to_process):
    #TODO may want to initialize stemer outside function
    stemmer = PorterStemmer()
    word = stemmer.stem(word_to_process)
    word = word.lower()
    return word

"""
Packs integer n into its hexadecimal representation string,
of length nbr_bytes (Big Endian format)
"""
def pack_bytes(n, nbr_bytes):
    s = ""
    while n:
        s = chr(n % 0x100) + s
        n = n / 0x100
    s = s.rjust(nbr_bytes, "\x00")
    return s

def unpack_string(s, nbr_bytes):
    #print s # Debug
    n = 0
    weight = 1
    for i in range(nbr_bytes):
        n += ord(s[-1]) * weight
        s = s[:-1]
        weight = weight * 0xff
    return n

def new_document(docID):
    return pack_bytes(0,1) + pack_bytes(docID,4)

def new_pointer(ptr):
    return pack_bytes(1,1) + pack_bytes(ptr,4)

class Root(object):
    def __init__(self, docID):
        self.head = Element(docID)
        self.last = self.head
        return

    def append_element(self, element):
        self.last.add_next(element)
        self.last = element
        return

    def insert_after(self, predecessor, element): # Needs to be implemented
        return 



class Element(object):
    def __init__(self, docID):
        self.docID = docID
        return

    def add_next(self, element):
        self.next = element
        return

    def add_skip_pointer(self, element):
	    self.skip_pointer = element
	    return

    