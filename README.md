# addend
 This 'addend.py' code is a python utility intended for the BLIND folks.

For Visual Impaired (VI) folks it is NOT easy to listen to and
 explore large python code files where the number of indent spaces
 on each line of code has a syntactical meaning for python interpreters.

 'addend.py' adds #comments, like '# :end: if', for easier sound recognition
 when a syntax block structure has ended as defined by python's space
 indentation rules. Those added '# :end:' comment lines, placed whenever
 a syntax block has ended, hopefully it provides guidance for VI folks
 while they simultaneously deciphering python code and intently listening
 to unfamiliar python code with their favorite reader like JAWS or NVDA.

 Requirement:     'black' a python syntax checker
 to install use:  'pip install black'

 Place 'addend.py' into your working directory and run from command line:

% python addend.py -h 

usage: addend.py [-h] [-r] [-d] [-v] [inFilename] [outFilename]

positional arguments:
  inFilename     process input inFilename.py to add '# :end:' lines based on python indent rules.
  outFilename    specify optional outFilename.py ; DEFAULT is inFilename is replaced.

optional arguments:
  -h, --help     show this help message and exit
  -r, --remove   ONLY remove ALL '# :end:' comment lines from input filename.
  -d, --debug    print debugging lines.
  -v, --version  print version number.

    Default output is 'inFilename.py' with '# :end:' comments added.
    Unchanged input file is SAVED as 'inFilename.MMDD-hhmmss.py'

 NOTE: all prior added "# :end:" comment lines are removed
 during the next addend.py run and are re-added accordingly.


  To define your own string for the BLOCK-End-Comment
  change the variable 'endLabel' in the code from:
  
    endLabel = "# :end:"  (requires leading "# ")

    to for examples:   
        endLabel = "# :}:"
        endLabel = "# @end"
        endLabel = "# }"

  The inserted Block-End-Comment line will read like this:
  
  >> # :end: class <name>
  >> # :end: def <name>
  >> # :end: if
  >> # :end: for
  >> # :end: while

 Deleted:
  all prior added comment lines starting with #endLabel
  will be deleted on any next run.

 Process flow:
 [1] read input.py and drop any prior #endLabel lines and write newinput.py
 [2] run "black" syntax checker on newinput.py
 [3] in case of any "black" errors processing stops.
 [4] read newinput.py file into line_array

 [5] create indent_type_array to classify lines by defining
   (a) indentLevel, (b) syntaxType: class, def, ..., (c) blockStarter 0/1
   
   syntaxType is [ 'code', 'MLC', 'cont' ]
        blockStarts are [ 'class name', 'def name', if, for, while ]
        statement syntax [ return, continue, break, pass, ...]
        no statement syntax [ #, blank, empty ]
        MLC is for multi line comments
   
 [6] loop over array of all python code lines
 
     a BLOCK-end-marker (like "# :end: <syntaxType name>") line is added:

     When
       current statement line has a currentIndentLevel
       less or equal to savedIndentLevel
     Then
       scan indent_type_array backwards starting from current (line - 1)
          to get to all prior indentvalues (blockstarter) with same or bigger currentIndentLevel

          retrieve the blockstarter's syntaxType + indent to close block;
                scan backwards from the current line 
                to find 1st line of simple CODE to add '# :end:' comment(s)

                  foreach prior blockstarter
                    join that code line with '# :end:" comment line like:
                    "\n (space * savedIndentLevel) + #endLabel + syntaxType"

     set savedIndentLevelValue from currentIndentLevelValue

 [7] write lines_array to temp_file.py
 [8] run syntax checker 'black' on temp_file.py
 [9] rename input.py to input.MMDD_hhmmss.py
 [10] rename temp_file.py to infile.py

 done.
 
