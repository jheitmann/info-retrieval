This is the README file for A0174724B-A0174723A's submission
Emails: e0215426@u.nus.edu and e0215425@u.nus.edu

== Python Version ==

We're using Python Version 2.7.12 for
this assignment.

== General Notes about this assignment ==

Give an overview of your program, describe the important algorithms/steps 
in your program, and discuss your experiments in general.  A few paragraphs 
are usually sufficient.

Creating the dictionary:
index.py creates an inverted index and a file of posting lists, from a collection of documents, the path to which is given by the user as input. To do so, the algorithm goes through 3 distinct steps:
1) Create a first version of both index and posting-list-file, without skip pointers. Every document is read, and for every word, after it was tokenized, stemmed and case-folded, we update the index (and the corresponding posting list) accordingly.
2) Add skip pointers to large enough posting lists. If a new skip pointer is created, here is how the posting list close to the node that has a skip pointer looks like:
Node (delimited by []) with flag set to 1 => NODES |[FLAG = 1 (1 char) | docID (8 chars)]| ptr (8 chars)| NODES, where NODES represents other nodes (possibly none at all)
3) Add the special word "CORPUS" to the index (and append its posting list), that allows us to retrieve the entire list of docIDs from the posting-list-file, then serialize the index, using the cPickle library.

Query processing :
Our program is able to process boolean queries i.e. in-fix expressions made of search terms and boolean operators (AND, OR, NOT and parenthesis). To do so, the algorithm goes through 4 distinct steps :
1) term reduction 
  The terms in the query need to be reduced following the same reduction flow as used for the inverted index. In our case each term is stemmed and case-folded.
2) post-fix translation
   the in-fix expression is parsed into a post-fix expression to simplify its evaluation. For example 'bill AND gates' is transformed to 'bill gates AND'. This is done using the Shunting-yard algorithm from our Lord Dijkstra.
3) postings list retrieval
  the postings list corresponding to each term in the expression are retrieved from the inverted index (dictionnary and postings-list files)
4) expression evaluation
  the expression can finally be evaluated using basic algorithms for the AND, OR and NOT operations between postings-list

== Files included with this submission ==

List the files in your submission here and provide a short 1 line
description of each file.  Make sure your submission's files are named
and formatted correctly.

index.py
This file contains the core algorithm to generate dictionary.txt and postings.txt from a collection of documents

search.py
This file contains the core algorithm for boolean query processing given a precomputed inverted index

tools.py
This file contains a variety of helper methods, used in both index.py and search.py

dictionary.txt
The inverted index, a mapping of the form (word: (doc. frequency, offset in postings.txt)) 

postings.txt
For every word in the dictionary, there is a corresponding posting list in this file


== Statement of individual work ==

Please initial one of the following statements.

[X] We, A0174724B-A0174723A, certify that I have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I
expressly vow that I have followed the Facebook rule in discussing
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

--> stackoverflow in general, for various issues with python

- https://en.wikipedia.org/wiki/Shunting-yard_algorithm: Shunting-yard algorithm

- https://en.wikipedia.org/wiki/Reverse_Polish_notation: Reverse Polish notation
