supportedTags = {"INDI": 0, "NAME": 1, "SEX": 1, "BIRT": 1, "DEAT": 1, "FAMC": 1, "FAMS": 1, "FAM": 0, "MARR": 1,
                 "HUSB": 1, "WIFE": 1, "CHIL": 1, "DIV": 1, "DATE": 2, "HEAD": 0, "TRLR": 0, "NOTE": 0}

treeList = {}
individualList = {}


def addTag(isIndi, id, tag, value):
    if value is not "":
        if isIndi:
            db = individualList
        else:
            db = treeList
        if db[id][tag] == "NA" or db[id][tag] == "":
            db[id][tag] = value
        else:
            if not isinstance(db[id][tag], list):
                db[id][tag] = [db[id][tag], value]
            else:
                db[id][tag] += [value]


def parse(gedcomFile):
    zeroLevelId = ""
    prevTag = ""
    for line in gedcomFile:
        fileLines = line.split()
        level = int(fileLines[0])
        tag = fileLines[1]
        arguments = " ".join(fileLines[2:])

        if fileLines[1] == "NOTE":
            continue
        if "INDI" in fileLines or "FAM" in fileLines:
            if level == 0 and (fileLines[2] == "INDI" or fileLines[2] == "FAM"):
                zeroLevelId = fileLines[1]
                tag = fileLines[2]
                arguments = fileLines[1]
                if fileLines[2] == "INDI":
                    individualList[arguments] = {"NAME": "NA",
                                                 "SEX": "NA",
                                                 "BIRT": "NA",
                                                 "DEAT": "NA",
                                                 "FAMC": "NA",
                                                 "FAMS": "NA"}
                    isIndi = True
                else:
                    treeList[arguments] = {"MARR": "NA",
                                           "HUSB": "NA",
                                           "WIFE": "NA",
                                           "CHIL": "NA",
                                           "DIV": "NA"}
                    isIndi = False
        elif fileLines[1] in supportedTags.keys() and level in supportedTags.values():
            if fileLines[1] == "DATE":
                addTag(isIndi, zeroLevelId, prevTag, arguments)
            else:
                addTag(isIndi, zeroLevelId, fileLines[1], arguments)
        prevTag = tag
    return treeList, individualList
