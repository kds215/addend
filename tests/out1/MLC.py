# python uses 4 spaces to indent; normal tab is 8 spaces
def getIndentCount(string):
    count = 0

    if string:
        newStrings = re.split(r"\S", string)

        for i in newStrings[0]:
            if i == " ":
                count += 1
                continue

            if i == "\t":
                raise Exception(
                    "...python trouble when indentation mixes tabs & spaces..."
                )

    return count


# multiple lines processing to identify multi line comments
def testMLComment(data, type, index):
    # toggle to track start+end multi lines
    isMLC_lines = False
    isLastMLC_line = False

    while not isLastMLC_line:
        lineHasMLC = MLC_regex.search(data[index])

        # not a multi line """ comment section
        if not isMLC_lines and not lineHasMLC:
            return index

        # beginning of """ comment section
        if not isMLC_lines and lineHasMLC:
            isMLC_lines = True
            # type line [ indent=0, type cache[1]="MLC", 0=not a blockStarter ]
            type[index] = [0, isMLC, noBLOCK]
            if debug:
                print("*start* MLC")
                print(f"index:{index}  data: {data[index]}")
            # read next line
            index += 1
            continue

        # continued """ comment section
        if isMLC_lines and not lineHasMLC:
            type[index] = [0, isMLC, noBLOCK]
            if debug:
                print("continue MLC")
                print(f"index:{index}  data: {data[index]}")
            index += 1
            continue

        # end of """ comment section
        if isMLC_lines and lineHasMLC:
            # lastLine stops while loop
            isLastMLC_line = True
            type[index] = [0, isMLC, noBLOCK]
            if debug:
                print("*end* MLC")
                print(f"index:{index}  data: {data[index]}")
            index += 1
            continue

    return index


def load_input(filename):
    # run black syntax checker on input python file just to be sure...

    if isPlatform == "Windows":
        success_code = subprocess.call(["black", "--quiet", filename], shell=True)
    else:
        success_code = subprocess.call(["black", "--quiet", filename])

    if success_code != 0:
        print(
            f"\n\n...pre-processing syntax checker: 'black --quiet {filename}' failed code: '{success_code}'\n\n"
        )
        exit()

    # load input file and drop all #endLabel comments
    with open(filename, "r") as f:
        data_without_endLabels = []

        for line in f:
            # ignore all lines starting with #:end:
            if endLabel_regex.search(line):
                if debug:
                    print("ignoring: ", line[0:-1])  # drop \n
            else:
                data_without_endLabels.append(line)

    return data_without_endLabels


def write_output(filename, data_EBS):
    # write output file containing #endLabel comments
    with open(filename, "w") as f:
        for line in data_EBS:
            f.write(line)
