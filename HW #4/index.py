#!/usr/bin/python
import re
import nltk
import sys
import getopt
import linecache
import tempfile
import math
import csv
import os
import time
try:
   import cPickle as pickle
except:
   import pickle
from os import listdir
from tools import *
from nltk.corpus import stopwords

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

csv.field_size_limit(sys.maxsize) # Explain

# Sorted list of docIDs
#documents = sorted(map(int, listdir(input_directory))) # Change those
# Total number of documents
""" 
Given a document with docID N, doc_infos[N]=(lenght, court, top N most coomon terms)
length[N] stores its length, as described in the lecture
notes, in order to do length normalization.
"""
doc_infos = {}

TERM_SAVED = 10
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
uni_wnbr = BidirectionalDict()
tuple_wnbr = BidirectionalDict()

uni_size = 0
tuple_size = 0

uni_postings = []
tuple_postings = []

#Blocks related variables
DOCS_PER_BLOCK = 500
block_size = 0
block_dictionnaries =[]
block_posts_files=[]




#===================== update the top N most frequent term of a doc===========#
stopWords = set(stopwords.words('english'))
def update_infos(docid,reduced_word,tf):
	global stopWords
	global doc_infos
	if reduced_word in stopWords:
		return 0
	heap = doc_infos[docid][2]
	if (not heap) or heap[0][1] <tf:
		insert(heap,(reduced_word,tf))
		if len(heap) >TERM_SAVED:
			extract_min(heap)


#============================ Write index to block ===========================#
"""
What remains to be done is to compute the length of every document (square root of the 
sum of tf-idf score squares, computed for all terms in the document), while also 
updating the dictionary with the offset in the posting-list-file that corresponds to a 
certain word. FIXME Finally, we serialize both dictionary and length. FIXME
"""

def write_block(n):
	postName = "block"+str(n)
	with open(postName, 'w') as outfile_post: #,open(dicName, 'w') as outfile_dict:
		offset = 0
		global uni_wnbr
		global uni_postings
		global doc_infos
		global dictionary
		global tuple_wnbr
		global tuple_postings
		global block_dictionnaries
		global block_posts_files

		sortedTerms = dictionary.keys()
		sortedTerms.sort()

		#for i, next_line in enumerate(uni_postings):
		for reduced_word in sortedTerms:
			if " " in reduced_word:
				i = tuple_wnbr[reduced_word] # Explain
				next_line = tuple_postings[i]
				next_posting_list = Postings(next_line)

				dictionary[reduced_word] = (dictionary[reduced_word], offset) # Update the dictionary
				outfile_post.write(next_line)
				offset += len(next_line)
			else:
				i = uni_wnbr[reduced_word]
				next_line = uni_postings[i]
				next_posting_list = Postings(next_line)

				for next_node in next_posting_list: # Iterate over the (docID,term_frequency) pairs
					tf = get_tf(next_node)
					weight = 1 + math.log10(tf)
					docid = get_docID(next_node)
					doc_infos[docid][0] =doc_infos[docid][0]+ weight*weight # tf-idf square 
					update_infos(docid,reduced_word,tf)

				dictionary[reduced_word] = (dictionary[reduced_word], offset) # Update the dictionary
				outfile_post.write(next_line)
				offset += len(next_line)


		#pickle.dump(dictionary,outfile_dict)
		# Final length is obtained after computing the square root of the previous value
		#pickle.dump({docID: math.sqrt(score_acc) for docID, score_acc in length.items()}, outfile_dict) 
		
		
		#save the dictionnary and lenghts
		block_dictionnaries.append(dictionary)
		block_posts_files.append(postName)



#============================= Create the index (Part 1) =============================#
"""
Every file with a docID in documents is opened and read, its words are first processed 
by the nltk tokenizer and second by the stem_and_casefold(word_to_process) function, 
which yields a reduced form of the word.
"""
print "START INDEXING"
s = time.time()

