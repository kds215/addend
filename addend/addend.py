#!/usr/bin/env python
# coding: utf-8

# Name: addend.py  KDS 11/22/2023

isVersion = "1.15"  

# KDS added :end: block for try:, except: & finally: statements

"""
isVersion = "1.14"  # KDS 11/20/23 changes for pip deployment on windows and MacOS
isVersion = "1.12"  # KDS 11/19/23 switched to addend; no more 'python addend.py'
isVersion = "1.11"  # KDS 11/18/23 changed to optional different output filename
                    # i.e. [-h] [-r] [-d] [-v] [inFilename] [outFilename]
isVersion = "1.10"  # KDS 11/17/23 fixed raw syntax re.split(r"\\S", string)
isVersion = "1.09"  # KDS 11/17/23 test for posix-style path for windows;
                    # use subprocess(['black,...], shell=True)
isVersion = "1.08"  # KDS 11/16/23 removed the [ "-n" noblanklines ] option
isVersion = "1.07"  # KDS 11/15/23 initial BETA release

Info: (for more see README.md)

 This 'addend' is a python code utility intended for the BLIND folks.

 For Visual Impaired (VI) folks it is NOT easy to listen to and
 explore large python code files where the number of indent spaces
 on each line of code has a syntactical meaning for python interpreters.

 'addend' adds #comments, like '# :end: if', for easier sound recognition
 when a syntax block structure has ended as defined by python's space
 indentation rules. Those added '# :end:' comment lines, placed whenever
 a syntax block has ended, hopefully it provides guidance for VI folks
 while they simultaneously deciphering python code and intently listening
 to unfamiliar python code with their favorite reader like JAWS or NVDA.

 Requirement:     'black' a python syntax checker
 to install use:  'pip install black'

 To install 'addend' on MacOS or Windows platform use:

   'pip install addend'

Run 'addend' from command line without leading 'python' and '.py' :

% addend -h 

usage: addend [-h] [-r] [-d] [-v] [inFilename] [outFilename]

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
 
"""

import os
import platform
import subprocess
import re
import datetime
import argparse

# define variables

if platform.system() == "Windows":
    isPlatform = "Windows"
# :end: if
else:
    isPlatform = "Unix"
# :end: else:

# line index
imax = 0

# identifies python indent-based syntax block starter
noBLOCK = 0  # not a syntax block starter
startsBLOCK = 1  # starts syntax block

# python line type classifiers
isCODE = 0  # is of type general python code syntax
isMLC = 1  # is multi line comments
isCONT = 2  # is arguments over multi lines
isBLANK = 3  # is blank/empty/spaces line
isCOMM = 4  # is #comment

# '-d or --debug' mode to activate print() feedback
debug = False

# '-r or --remove' ONLY '# :end:' comment lines
removeAllEndLinesOnly = False

# required input file
inFilename = ""
# backup file of input file
backupFilename = ""
# optional output file
outFilename = ""

#### change to '# }' if a shorter reader sound is preferred
endLabel = "# :end:"

#### define & compile Regular Expressions in use

# 'endLabel'
endLabel_regex = re.compile(r"^\s*" + endLabel)

# # any comment line
comment_regex = re.compile(r"^\s*#")

# any blank line with spaces or tabs
blank_regex = re.compile(r"^\s*$")

# any continued standalone ) or ): closing argument line
cont_regex = re.compile(r"^\s*\):*$")

# class <name>
class_regex = re.compile(r"^\s*class (\w+)(\(|:)")

# def <name>
def_regex = re.compile(r"^\s*def (\w+)(\(|:)")

# if
if_regex = re.compile(r"^\s*if ")

# else:
else_regex = re.compile(r"^\s*else:")

# elif
elif_regex = re.compile(r"^\s*elif ")

# for
for_regex = re.compile(r"^\s*for ")

# while
while_regex = re.compile(r"^\s*while ")

# with
with_regex = re.compile(r"^\s*with ")

# try
try_regex = re.compile(r"^\s*try:")

