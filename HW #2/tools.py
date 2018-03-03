#!/usr/bin/python
import re
import nltk
import sys
import getopt

def tokenize(word_to_process): 
	return word_to_process

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

def unpack_string(s, nbr_bytes): # nbr_bytes = len(s)
    n = 0
    weight = 1
    for i in range(nbr_bytes):
        n += ord(s[-1]) * weight
        s = s[:-1]
        weight = weight * 0xff
    return n

def new_document(flag, docID):
    return pack_bytes(flag,1) + pack_bytes(docID,4)

def new_pointer(ptr):
    return  pack_bytes(ptr,4)

# Link: https://stackoverflow.com/questions/1063319/reversible-dictionary-for-python
class BidirectionalDict(dict): 
    def __setitem__(self, key, val):
        dict.__setitem__(self, key, val)
        dict.__setitem__(self, val, key)

    def __delitem__(self, key):
        dict.__delitem__(self, self[key])
        dict.__delitem__(self, key)

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

    