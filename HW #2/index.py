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

documents = sorted(map(int, listdir(input_directory)[:50])) # 10 for testing purposes, save in txt file

dictionary = {} # Inverted index
word_number = BidirectionalDict() # word --> number/line is a bijective mapping
vocab_size = 0

open(output_file_postings,'w').close() # Create empty file

#============================ Create the index (Part 1) ============================#
for docID in documents: # Scan all the documents
	doc_path = input_directory + str(docID) # Absolute path of the current document

	with open(doc_path, 'r') as next_doc:

		for line in next_doc:
			words = nltk.word_tokenize(line) # Tokenized words

			for word in words:
				reduced_word = stem_and_casefold(word) # Change this
				dictionary.setdefault(reduced_word,0)

				if dictionary[reduced_word] == 0: # First occurence of reduced_word
					word_number[reduced_word] = vocab_size # Update word_number
					#print "A word not seen: " + '(' + word + ')' + '\n' # Debug
					new_line = new_document(0,docID) + '\n' # flag | docID (5 bytes), 1st one for debug: pack_bytes(vocab_size,4) + 
					
					with open(output_file_postings, 'a') as outfile_post: # Append this new line
						outfile_post.write(new_line)

					dictionary[reduced_word] += 1
					vocab_size += 1 

				else: # Word already in index
					#print "------- STATS -------\n"
					#print "A word in doc nbr " + str(docID) + ": " + '(' + word + ')' + '\n' # Debug
					line_number = word_number[reduced_word]
					#print "Line number: " + str(line_number) + '\n' # Debug
					linecache.clearcache() # Explain this one
					posting_list = linecache.getline(output_file_postings,line_number+1)[:-1] # '\n' ignored, explain +1
					#print "Actual line vs line number: " + str(line_number) + " vs " + str(unpack_string(posting_list[:8])) + '\n'
					#print "Length of posting list: " + str(len(posting_list)) + '\n' # Debug
					#print "------- END STATS -------\n"
					last_docID = unpack_string(posting_list[-4:])

					if  last_docID != docID: # Explain args
						new_line = posting_list + new_document(0,docID) + '\n' # Add auxiliary method?
						replace_line(output_file_postings, line_number, new_line) # Need to overwrite the whole file
						dictionary[reduced_word] += 1


#============================ Add Skip pointers (Part 2) ============================#
fp = tempfile.TemporaryFile()

#print "Vocabulary size: " + str(vocab_size) + '\n' # Debug

with open(output_file_postings, 'r') as outfile_post:
	for i, next_posting_list in enumerate(outfile_post):
		#print "Ith word: " + str(i) + '\n' # Debug
		reduced_word = word_number[i]
		doc_frequency = dictionary[reduced_word]
		floor = int(math.floor(math.sqrt((len(next_posting_list)-1)/9))) # -1: '\n', 9 = length of docID
		nbr_skip_ptr = floor-1  # Explain this value
		length_skip_ptr = floor+1 # No skip pointers overlap, hence l * 9chars(1: flag | 8: docID)
		new_line = next_posting_list
		for j in range(nbr_skip_ptr):
			ptr_addr = 9*(j*length_skip_ptr) + 8*j # Explain this formula
			ptr = ptr_addr+9*(length_skip_ptr+1)-1 # Explain this formula
			new_line = new_line[:ptr_addr] + new_document(1, unpack_string(new_line[ptr_addr:ptr_addr+9])) + new_pointer(ptr) + new_line[ptr_addr+9:] # Explain
		fp.write(new_line)

fp.seek(0)
with open(output_file_postings, 'w') as outfile_post:
	for next_posting_list in fp:
		outfile_post.write(next_posting_list)
fp.close()


#============================ Write index to file (Part3) ============================#
with open(output_file_postings, 'r') as outfile_post, open(output_file_dictionary, 'w') as outfile_dict: # Problem with no such file
	offset = 0

	for i, next_posting_list in enumerate(outfile_post):
		#print "Ith word: " + str(i) + '\n' # Debug
		reduced_word = word_number[i]
		dictionary[reduced_word] = (dictionary[reduced_word], offset) 
		offset += len(next_posting_list)

	pickle.dump(dictionary,outfile_dict)
	outfile_dict.flush()