# except
except_regex = re.compile(r"^\s*except.*:")

# finally
finally_regex = re.compile(r"^\s*finally:")

# import
import_regex = re.compile(r"^\s*import ")

# from
from_regex = re.compile(r"^\s*from ")

# multi line comment checks anywhere in the line for "\"" or '''
MLC_regex = re.compile(r'^.*("""|\'\'\').*')

# def section starts here


# python uses 4 spaces to indent; normal tab is 8 spaces
def getIndentCount(string):
    count = 0

    if string:
        newStrings = re.split(r"\S", string)

        for i in newStrings[0]:
            if i == " ":
                count += 1
                continue
            # :end: if

            if i == "\t":
                raise Exception(
                    "...python trouble when indentation mixes tabs & spaces..."
                )
            # :end: if
        # :end: for
    # :end: if

    return count


# :end: def getIndentCount


# multiple lines processing to identify multi line comments
def testMLComment(data, type, index):
    # toggle to track start+end multi lines
    isMLC_lines = False
    isLastMLC_line = False

    while not isLastMLC_line:
        lineHasMLC = MLC_regex.search(data[index])

        # not a multi line comment section
        if not isMLC_lines and not lineHasMLC:
            return index
        # :end: if

        # beginning of MLC comment section
        if not isMLC_lines and lineHasMLC:
            isMLC_lines = True
            # type line [ indent=0, type cache[1]="MLC", 0=not a blockStarter ]
            type[index] = [0, isMLC, noBLOCK]
            if debug:
                print("*start* MLC")
                print(f"index:{index}  data: {data[index]}")
            # :end: if
            # read next line
            index += 1
            continue
        # :end: if

        # continued MLC comment section
        if isMLC_lines and not lineHasMLC:
            type[index] = [0, isMLC, noBLOCK]
            if debug:
                print("continue MLC")
                print(f"index:{index}  data: {data[index]}")
            # :end: if
            index += 1
            continue
        # :end: if

        # end of MLC comment section
        if isMLC_lines and lineHasMLC:
            # lastLine stops while loop
            isLastMLC_line = True
            type[index] = [0, isMLC, noBLOCK]
            if debug:
                print("*end* MLC")
                print(f"index:{index}  data: {data[index]}")
            # :end: if
            index += 1
            continue
        # :end: if
    # :end: while

    return index


# :end: def testMLComment


def load_input(filename):
    # run black syntax checker on input python file just to be sure...

    if isPlatform == "Windows":
        success_code = subprocess.call(["black", "--quiet", filename], shell=True)
    # :end: if
    else:
        success_code = subprocess.call(["black", "--quiet", filename])
    # :end: else:

    if success_code != 0:
        print(
            f"\n\n...pre-processing syntax checker: 'black --quiet {filename}' failed code: '{success_code}'\n\n"
        )
        exit()
    # :end: if

    # load input file and drop all #endLabel comments
    with open(filename, "r") as f:
        data_without_endLabels = []

        for line in f:
            # ignore all lines starting with #:end:
            if endLabel_regex.search(line):
                if debug:
                    print("ignoring: ", line[0:-1])  # drop \n
                # :end: if
            # :end: if
            else:
                data_without_endLabels.append(line)
            # :end: else:
        # :end: for
    # :end: with

    # add temp last line for proper '# :end:' closing
    data_without_endLabels.append("#!!end: ")

    return data_without_endLabels


# :end: def load_input


def write_output(filename, data_EBS):

    # remove temp last line that enforced proper :end: closing
    data_EBS.pop() 

    # write output file containing #endLabel comments
    with open(filename, "w") as f:
        for line in data_EBS:
            f.write(line)
        # :end: for
    # :end: with


# :end: def write_output


