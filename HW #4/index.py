#!/usr/bin/python
import re
import nltk
import sys
import getopt
import linecache
import tempfile
import math
try:
   import cPickle as pickle
except:
   import pickle
from os import listdir
from tools import *

def usage():
    print "usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file"


input_directory = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError, err:
    usage()
    sys.exit(2)
    
for o, a in opts:
    if o == '-i': # input directory
        input_directory = a
    elif o == '-d': # dictionary file
        output_file_dictionary = a
    elif o == '-p': # postings file
        output_file_postings = a
    else:
        assert False, "unhandled option"
        
if input_directory == None or output_file_postings == None or output_file_dictionary == None:
    usage()
    sys.exit(2)


# Sorted list of docIDs
documents = sorted(map(int, listdir(input_directory))) 
# Total number of documents
NRB_DOCS = len(documents)
""" 
Given a document with docID N, length[N] stores its length, as described in the lecture
notes, in order to do length normalization.
"""
length = {docID: 0 for docID in documents}
"""
dictionary is our inverted index, in part 1 it contains the mapping 
(word: doc_frequency). Part 2 then adds to the value of a (key,value) tupple the 
position of the posting list that corresponds to the key (a word). Hence the final 
mapping is the following: (word: (doc_frequency, offset)).
"""
uni_dic = {}
bi_dic = {}
tri_dic = {}
"""
(word: number) is a bijective mapping, if word is the ith term encountered during the
indexing phase, then number = i. Once the index is complete, number ranges from 0 to 
vocabulary-size-1. This bidirectional dictionary is useful to us, because it can be
used to determine the line in the posting-list-file that corresponds to a given word, 
and vice versa.
"""
word_number = BidirectionalDict() 
vocab_size = 0 # Number of words encountered, grows with the dictionary

open(output_file_postings,'w').close() # Create an empty file

#============================= Create the index (Part 1) =============================#
"""
Every file with a docID in documents is opened and read, its words are first processed 
by the nltk tokenizer and second by the stem_and_casefold(word_to_process) function, 
which yields a reduced form of the word.
"""
for docID in documents: # Scan all the documents
	doc_path = input_directory + str(docID) # Absolute path of the current document

	with open(doc_path, 'r') as next_doc:

		for line in next_doc:
			words = nltk.word_tokenize(line) # Tokenized words
			for word in words:
				reduced_word = stem_and_casefold(word) # Applies stemming and case-folding
				uni_dic.setdefault(reduced_word,0)

				if uni_dic[reduced_word] == 0: # First occurence of reduced_word
					word_number[reduced_word] = vocab_size 
					new_line = new_node(docID) + '\n' 

					# Append this newly created posting list to posting-list-file
					with open(output_file_postings, 'a') as outfile_post: 
						outfile_post.write(new_line) 

					uni_dic[reduced_word] += 1 # doc_frequency updated 
					vocab_size += 1 # A new word

				else: # reduced_word already in index
					line_number = word_number[reduced_word] 
					"""
					Using linecache, lines start at 1 (not at 0)
					We need to clear the cache before loading a line, so that it includes
					the most recent changes made to it
					"""
					linecache.clearcache() 
					line = linecache.getline(output_file_postings,line_number+1)
					posting_list = Postings(line)
					last_node = posting_list.value_at(-1) 
					last_docID = get_docID(last_node)

					"""
					If docID and last_docID are identical, we increment the term_frequency
					attribute of last_node. If not, we append a new node to the posting
					list.
					"""
					if  docID == last_docID: # term_frequency needs to be updated
						update_last_node(output_file_postings, line_number)
					else: # New node appended to the posting list
						new_line = posting_list.to_string() + new_node(docID) + '\n' 
						update_posting_list(output_file_postings, line_number, new_line)  
						uni_dic[reduced_word] += 1 # doc_frequency updated



#============================ Write index to file (Part 2) ===========================#
"""
What remains to be done is to compute the length of every document (square root of the 
sum of tf-idf score squares, computed for all terms in the document), while also 
updating the dictionary with the offset in the posting-list-file that corresponds to a 
certain word. Finally, we serialize both dictionary and length.
"""
with open(output_file_postings, 'r+') as outfile_post, open(output_file_dictionary, 'w') as outfile_dict:
	offset = 0

	for i, next_line in enumerate(outfile_post):
		reduced_word = word_number[i]
		next_posting_list = Postings(next_line)

		for next_node in next_posting_list: # Iterate over the (docID,term_frequency) pairs
			weight = 1 + math.log10(get_tf(next_node))
			length[get_docID(next_node)] += weight*weight # tf-idf square 

		uni_dic[reduced_word] = (uni_dic[reduced_word], offset) # Update the dictionary
		offset += len(next_line)

	pickle.dump(uni_dic,outfile_dict)
	# Final length is obtained after computing the square root of the previous value
	pickle.dump({docID: math.sqrt(score_acc) for docID, score_acc in length.items()}, outfile_dict) 
