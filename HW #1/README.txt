This is the README file for A0174723A's submission

== Python Version ==

I'm using Python Version <2.7.12> for
this assignment.

== General Notes about this assignment ==

Give an overview of your program, describe the important algorithms/steps 
in your program, and discuss your experiments in general.  A few paragraphs 
are usually sufficient.

1. build_LM(in_file)
Builds a language model from a given file, that is creates a mapping (language,4-gram)->probability. Every line of the in_file needs to have the same format "label string", where label is a language contained in a list of languages (this list was defined and can be extended), and string is a text whose language is label. In order to compute the mapping (language,4-gram)->probability for given language and 4-gram, the entire in_file is scanned, and the algorithm counts the number of occurences of this specific 4-gram in lines that have language as their label. Then this number is divided by the total amount of 4-grams (not necessarily distinct) in lines that have language as their label. 

Remark: I chose not to pad the beginning and the end of a string


2. test_LM(in_file, out_file, LM)
Lines in in_file are of the form "string", and lines in out_file add a label (language) to this string: "label string". This label is determined using the language model LM, string is decomposed in its collection of 4-grams ('Hello World' -> ('Hell', 'ello', 'llo ', ...)). We want to compute the probability that this collection corresponds to a certain language l, assuming independence this is the product of the individual probabilities prob(l,4-gram) = LM((l,4-gram)). To avoid underflow we make use of log, hence the product of the probabilites becomes as sum, and we add 0 if the 4-gram is not in the language model. We assign this probability to l. The l with the highest probability is then the label. 


== Files included with this submission ==

List the files in your submission here and provide a short 1 line
description of each file.  Make sure your submission's files are named
and formatted correctly.

1. build_test_LM.py
2. README.txt

== Statement of individual work ==

Please initial one of the following statements.

[X] I, A0174723A, certify that I have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I
expressly vow that I have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[ ] I, A0000000X, did not follow the class rules regarding homework
assignment, because of the following reason:

<Please fill in>

I suggest that I should be graded as follows: Full mark

<Please fill in>

== References ==

<Please list any websites and/or people you consulted with for this
assignment and state their role>

python_tutorial.pdf