#  update type array with indentLevel and index-to-cached-syntax and blockStarter
def upd_indent(keyword, is_regex, data, type, index, cache, identLevel, startsBlock):
    if debug:
        print(f"**upd_indent(): identLevel: {identLevel} keyword: {keyword}")
        print(f"data[{index}]: {data[index]}")
    # :end: if

    classDefName = ""

    match = is_regex.search(data[index])

    if match:
        len_groups = len(match.groups())

        if len_groups > 0:
            classDefName = " " + match.group(1)
        # :end: if

        keywordName = keyword + classDefName

        # to ignore duplicates
        seen = set(cache)
        if keywordName not in seen:
            cache.append(keywordName)
        # :end: if

        isIndex_Cache = cache.index(keywordName)

        type[index] = [identLevel, isIndex_Cache, startsBlock]

        if debug:
            print(f"keyword: {keyword}")
            print(f"type[{index}] = {type[index]}")
        # :end: if
    # :end: if

    return match, index


# :end: def upd_indent


# creates type array classifying python code lines
def classify_lines(data):
    # type[line#] = [ #indentLevel, pysyntax, isblockStarter ]

    # cache for code syntax + name like 'def name' or 'class name'
    cache = []
    cache.append("code")  # [isCODE] code line
    cache.append("MLC")  # [isMLC] multi line comment line
    cache.append("cont")  # [isCONT] for args over multiple lines
    cache.append("blank")  # [isBLANK] for space/empty lines
    cache.append("#")  # [isCOMM] for #comments

    type = []
    for i in range(imax):
        # initialize type array to 0 indent plus every line is blank and is no block starter
        # [indentLevel, index to cache, no block starter]
        type.append([0, isBLANK, noBLOCK])
    # :end: for

    # loop over python data lines
    index = -1

    while index < imax:
        # index can change in some functions to skip lines like in MLC
        index += 1

        # check for over index over runs
        if index >= imax:
            if debug:
                print(f"line index {index} >= imax {imax}")
            # :end: if

            break
        # :end: if

        # skips all MLC lines start->end by changing index
        index = testMLComment(data, type, index)
        if index >= imax:
            break
        # :end: if

        # first ignore empty lines
        if data[index] == None:
            type[index] = [0, isBLANK, noBLOCK]
            continue
        # :end: if

        identLevel = getIndentCount(data[index])

        # 2nd get #comments and blank lines out of the way
        isBlank, index = upd_indent(
            "blank", blank_regex, data, type, index, cache, identLevel, noBLOCK
        )
        if isBlank:
            continue
        # :end: if

        # check for continuation lines in case of multi line argument passing
        isCont, index = upd_indent(
            "cont", cont_regex, data, type, index, cache, identLevel, noBLOCK
        )
        if isCont:
            continue
        # :end: if

        # process #comment lines before MLC start->end
        isComment, index = upd_indent(
            "#", comment_regex, data, type, index, cache, identLevel, noBLOCK
        )
        if isComment:
            continue
        # :end: if

        isImport, index = upd_indent(
            "import", import_regex, data, type, index, cache, identLevel, noBLOCK
        )
        if isImport:
            continue
        # :end: if

        isFrom, index = upd_indent(
            "from", from_regex, data, type, index, cache, identLevel, noBLOCK
        )
        if isFrom:
            continue
        # :end: if

        isClass, index = upd_indent(
            "class", class_regex, data, type, index, cache, identLevel, startsBLOCK
        )
        if isClass:
            continue
        # :end: if

        isDef, index = upd_indent(
            "def", def_regex, data, type, index, cache, identLevel, startsBLOCK
        )
        if isDef:
            continue
        # :end: if

        isIf, index = upd_indent(
            "if", if_regex, data, type, index, cache, identLevel, startsBLOCK
        )
        if isIf:
            continue
        # :end: if

        isElse, index = upd_indent(
            "else:", else_regex, data, type, index, cache, identLevel, startsBLOCK
        )
        if isElse:
            continue
        # :end: if

        isElif, index = upd_indent(
            "elif", elif_regex, data, type, index, cache, identLevel, startsBLOCK
        )
        if isElif:
            continue
        # :end: if

        isFor, index = upd_indent(
            "for", for_regex, data, type, index, cache, identLevel, startsBLOCK
        )
        if isFor:
            continue
        # :end: if

        isWhile, index = upd_indent(
            "while", while_regex, data, type, index, cache, identLevel, startsBLOCK
        )
        if isWhile:
            continue
        # :end: if

        isWith, index = upd_indent(
            "with", with_regex, data, type, index, cache, identLevel, startsBLOCK
        )
        if isWith:
            continue
        # :end: if

        isTry, index = upd_indent(
            "try", try_regex, data, type, index, cache, identLevel, startsBLOCK
        )
        if isTry:
            continue
        # :end: if

        isExcept, index = upd_indent(
            "except", except_regex, data, type, index, cache, identLevel, startsBLOCK
        )
        if isExcept:
            continue
        # :end: if

        isFinally, index = upd_indent(
            "finally", finally_regex, data, type, index, cache, identLevel, startsBLOCK
        )
        if isFinally:
            continue
        # :end: if


        # must be plain line of code
        type[index] = [identLevel, isCODE, noBLOCK]

        if debug:
            print(f"plain code: type[{index}] = [{identLevel}, ...]")
            print(f"LINE#[{index+1}]: {data[index]}")
        # :end: if
    # :end: while

    return type, data, cache


