import cmd
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
        if tag not in db[id].keys() or db[id][tag] == "":
            db[id][tag] = value
        else:
            if isinstance(db[id][tag], list):
                db[id][tag] += [value]
            else:
                db[id][tag] = [db[id][tag]] + [value]


def parse(gedcomFile):
    zeroLevelId = ""
    prevTag = ""
    for line in gedcomFile:
        fileLines = line.split()
        level = int(fileLines[0])
        tag = fileLines[1]
        valid = "N"
        arguments = " ".join(fileLines[2:])

        if fileLines[1] == "NOTE":
            continue
        if "INDI" in fileLines or "FAM" in fileLines:
            if level == 0 and (fileLines[2] == "INDI" or fileLines[2] == "FAM"):
                zeroLevelId = fileLines[1]
                valid = "Y"
                tag = fileLines[2]
                arguments = fileLines[1]
                if fileLines[2] == "INDI":
                    individualList[arguments] = {}
                    isIndi = True
                else:
                    treeList[arguments] = {}
                    isIndi = False
        elif fileLines[1] in supportedTags.keys() and level in supportedTags.values():
            if fileLines[1] == "DATE":
                addTag(isIndi, zeroLevelId, prevTag, arguments)
            else:
                addTag(isIndi, zeroLevelId, fileLines[1], arguments)
            if supportedTags[fileLines[1]] == level:
                valid = "Y"

        prevTag = tag
    return treeList, individualList




# # if __name__ == "__main__":
#     with open(sys.argv[1], "r") as file:
#         gedcomFile = file.readlines()
#     parse(gedcomFile)
#     printTree()
#
# # for testing within IDE
# with open("familyTree.ged", "r") as file:
#     gedcomFile = file.readlines()
# parse(gedcomFile)
# printTree()
# treeChecker
