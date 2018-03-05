#!/usr/bin/python
import re
import nltk
import sys
import getopt
import linecache
import tempfile
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
documents = sorted(map(int, listdir(input_directory))) # [:200] for testing purposes

"""
dictionary is our inverted index, in part 1 & 2 it contains the mapping 
(word: doc_frequency). Part 3 then adds to the value of a (key,value) tupple the 
position of the posting list that corresponds to the key (a word). Hence the final 
mapping is the following: (word: (doc_frequency, offset)).
"""
dictionary = {} 
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
				dictionary.setdefault(reduced_word,0)

				if dictionary[reduced_word] == 0: # First occurence of reduced_word
					word_number[reduced_word] = vocab_size 
					new_line = new_node(0,docID) + '\n' 

					# Append this newly created posting list to posting-list-file
					with open(output_file_postings, 'a') as outfile_post: 
						outfile_post.write(new_line) 

					dictionary[reduced_word] += 1 # doc_frequency updated 
					vocab_size += 1 # A new word

				else: # reduced_word already in index
					line_number = word_number[reduced_word] 
					"""
					Using linecache, lines start at 1 (not at 0)
					We need to clear the cache before loading a line, so that it includes
					the most recent changes made to it
					"""
					linecache.clearcache() 
					posting_list = linecache.getline(output_file_postings,line_number+1)[:-1] # [:-1]: '\n' ignored
					last_docID = unpack_string(posting_list[-ELEM_SIZE:]) # docID of the last node in posting_list

					"""
					If docID and last_docID are identical, nothing needs to be done.
					If not, docID will be appended to the posting list of the current 
					word, and this posting list is properly updated in the posting-list
					-file
					"""
					if  docID != last_docID: 
						new_line = posting_list + new_node(0,docID) + '\n' 
						replace_line(output_file_postings, line_number, new_line)  
						dictionary[reduced_word] += 1 # doc_frequency updated


#============================ Add Skip pointers (Part 2) =============================#
"""
At this point we have a complete posting-list-file, without any skip pointers. We read 
every line of the posting-list-file, check if skip pointers can be inserted, and if so, 
write a modified line (that has all the skip pointers) to a temporary file. Once we 
reached the end of posting-list-file, we overwrite it using the lines from the temporary
file. 
"""
fp = tempfile.TemporaryFile()

with open(output_file_postings, 'r+') as outfile_post:

	for next_posting_list in outfile_post:
		skip_val = skip_value(len(next_posting_list[:-1])) # [:-1]: '\n' ignored
		"""
		Heuristics show that these two values work just fine for any possible posting-
		list length (especially small and perfect square lengths)
		"""
		nbr_skip_ptr = skip_val-1 # Number of skip pointers to be inserted
		skip_ptr_length = skip_val+1 # Length of a skip pointer (#nodes skipped + 1)

		new_line = next_posting_list
		for i in range(nbr_skip_ptr):
			# Comments in tools.py provide a detailed description of the following methods
			next_addr = node_addr(i,skip_ptr_length)
			node_string = unpack_string(new_line[next_addr:(next_addr+NODE_SIZE)])
			ptr = ptr_value(next_addr,skip_ptr_length) 
			
			# Node (delimited by []) with flag set to 1: NODES |[FLAG = 1 (1 char) | docID (8 chars)]| ptr (8 chars)| NODES
			new_line = new_line[:next_addr] + new_node(1,node_string) + new_pointer(ptr) + new_line[(next_addr+NODE_SIZE):]
		fp.write(new_line)
	
	# Overwrite posting-list-file with the new posting-lists, that include skip pointers
	fp.seek(0) 
	outfile_post.seek(0)
	for next_posting_list in fp:
		outfile_post.write(next_posting_list)
	fp.close()
	

#============================ Write index to file (Part 3) ===========================#
"""
What remains to be done is to add a special word to the dictionary, whose corresponding 
posting-list contains all the docIDs (which we append to the posting-list-file), and 
finally to serialize the dictionary in a txt file.
"""
with open(output_file_postings, 'r+') as outfile_post, open(output_file_dictionary, 'w') as outfile_dict:
	# ---- Add a special word to the dictionary to get the list of all documents ---- #
	word_number[DOC_LIST] = vocab_size

	new_line = ""
	for docID in documents:
		new_line += new_node(0,docID)
	new_line += '\n'

	outfile_post.seek(0,2) # Append the list of all documents
	outfile_post.write(new_line)
	dictionary[DOC_LIST] = len(documents)
	vocab_size += 1

	# ---------------- Serialize the dictionary and save it in a file --------------- #
	outfile_post.seek(0)
	
	offset = 0
	for i, next_posting_list in enumerate(outfile_post):
		reduced_word = word_number[i]
		dictionary[reduced_word] = (dictionary[reduced_word], offset) 
		offset += len(next_posting_list)

	pickle.dump(dictionary,outfile_dict)
	outfile_dict.flush()