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
from nltk.tokenize import RegexpTokenizer

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

open("tmp_bi_post",'w').close() # Create an empty file

# Sorted list of docIDs
#documents = sorted(map(int, listdir(input_directory))) # Change those
# Total number of documents
""" 
Given a document with docID N, doc_infos[id]=(lenght, court, top N most coomon terms)
length[N] stores its length, as described in the lecture
notes, in order to do length normalization.
"""
doc_infos = {}

TERM_SAVED = 50
"""
dictionary is our inverted index, in part 1 & 2 it contains the mapping 
(word: doc_frequency). Part 3 then adds to the value of a (key,value) tuple the 
position of the posting list that corresponds to the key (a word). Hence the final 
mapping is the following: (word: (doc_frequency, offset)).
"""
dictionary = {}

# TODO: explain
bi_dictionary = {} # added

"""
(word: number) is a bijective mapping, if word is the ith term encountered during the
indexing phase, then number = i. Once the index is complete, number ranges from 0 to 
vocabulary-size-1. This bidirectional dictionary is useful to us, because it can be
used to determine the line in the posting-list-file that corresponds to a given word, 
and vice versa.
"""
uni_wnbr = BidirectionalDict()

uni_size = 0

uni_postings = []
#Blocks related variables
DOCS_PER_BLOCK = 500
block_size = 0
block_dictionnaries =[]
block_posts_files=[]
block_bi_posts_files=[] # added


#===================== update the top N most frequent term of a doc===========#
TOO_COMMON_DF = 5000
stopWords = set(map(stem_and_casefold ,stopwords.words('english')))
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
	bi_post_name = "bi_block"+str(n)
	with open(postName, 'w') as outfile_post, open(bi_post_name, 'w') as outfile_bi_post: #,open(dicName, 'w') as outfile_dict:
		global uni_wnbr
		global uni_postings
		global doc_infos
		global dictionary
		global bi_dictionary # added
		global block_dictionnaries
		global block_posts_files
		global block_bi_posts_files # added

		offset = 0
		sortedTerms = dictionary.keys()
		sortedTerms.sort()

		#for i, next_line in enumerate(uni_postings):
		for reduced_word in sortedTerms:
			i = uni_wnbr[reduced_word]
			next_line = uni_postings[i]
			next_posting_list = Postings(next_line)

			for next_node in next_posting_list: # Iterate over the (docID,term_frequency) pairs
				tf = get_tf(next_node)
				weight = 1 + math.log10(tf)
				docid= get_docID(next_node)
				doc_infos[docid][0] =doc_infos[docid][0]+ weight*weight # tf-idf square 
				#update_infos(docID,reduced_word,tf)

			dictionary[reduced_word] = (dictionary[reduced_word], offset) # Update the dictionary
			outfile_post.write(next_line)
			offset += len(next_line)

		offset = 0
		sorted_bi_grams = bi_dictionary.keys()
		sorted_bi_grams.sort()

		next_line = ""
		for index, term_doc in enumerate(sorted_bi_grams):
			t1 = term_doc[0]
			docID = term_doc[1]
			for t2 in bi_dictionary[(t1,docID)]:
				next_line += node_with_hash(docID,t2) 
			if index == (len(sorted_bi_grams)-1) or t1 != sorted_bi_grams[index+1][0]:
				dictionary[t1] = (dictionary[t1][0], dictionary[t1][1], offset)
				next_line += '\n'
				outfile_bi_post.write(next_line)
				offset += len(next_line)
				next_line = ""

		#pickle.dump(dictionary,outfile_dict)
		# Final length is obtained after computing the square root of the previous value
		#pickle.dump({docID: math.sqrt(score_acc) for docID, score_acc in length.items()}, outfile_dict) 
		
		
		#save the dictionnary and lenghts
		block_dictionnaries.append(dictionary)
		block_posts_files.append(postName)
		block_bi_posts_files.append(bi_post_name)


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

		docID = int(report[0]) # Extract docID
		doc_infos[docID] = [0,report[4],[]]
		
		#print("Report being processed: " + str(docID))
		title = report[1].decode('UTF8').encode('ASCII', "ignore")  # Extract content, encode to ASCII
		content = report[2].decode('UTF8').encode('ASCII',"ignore") # Extract content, encode to ASCII
		date =  report[3].decode('UTF8').encode('ASCII',"ignore") # Extract content, encode to ASCII
		court = report[4].decode('UTF8').encode('ASCII',"ignore") # Extract content, encode to ASCII
		
		uni_words=[]
		#tokens = nltk.word_tokenize(content)
		content = title + " " + content + " " + date + " " + court

		#spans = nltk.tokenize.WhitespaceTokenizer().span_tokenize(content)
		# Yield the relevant slice of the input string representing each individual token in the sequence
		#tokens = [content[begin: end] for (begin, end) in spans]

		tokenizer = RegexpTokenizer(r'\w+')
		uni_words = tokenizer.tokenize(content)
		uni_words = [stem_and_casefold(term) for term in uni_words]
		
		# TODO: explain
		bi_words = zip(uni_words,uni_words[1:])
		for t1,t2 in bi_words:
			if t1 < t2:
				bi_dictionary.setdefault((t1,docID),set())
				bi_dictionary[(t1,docID)].add(t2)
			else:
				bi_dictionary.setdefault((t2,docID),set())
				bi_dictionary[(t2,docID)].add(t1)

		
		for word_idx, reduced_word in enumerate(uni_words):
			dictionary.setdefault(reduced_word,0)
			term_frequency = 1
			

			if dictionary[reduced_word] == 0: # First occurence of reduced_word 
				new_line = new_node(docID) + '\n' 

				# Append this newly created posting list to posting-list-file
				uni_wnbr[reduced_word] = uni_size
				uni_postings.append(new_line)
				uni_size += 1

				dictionary[reduced_word] += 1 # doc_frequency updated 
			else: # reduced_word already in index
				line_number = uni_wnbr[reduced_word] 
				line = uni_postings[line_number]
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

				uni_postings[line_number] = new_line

		
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
			bi_dictionary = {}
			uni_wnbr = BidirectionalDict()

			uni_size = 0

			uni_postings = []
			print time.time() -t
			st = time.time()


