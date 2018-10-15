import sqlite3

supportedTags = {
    "0": ["INDI", "FAM", "HEAD", "TRLR", "NOTE"],
    "1": ["NAME", "SEX", "BIRT", "DEAT", "FAMC", "FAMS", "MARR", "HUSB", "WIFE", "CHIL", "DIV"],
    "2": ["DATE"]
}

treeList = {}
individualList = {}


def isSupported(line):
    tokens = line.split(" ")
    if tokens[0] in {"0", "1", "2"}:
        if tokens[0] == "2" and tokens[2] in {"INDI", "FAM"}:
            tokens[1], tokens[2] = tokens[2], tokens[1]
        if tokens[1] in supportedTags[tokens[0]]:
            return True
    raise ValueError("Tag " + tokens[1] + " not supported by level " + tokens[0])


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


def checkTables(cursor):
    tableInfo = cursor.execute("SELECT * FROM sqlite_master WHERE type='table'").fetchall()
    tablenames = []
    for table in tableInfo:
        tablenames += [table[1]]
    if "individuals" not in tablenames:
        cursor.execute(
            "CREATE TABLE individuals (ID TEXT, NAME TEXT, SEX TEXT, BIRT TEXT, DEAT TEXT, FAMC TEXT, FAMS TEXT)")
    if "families" not in tablenames:
        cursor.execute("CREATE TABLE families (ID TEXT, HUSB TEXT, WIFE TEXT, CHIL TEXT, DIV TEXT)")


def addEntries(prevLevel, prevTag, currLine, linesLeft):
    currLine = currLine.strip()
    if int(currLine[0]) < 0 or int(currLine[0]) > prevLevel + 1:
        raise SyntaxError("Invalid level: " + currLine[0] + ", previous level: " + prevLevel)


def parse(gedcomFile):
    database = sqlite3.connect("gedcom.db")
    cursor = database.cursor()

    checkTables(cursor)
    addEntries(-1, None, gedcomFile[0], gedcomFile[1:])
    # zeroLevelId = ""
    # prevTag = ""
    # for line in gedcomFile:
    #     fileLines = line.split()
    #     level = int(fileLines[0])
    #     tag = fileLines[1]
    #     arguments = " ".join(fileLines[2:])
    #
    #     if fileLines[1] == "NOTE":
    #         continue
    #     if "INDI" in fileLines or "FAM" in fileLines:
    #         if level == 0 and (fileLines[2] == "INDI" or fileLines[2] == "FAM"):
    #             zeroLevelId = fileLines[1]
    #             tag = fileLines[2]
    #             arguments = fileLines[1]
    #             if fileLines[2] == "INDI":
    #                 individualList[arguments] = {"NAME": "NA",
    #                                              "SEX": "NA",
    #                                              "BIRT": "NA",
    #                                              "DEAT": "NA",
    #                                              "FAMC": "NA",
    #                                              "FAMS": "NA"}
    #                 isIndi = True
    #             else:
    #                 treeList[arguments] = {"MARR": "NA",
    #                                        "HUSB": "NA",
    #                                        "WIFE": "NA",
    #                                        "CHIL": "NA",
    #                                        "DIV": "NA"}
    #                 isIndi = False
    #     elif fileLines[1] in supportedTags.keys() and level in supportedTags.values():
    #         if fileLines[1] == "DATE":
    #             addTag(isIndi, zeroLevelId, prevTag, arguments)
    #         else:
    #             addTag(isIndi, zeroLevelId, fileLines[1], arguments)
    #     prevTag = tag
    database.close()
    # return treeList, individualList


parse([])
