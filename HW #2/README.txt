This is the README file for A0000000X's submission

== Python Version ==

I'm (We're) using Python Version <2.7.x or replace version number> for
this assignment.

== General Notes about this assignment ==

Give an overview of your program, describe the important algorithms/steps 
in your program, and discuss your experiments in general.  A few paragraphs 
are usually sufficient.

Query processing :
Our program is able to process boolean queries i.e. in-fix expressions made of search terms and boolean operators (AND, OR, NOT and parenthesis). To do so, the algorithm goes through X distinct steps :
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

search.py
This file contains the core algorithm for boolean query processing given a precomputed inverted index.

== Statement of individual work ==

Please initial one of the following statements.

[X] I, A0000000X, certify that I have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I
expressly vow that I have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[ ] I, A0000000X, did not follow the class rules regarding homework
assignment, because of the following reason:

<Please fill in>

I suggest that I should be graded as follows:

<Please fill in>

== References ==

<Please list any websites and/or people you consulted with for this
assignment and state their role>