if rep_nbr% DOCS_PER_BLOCK != DOCS_PER_BLOCK -1 :
	block_size +=1
	block_number = rep_nbr/ DOCS_PER_BLOCK
	print "WRITE BLOCK "+str(block_number)
	write_block(block_number)
	
	uni_wnbr = BidirectionalDict()
	uni_size = 0

	uni_postings = None

print "\nINDEXING TIME"
print (time.time() -s)
#============================= Merge blocks in one file (Part2)=======================#
print "\nSTART MERGING"

#FIXME--DELETE
print "INITIALIZATION"
start = time.time()


dictionary = {}
post_files = []
bi_post_files = []

# open files
for postName in block_posts_files:
	post_files.append(open(postName,'r'))

for bi_post_name in block_bi_posts_files:
	bi_post_files.append(open(bi_post_name,'r'))

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
with open(output_file_postings,"w") as mergedPost, open("tmp_bi_post", 'r+') as merged_bi_post:
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
		
		#if df > TOO_COMMON_DF add term to stop_words
		if df>=TOO_COMMON_DF:
			print termMin
			stopWords.add(termMin)
		
		#write all post in mergedPost
		final_posting = ""
		final_bi_posting = ""
		for idx in min_ids:
			#read postList
			posting_list = post_files[idx].readline()
			
			if posting_list[-1] == "\n":
				posting_list = posting_list[:-1]
			
			final_posting+= posting_list

			if len(block_dictionnaries[idx][termMin]) == 3:
				bi_posting_list = bi_post_files[idx].readline()

				if bi_posting_list[-1] == "\n":
					bi_posting_list = bi_posting_list[:-1]
			
				final_bi_posting+= bi_posting_list

			#update used term
			index_block[idx] += 1
			
		#write in final file
		mergedPost.write(final_posting+"\n")
		if len(final_bi_posting) > 0:
			uni_wnbr[termMin] = uni_size
			uni_size += 1
			merged_bi_post.write(final_bi_posting+'\n')

	# TODO: explain
	merged_bi_post.seek(0)
	for index, line in enumerate(merged_bi_post):
		term = uni_wnbr[index]
		dictionary[term] = (dictionary[term][0],dictionary[term][1],mergedPost.tell())
		mergedPost.write(line)


#FIXME--DELETE
print "\nMERGE TIME"
print time.time()-start


#close files
for f in post_files:
	f.close()
for bi_f in bi_post_files:
	bi_f.close()
for fname in block_posts_files:
	os.remove(fname)
for bi_fname in block_bi_posts_files:
	os.remove(bi_fname)
os.remove("tmp_bi_post")
#======= Create a vector with the most commons words for each documents===============#
print "CREATE VECTORS TIME"
temp = time.time()

with open(output_file_postings,"r") as mergedPost:
	for term in dictionary:
		offset = dictionary[term][1]
		mergedPost.seek(offset)
		posting_list = Postings(mergedPost.readline())
		for pair in posting_list:
			docid = get_docID(pair)
			tf = get_tf(pair)
			update_infos(docid,term,tf)



print time.time() -temp
#============================= Write Dictionnary file ================================#
print "WRITE DICO TIME"
temp = time.time()

with open(output_file_dictionary,"w") as outfile_dict:
	pickle.dump(dictionary,outfile_dict)
	# Final length is obtained after computing the square root of the previous value
	#FIXME
	pickle.dump({docID: (math.sqrt(info[0]),info[1],info[2]) for docID, info in doc_infos.items()}, outfile_dict) 

print time.time()-temp
print "COMPLETE"
print "Total TIME"
print time.time()-s
