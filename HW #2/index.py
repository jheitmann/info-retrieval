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

documents = listdir(input_directory).[:20] # 10 for testing purposes

index = {} # Inverted index
word_number = BidirectionalDict() # word --> number/line is a bijective mapping
vocab_size = 0

open(output_file_postings,'w').close() # Create empty file

# Create the index (Part 1)
for docID, doc_name in enumerate(documents): # Scan all the documents
	doc_path = input_directory + doc_name # Absolute path of the current document

	with open(doc_path, 'r') as next_doc:

		for line in next_doc: 
			words = line.split(' ') # Should not be done here, tokenize() will take care of this

			for word in words:
				linecache.clearcache() # Explain this one
				tokenized_word = tokenize(word) # Change this
				index.setdefault(tokenized_word,0)

				if index[tokenized_word] == 0: # First occurence of tokenized_word
					word_number[tokenized_word] = vocab_size # Update word_number
					#print "A word not seen: " + '(' + word + ')' + '\n' # Debug
					new_line = new_document(0,docID) + '\n' # flag | docID (5 bytes)
					
					with open(output_file_postings, 'a') as outfile_post: # Append this new line
						outfile_post.write(new_line)

					index[tokenized_word] +=1
					vocab_size += 1 

				else: # Word already in index
					#print "A word: " + '(' + word + ')' + '\n' # Debug
					line_number = word_number[tokenized_word]
					#print "Line number: " + str(line_number) + '\n' # Debug
					posting_list = linecache.getline(output_file_postings,line_number)[:-1] # '\n' ignored
					#print "Length of posting list: " + str(len(posting_list)) + '\n' # Debug
					last_docID = unpack_string(posting_list[-4:], 4)

					if  last_docID != docID: # Explain args
						new_line = posting_list + new_document(0,docID) + '\n' # Add auxiliary method?
						replace_line(output_file_postings, line_number, new_line) # Need to overwrite the whole file
						index[tokenized_word] += 1
# Add Skip pointers (Part 2)

# Write index to file (Part3)
with open(output_file_postings, 'r') as outfile_post, open(output_file_dictionary, 'w') as outfile_dict: # Problem with no such file
	offset = 0

	for i, next_posting_list in enumerate(outfile_post):
		tokenized_word = word_number[i]
		index[tokenized_word] = (index[tokenized_word], offset) 
		offset += len(next_posting_list)

	outfile_dict.write(pickle.dumps(index))