# :end: def classify_lines


def insert_End_comment(type, data, index, cache, currentIndentValue, indentStack):
    if debug:
        print(f"***def insert_End_comment: on some before LINE#: {index+1}")
        print(f"***indentStack: {indentStack}")
    # :end: if

    isSyntaxName = ""

    # check for end of stack
    if len(indentStack) > 1:
        sIndent, sLine, sBlockstarter = indentStack.pop()
        if debug:
            print(
                f"*1*popped from stack: sIndent={sIndent}, sLine#={sLine+1}, sBlockstarter={sBlockstarter}"
            )
        # :end: if

        if not sBlockstarter:
            return
        # :end: if
    # :end: if
    else:
        # empty stack ergo no blocks to close
        return
    # :end: else:

    # roll-up all BLOCKs with greater equal indent value
    while currentIndentValue <= sIndent:
        # get syntax like 'def abcd' or 'if' etc
        isSyntaxName = cache[type[sLine][1]]

        if isSyntaxName:
            if debug:
                print(f"isSyntaxName: {isSyntaxName}")
            # :end: if

            for k in range(-1, -index, -1):
                kcheck = index + k

                # limit check to top line
                if kcheck < 0:
                    if debug:
                        print(f"NO code line found to append :end: comment to")
                    # :end: if
                    break
                # :end: if

                if type[kcheck][1] == isCODE or type[kcheck][1] == isCONT:
                    if debug:
                        print(
                            f"found LINE#[{kcheck+1}] to append '# :end: {isSyntaxName}'"
                        )
                    # :end: if

                    indent_spaces = " " * type[sLine][0]  # IndentValue of blockstarter
                    data[kcheck] += indent_spaces + endLabel + " " + isSyntaxName + "\n"

                    if debug:
                        print(f"updated LINE#[{kcheck+1}]:")
                        print(data[kcheck])
                    # :end: if

                    break
                # :end: if
            # :end: for
        # :end: if

        # don't pop stack when stackindent < currentIndent
        if indentStack[-1][0] < currentIndentValue and indentStack[-1][2] == 1:
            break
        # :end: if

        # check for end of stack
        if len(indentStack) > 1:
            sIndent, sLine, sBlockstarter = indentStack.pop()
            if debug:
                print(
                    f"*2*popped from stack: sIndent={sIndent}, sLine#{sLine+1}, sBlockstarter={sBlockstarter}"
                )
            # :end: if
        # :end: if
        else:
            sIndent = -1
        # :end: else:
    # :end: while

    return


# :end: def insert_End_comment


