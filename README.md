# addend
 This `'addend.py'` code is a python utility intended for the `BLIND` folks.

 For Visual Impaired (VI) folks it is NOT easy to listen to and
 explore large python code files where the number of indent spaces
 on each line of code has a syntactical meaning for python interpreters.

 'addend' adds #comments, like '`# :end: if`','`# :end: for`' etc, for easier 
 sound recognition when a syntax block structure has ended as defined by python's space
 indentation rules. Those added '`# :end:`' comment lines are placed whenever
 a syntax block has ended.  Hopefully, these #comments provides guidance for VI folks
 while they simultaneously decipher python code and intently listen
 to unfamiliar python code with their favorite reader like JAWS or NVDA.

 Python started in 1991 and is now a popular programming language because of
 its syntax simplicity and success in Data Science & ML Projects. 
 With the advent of python-based LLMs the use of python has increased 
 dramatically leaving blind programmers at a disadvantage in that field.
 Python is an "offside" language depending solely on the different space
 indentation to close syntax blocks. This makes it difficult for
 blind folks to study unfamiliar python code and to listen at the 
 same time to readers like JAWS or NVDA.
 
 Below highlights the blind's dilemma - advice given by a python 
 developer to folks working in python:

 "Generally, if you're used to curly braces {} language, 
  just indent the code like them and you'll be fine." 

  <b>should be expanded to ==></b> "except when you are blind and depend on a reader".

 Blind folks are disadvantaged in today's fast past AI work environments when it comes to using python.

 'addend' is hopefully a simple step to make it easier for the
 VI folks to use JAWS or NVDA readers and work on 
 large & unfamiliar python files. 

 The basics for working with 'addend':
<pre><code>
 [1] use it in conjunction with VScode:
   ==>  'code my_large.py'       launch python file in VScode
   ==>  'addend my_large.py'     run in cmd/terminal window
      a backup 'my_large.MMDD.hhmmss.py' is automatically created
      and VScode updates showing '# :end:' comments.

 [2] use it to keep original file untouched, use new file that is generated:
   ==> 'addend my_large.py new_large.py'
      'code new_large.py' VScode shows the added '# :end:' comments.

 [3] to remove any added '# :end:' comments use:
   ==> 'addend -r new_large.py'       (output to same file)
   ==> 'addend -r new_large.py final_large.py'    (output to different file)
   ==> 'addend -r -d new_large.py'    (also lists all ignored lines)

 
 Python version: >=3.7 installation is required.

 Other requirement:     'black' a python syntax checker
    to install use:     'pip install black'

 To install 'addend' on MacOS or Windows platform use:

   'pip install addend'

 Run 'addend' from command line without leading 'python' or '.py' :

 % 'addend --help' 

 usage: addend [-h] [-r] [-d] [-v] [inFilename] [outFilename]

 positional arguments:
  inFilename     process input inFilename.py to add '# :end:' lines based on python indent rules.
  outFilename    specify optional outFilename.py ; DEFAULT is inFilename.py is replaced.

 optional arguments:
  -h, --help     show this help message and exit
  -r, --remove   ONLY remove ALL '# :end:' comment lines from input filename.
  -d, --debug    print debugging lines.
  -v, --version  print version number.

    Default output is 'inFilename.py' with '# :end:' comments added.
    Unchanged input file is SAVED as 'inFilename.MMDD-hhmmss.py'

 NOTE: all prior added "# :end:" comment lines are removed
 during the next addend run and are re-added accordingly.
</code>
</pre>
 