with open(input_directory, 'rb') as csvfile: # Scan all the documents
	
	st = time.time()
	law_reports = csv.reader(csvfile, delimiter=',', quotechar='"')
	law_reports.next() # Explain (first line contains tags)
	for rep_nbr, report in enumerate(law_reports):
		#if rep_nbr == 250:
			#break # For testing purposes
		
		
		docID = int(report[0]) # Extract docID
		doc_infos[docID] = [0,report[4],[]]
		
		#print("Report being processed: " + str(docID))
		content = report[2].decode('UTF8').encode('ASCII',"ignore") # Extract content, encode to ASCII
		
		
		uni_words=[]
		tokens = nltk.word_tokenize(content)
		
		for token in tokens:
			uni_words.append(stem_and_casefold(token))
		
		#uni_words = map(stem_and_casefold, nltk.word_tokenize(content)) # Tokenized, then stemming/casefolding
		
		
		bi_words = map(lambda t: t[0] + " " + t[1], zip(uni_words,uni_words[1:])) # add function
		
		
		tri_words = map(lambda t: t[0] + " " + t[1] + " " + t[2], zip(uni_words,uni_words[1:],uni_words[2:])) # add function
		
		
		#print("First words of the report " + ", ".join(words[:10]) + '\n')
		all_words = uni_words + bi_words + tri_words
		
		
		for word_idx, reduced_word in enumerate(all_words):
			dictionary.setdefault(reduced_word,0)
			term_frequency = 1
			

			if dictionary[reduced_word] == 0: # First occurence of reduced_word 
				new_line = new_node(docID) + '\n' 

				# Append this newly created posting list to posting-list-file
				if word_idx < len(uni_words):
					uni_wnbr[reduced_word] = uni_size
					uni_postings.append(new_line)
					uni_size += 1
				else:
					tuple_wnbr[reduced_word] = tuple_size
					tuple_postings.append(new_line)
					tuple_size += 1

				dictionary[reduced_word] += 1 # doc_frequency updated 
			else: # reduced_word already in index
				if word_idx < len(uni_words):
					line_number = uni_wnbr[reduced_word] 
					line = uni_postings[line_number]
				else:
					line_number = tuple_wnbr[reduced_word]
					line = tuple_postings[line_number]
				"""
				Using linecache, lines start at 1 (not at 0)
				We need to clear the cache before loading a line, so that it includes
				the most recent changes made to it
				""" 
				
				posting_list = Postings(line)
				last_node = posting_list.value_at(-1) 
				last_docID = get_docID(last_node)

				"""
				If docID and last_docID are identical, we increment the term_frequency
				attribute of last_node. If not, we append a new node to the posting
				list.
				"""
				if  docID == last_docID: # term_frequency needs to be updated
					new_line = posting_list.to_string()[:-NODE_SIZE] + updated_tf(last_node) + '\n'
				else: # New node appended to the posting list
					new_line = posting_list.to_string() + new_node(docID) + '\n'
					dictionary[reduced_word] += 1 # doc_frequency updated

				if word_idx < len(uni_words):
					uni_postings[line_number] = new_line
				else:
					tuple_postings[line_number] = new_line
					
		
		#============================ Write index to block ===========================#
		if rep_nbr% DOCS_PER_BLOCK == DOCS_PER_BLOCK -1 :
			print "\nINDEXING BLOCK TIME"
			print time.time()-st
			t = time.time()
			block_size +=1
			block_number = rep_nbr/ DOCS_PER_BLOCK
			print "WRITE BLOCK "+str(block_number)
			write_block(block_number)
			
			dictionary = {}
			uni_wnbr = BidirectionalDict()
			tuple_wnbr = BidirectionalDict()

			uni_size = 0
			tuple_size = 0

			uni_postings = []
			tuple_postings = []
			print time.time() -t
			st = time.time()


if rep_nbr% DOCS_PER_BLOCK != DOCS_PER_BLOCK -1 :
	block_size +=1
	block_number = rep_nbr/ DOCS_PER_BLOCK
	print "WRITE BLOCK "+str(block_number)
	write_block(block_number)
	
	#make sure that we won't reuse these after
	uni_wnbr = None
	tuple_wnbr = None
	uni_size = 0
	tuple_size = 0

	uni_postings = None
	tuple_postings = None

print "\nINDEXING TIME"
print (time.time() -s)
#============================= Merge blocks in one file (Part2)=======================#
print "\nSTART MERGING"

#FIXME--DELETE
print "INITIALIZATION"
start = time.time()


dictionary = {}
post_files = []

# open files
for postName in block_posts_files:
	post_files.append(open(postName,"r"))

# list and sort all terms for each dictionnary
block_terms =[]
index_block = []
len_block = []
for dic  in block_dictionnaries:
	terms = dic.keys()
	terms.sort()
	block_terms.append(terms)
	index_block.append(0)
	len_block.append(len(terms)) 

#FIXME--DELETE
tot = time.time()-start
print tot
start = time.time()

# Merge
with open(output_file_postings,"w") as mergedPost:
	while True:
		#initialize
		termMin = None
		min_ids = []
		
		#identifie minimum term
		for idx in range(block_size):
			i = index_block[idx]
			if i>=len_block[idx]:
				continue
			if  termMin == None or block_terms[idx][i] < termMin:
				termMin = block_terms[idx][i]
				min_ids = [idx]
			elif block_terms[idx][i] == termMin:
				min_ids.append(idx)
				
		
		#close if all dictionnary are finished
		if termMin == None:
			break
		
		#compute total document frequency
		df = 0
		for idx in min_ids:
			df += block_dictionnaries[idx][termMin][0]
		
		#add in final dic
		dictionary[termMin] = (df,mergedPost.tell())
		
		
		#write all post in mergedPost
		final_posting = ""
		for idx in min_ids:
			#read postList
			posting_list = post_files[idx].readline()
			
			if posting_list[-1] == "\n":
				posting_list = posting_list[:-1]
			
			final_posting+= posting_list
			
			#update used term
			index_block[idx] += 1
			
		#write in final file
		mergedPost.write(final_posting+"\n")

#FIXME--DELETE
print "\nMERGE TIME"
print time.time()-start

print "WRITE DICO TIME"
temp = time.time()

#close files
for f in post_files:
	f.close()
for fname in block_posts_files:
	os.remove(fname)

with open(output_file_dictionary,"w") as outfile_dict:
	pickle.dump(dictionary,outfile_dict)
	# Final length is obtained after computing the square root of the previous value
	#FIXME
	pickle.dump({docID: (math.sqrt(info[0]),info[1],info[2]) for docID, info in doc_infos.items()}, outfile_dict) 

print time.time()-temp
print "COMPLETE"
print "Total TIME"
print time.time()-s
