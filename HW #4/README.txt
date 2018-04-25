This is the README file for A0174724B-A0174723A-A0174721H's submission
Emails: e0215426@u.nus.edu, e0215425@u.nus.edu and @u.nus.edu

== Python Version ==

We're using Python Version 2.7.12 for
this assignment.

== General Notes about this assignment ==

Creating the dictionary:
index.py creates an inverted index, a file of posting lists and a mapping length, from a collection of documents, the path to which is given by the user as input. To do so, the algorithm goes through 4 distinct steps:

	1) Create both the index and posting-list blocks. Every document is read, and for every word, after it was tokenized, stemmed and case-folded, we update the index (and the corresponding posting list) accordingly.
	For every 500 documents indexed (arbitrary number) we write the posting list into a block and we compute every documents length (using only the term frequency for terms in the document).
	
	2) Once the indexing is complete, we merge all block into one file. To do so, we simply sort all the terms in the dictionnary and for all the terms we fetch the postings list in each block containing the term. Then we concatenate the differents postings list into one posting list that we write into output_file_postings.

	3)Once the final posting list is created, we create an approximation of the vector for each document.
To do so, we only consider the 50 terms with the highest term freqency for each document. This vector will help us to apply rocchio algorithm in search.py.
	We wanted the vector to be the most specific to a document, so we excluded from the vector all the term contained in stopWords from the library nltk.corpus. But we also excluded the term with a document frequency higher than 5000, since it means that the term appear in more than 1/4 of the documents. It's not relevant to a particular document anymore, but the term is relevant to the entire dataset.

	4)Finally, we write the dictionnary, the lengths and the vectors into output_file_dictionary

Although left as a comment in the code, our search engine initially supported phrasal queries for boolean retrieval, that is queries that include phrases such as "A B" or "A B C", where A, B and C are words. In order to reduce overhead in the dictionary and the posting-list-file, phrases with more than 2 words are transformed as follows: "A B C ..." -> "A B" AND "B C" AND ... Moreover, phrases "A B" and "B A" are considered to be identical. For a word "A", the algorithm updates the entry dictionary["A"] by appending to the tuple a second offset, wich represents the offset in posting-list-file of the list of pairs (docID,hash32("Bi")), where "Bi" is a word such that "A" < "Bi" (string comparison), and "A Bi" appears in the document docID. We chose not to include this code because the corresponding "postings.txt" file, with its size of 1.3 Gb, was too big to be uploaded.

Query processing :
Our program is able to process free term queries. To do so, the algorithm goes through 5 distinct steps :

1)query expansion:
	The query is expanded by adding the synonyms of every terms but with a lower weight than the original terms of the query. Originals terms have a weight of 1+log(3) and synonyms a weight of 1.

2) term reduction 
  The terms in the query need to be reduced following the same reduction flow as used for the inverted index. In our case each term is stemmed and case-folded after tokenization.

3) rocchio algorithm:
	We apply rocchio algorithm on the query using the approximated vectors for each document.
We chose to select only the top 5 documents using cosine score to be relevants. The weights are 0.9 for Alpha and 0.1 for Beta, so the original query is still really important compare to the pseudo-relevants documents but after few tries we've seen that rocchio algorithm is more likely to scatter the result if Beta is too big.

4) cosine scores computation
  The cosine score for each document is computed following the algorithm given in class

5) Documents are sorted by cosine score

Again, the phrasal query code is left as a comment. Phrases with more than 2 words are transformed as follows: "A B C ..." -> "A B" AND "B C" AND ... with possible reordering such that for every bi-gram "Bi Bj" "Bi" < "Bj". If a phrase is detected, we transform it, and for each bi-gram we use the second offset in dictionary instead of the first one, e.g. for "Bi Bj": retrieve dictionary["Bi"], access the third attribute if present, seek to that offset in posting-list-file, and collect the docIDs of the nodes that have hash32("Bj") as their second attribute.

== Files included with this submission ==

List the files in your submission here and provide a short 1 line
description of each file.  Make sure your submission's files are named
and formatted correctly.

index.py
This file contains the core algorithm to generate dictionary.txt and postings.txt from a collection of documents

search.py
This file contains the core algorithm for query processing given a precomputed inverted index

tools.py
This file contains a variety of helper methods, used in both index.py and search.py

dictionary.txt
The inverted index, a mapping of the form (word: (doc. frequency, offset in postings.txt)) 

postings.txt
For every word in the dictionary, there is a corresponding posting list in this file


== Statement of individual work ==

Please initial one of the following statements.

[X] We, A0174724B-A0174723A-A0174721H, certify that we have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, we
expressly vow that we have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[ ] I, A0000000X, did not follow the class rules regarding homework
assignment, because of the following reason:

<Please fill in>

I suggest that I should be graded as follows: /

<Please fill in>

== References ==

<Please list any websites and/or people you consulted with for this
assignment and state their role>

- stackoverflow.com/questions/1063319/reversible-dictionary-for-python: Code for the bidirectional dictionary

- https://courses.csail.mit.edu/6.006/fall10/handouts/recitation10-8.pdf : Pseudo code for max-heap
    and https://en.wikipedia.org/wiki/Binary_heap : Pseudo code for max-heap