# appends End_Block_Comments to only python code lines
def add_EndBlockComments(type, data, cache):
    if debug:
        print(f"  >>>>  def add_EndBlockComments:")
        print("type: ", type)
        print("data: ", data)
        print("cache:", cache)
    # :end: if

    # initialize indentation stack: [indentvalue<0, index<0, blockstarter=no]
    indentStack = []
    indentStack.append([-1, -1, noBLOCK])

    if debug:
        print("init indentStack: ", indentStack)
    # :end: if

    # process python file lines
    for index in range(imax):
        if debug:
            print(f">>>type[{index}]: {type[index]} data[{index}]: {data[index]}")
            # type[index][0]=indent, [1]=index_cached_name, [2]=blockstarter
            print(
                f">>>type[{index}]  [indent]: {type[index][0]} [cache]: {type[index][1]} [blockstarter]: {type[index][2]}"
            )
        # :end: if

        # skip all blank lines during indent processing
        if type[index][1] in [isMLC, isCONT, isBLANK, isCOMM]:
            if debug:
                print(f"skipping index: {index}  aka LINE: {index+1}")
            # :end: if
            continue
        # :end: if

        currentIndentValue = type[index][0]

        if debug:
            print(
                f"...currentIndentValue: {currentIndentValue} <= indentStack[-1][0]: {indentStack[-1][0]}"
            )
            print(f"...indentStack: {indentStack}")
        # :end: if

        # indent <= indent on stack
        while currentIndentValue <= indentStack[-1][0]:
            # appends #:end: comment at first prior code line
            insert_End_comment(
                type, data, index, cache, currentIndentValue, indentStack
            )
        # :end: while

        # push onto stack new indent,index,blockstarter
        # but skip when 0 indent and not a blockstarter
        # because there is no more "offsides" beyond indent 0
        if currentIndentValue == 0 and not type[index][2]:
            continue
        # :end: if

        indentStack.append([currentIndentValue, index, type[index][2]])

        if debug:
            print(f"indentStack: {indentStack}")
        # :end: if
    # :end: for

    # close possibly more lines to add '# :end:' comments at EOF reached
    while len(indentStack) > 1:
        currentIndentValue = indentStack[-1][0]

        insert_End_comment(
            type, data, (imax - 1), cache, currentIndentValue, indentStack
        )
    # :end: while

    return data


# :end: def add_EndBlockComments


def getBackupFilename(inputFilename):
    now = datetime.datetime.now()
    MMDD_hhmmss = now.strftime("%m%d_%H%M%S")
    timeName = "." + MMDD_hhmmss + ".py"
    backupFilename = re.sub(r".py$", timeName, inputFilename)

    return backupFilename


# :end: def getBackupFilename


