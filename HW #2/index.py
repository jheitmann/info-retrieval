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
from tools import tokenize
from tools import Root
from tools import Element

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

NUMBER_OF_DOCS = 10 # Number of documents in the directory directory-of-documents, total = 14818

index = {} # Inverted index
vocab_size = 0

with open(output_file_dictionary, 'w') as outfile_dict, open(output_file_postings, 'r+') as outfile_post: # Problem with no such file
	# Create the index (Part 1)
	for doc in range(1, NUMBER_OF_DOCS+1):
		doc_path = input_directory + str(doc)
		with open(doc_path, 'r') as next_doc:
			for line in next_doc:
				words = line.split(' ')
				for word in words:
					tokenized_word = tokenize(word)
					index.setdefault(tokenized_word, (vocab_size, 0, 777)) # 777 should be replaced by offset...
					if index[tokenized_word][1] == 0 :
						new_line = pickle.dumps(Root(doc)) + '\n' # Serializes a new root, containing doc
						outfile_post.seek(0,2) # 2: we want to append the new words posting list
						outfile_post.write(new_line)
						index[tokenized_word] = (index[tokenized_word][0], index[tokenized_word][1]+1, index[tokenized_word][2]) # First occurence, change this
						vocab_size += 1 
					else:
						"""
						linecache loads the nth line of outfile_post into cache, where n is index[tokenized_word]
						This line is a serialized linked list, pickle.loads deserializes the line and saves it as 
						posting_list
						"""
						line_number = index[tokenized_word][0]
						posting_list = pickle.loads(linecache.getline(output_file_postings,line_number)) # Cache -> clear, -1 : remove newline [:-1]
						if posting_list.last.docID != doc:
							posting_list.append_element(Element(doc))
							new_line = pickle.dumps(posting_list) + '\n'
							# Need to overwrite the whole file
							output_file.seek(0)
							fp = tempfile.TemporaryFile() # temporay file
							fp.write(new_line)
							offset = 0
							for i, next_posting_list in enumerate(outfile_post):
								if i < line_number:
									offset += len(next_posting_list)
								elif i > line_number:
									fp.write(next_posting_list)

							fp.seek(0)
							outfile_post.seek(offset) 
							for pl in fp:
								outfile_post.write(pl)
							fp.close()

							index[tokenized_word] = (index[tokenized_word][0], index[tokenized_word][1]+1, index[tokenized_word][2]) # Change this
	linecache.clearcache()
	# Add Skip pointers (Part 2)