##################################
#
# Main code section starts here...
#
def main():
    global isVersion
    global inFilename, backupFilename, outFilename
    global isPlatform, imax, noBLOCK, startsBLOCK
    global isCODE, isMLC, isCONT, isBLANK, isCOMM
    global endLabel, debug, removeAllEndLinesOnly
    global endLabel_regex, comment_regex, blank_regex, cont_regex
    global class_regex, def_regex, if_regex, else_regex
    global elif_regex, for_regex, while_regex, with_regex
    global import_regex, from_regex, MLC_regex
    global try_regex, except_regex, finally_regex

    # start processing python input file...
    #
    # this file will hold the python output lines with '# :end:' comments
    endfile = "end_file.py"

    # works only when running in command line python mode
    scriptname = os.path.basename(__file__)

    # parse input args...
    execname = re.sub(r".py$", "", scriptname)
    parser = argparse.ArgumentParser(prog=execname)

    parser.add_argument(
        "-r",
        "--remove",
        action="store_true",
        help="ONLY remove ALL '# :end:' comment lines from input filename.",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="print debugging lines.",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="store_true",
        help="print version number.",
    )
    parser.add_argument(
        "inFilename",
        type=str,
        nargs="?",
        help="process input inFilename.py to add '# :end:' lines based on python indent rules.",
    )
    parser.add_argument(
        "outFilename",
        type=str,
        nargs="?",
        help="specify optional outFilename.py ; DEFAULT is inFilename is replaced.",
    )

    args = parser.parse_args()

    if args.remove:
        removeAllEndLinesOnly = True
    # :end: if

    if args.debug:
        debug = True
    # :end: if

    if args.version:
        print(f"\n   >>> '{execname}' running version: {isVersion}\n")
        exit()
    # :end: if

    if args.outFilename:
        outFilename = args.outFilename
    # :end: if

    # required input
    if args.inFilename:
        inFilename = args.inFilename

        # in case Windows notepad has this file open...
        if not os.path.exists(inFilename):
            print(f"\n\n   >>> specified inFilename is missing: '{inFilename}'\n\n")
            exit()
        # :end: if
    # :end: if

    else:
        print("\n   >>> missing required input: 'inFilename.py' ; check --help ...\n")
        exit()
    # :end: else:

    if inFilename.lower().endswith(".py"):
        if outFilename:
            print(f"\nprocessing:")
            print(f"   >>>  input==> {inFilename}")
            print(f"   >>> output==> {outFilename}\n")
        # :end: if
        else:
            backupFilename = getBackupFilename(inFilename)
            print(f"\nprocessing:")
            print(f"   >>>  input==> {inFilename}")
            print(f"   >>> saveAs==> {backupFilename}")
            print(f"   >>> output==> {inFilename}\n")
        # :end: else:

        # Load the python file lines and remove old :end: lines too
        pydata = load_input(inFilename)
        imax = len(pydata)

        if removeAllEndLinesOnly:
            data_EBC = pydata
        # :end: if

        else:
            # all python line processing takes place here...
            #
            # classify lines by syntax type tags in parallel to the python code lines,
            #     i.e. type[line_index] = [ indent, cache_index to syntax_type_names, blockstarter=0/1 ]
            type, data, cache = classify_lines(pydata)

            # append '#:end:' at end_of_block code lines
            data_EBC = add_EndBlockComments(type, data, cache)
        # :end: else:

        # in case of NO (optional) output file was specified
        # rename input to backup filename.MMDD_hhmmss.
        if not outFilename:
            if os.path.exists(inFilename):
                os.rename(inFilename, backupFilename)
            # :end: if
            else:
                print(
                    f"\n   >>> file ERROR: '{execname}' is missing '{inFilename}' ; check --help \n"
                )
                exit()
            # :end: else:
        # :end: if

        # saving python code with added '# :end:' comment lines
        # OR no :end: if removeAllEndLinesOnly was true;
        # under Windows need to first delete existing file
        if os.path.exists(endfile):
            os.remove(endfile)
        # :end: if
        write_output(endfile, data_EBC)

        # run black syntax checker on new python file to be sure...
        if isPlatform == "Windows":
            success_code = subprocess.call(["black", "--quiet", endfile], shell=True)
        # :end: if
        else:
            success_code = subprocess.call(["black", "--quiet", endfile])
        # :end: else:

        if success_code != 0:
            print(
                f"\n   >>> post-processing syntax checker: 'black --quiet {endfile}' failed\n"
            )
            print(f"   >>> input file '{inFilename}' has NOT changed.")
            print(
                f"   >>> run 'black {endfile}' for possible reasons why 'black' syntax checker has failed.\n\n"
            )
        # :end: if

        # on 'black' success switching temp file into output file
        if os.path.exists(endfile):
            if outFilename:
                os.rename(endfile, outFilename)
            # :end: if
            else:
                os.rename(endfile, inFilename)
            # :end: else:
        # :end: if
        else:
            print(
                f"\n   >>> failed:  '{execname}' output file='{endfile}' does not exist. Unable to rename to '{inFilename}' \n"
            )
            print(
                f"\n   >>> check original input file: '{backupFilename}' for possible syntax conflicts. \n"
            )

            exit()
        # :end: else:

        if not outFilename:
            print(f"\n   done: original input file saved as '{backupFilename}'\n")
        # :end: if
    # :end: if

    else:
        print(
            f"\n   >>> syntax error expecting: '{execname} inFilename.py' ; check --help for details.\n"
        )
    # :end: else:

    exit()


# :end: def main


if __name__ == "__main__":
    main()
# :end: if


