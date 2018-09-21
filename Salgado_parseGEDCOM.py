import datetime
import sys
from prettytable import PrettyTable
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


def printTree():
    indiTable = PrettyTable(["ID", "Name", "Gender", "Birthday", "Age", "Alive", "Death", "Child", "Spouse"])
    columns = ["NAME", "SEX", "BIRT", "DEAT", "FAMC", "FAMS"]
    for id, args in individualList.items():
        for col in columns:
            if col not in args.keys():
                args[col] = "NA"
        if args["BIRT"] is not "NA":
            birth = datetime.datetime.strptime(args["BIRT"], "%d %b %Y").date()
        else:
            birth = datetime.date(1, 1, 1)  # just to prevent errors
        if args["DEAT"] is not "NA":
            death = datetime.datetime.strptime(args["DEAT"], "%d %b %Y").date()
            age = death - birth
        else:
            age = datetime.date.today() - birth
        indiTable.add_row(
            [id, args["NAME"], args["SEX"], args["BIRT"], age.days // 365, args["DEAT"] == "NA", args["DEAT"],
             args["FAMC"], args["FAMS"]])

    famTable = PrettyTable(
        ["ID", "Married", "Divorced", "Husband ID", "Husband Name", "Wife ID", "Wife Name", "Children"])
    columns = ["MARR", "DIV", "HUSB", "WIFE", "CHIL"]
    for id, args in treeList.items():
        for col in columns:
            if col not in args.keys():
                args[col] = "NA"
        if args["HUSB"] is not "NA":
            husbName = individualList[args["HUSB"]]["NAME"]
        else:
            husbName = "NA"
        if args["WIFE"] is not "NA":
            wifeName = individualList[args["WIFE"]]["NAME"]
        else:
            wifeName = "NA"
        famTable.add_row([id, args["MARR"], args["DIV"], args["HUSB"], husbName, args["WIFE"], wifeName, args["CHIL"]])

    print("Individuals")
    print(indiTable.get_string(sortby="ID"))
    print("Families")
    print(famTable.get_string(sortby="ID"))

if __name__ == "__main__":
    with open(sys.argv[1], "r") as file:
        gedcomFile = file.readlines()
    parse(gedcomFile)
    printTree()

# for testing within IDE
# with open("familyTree.ged", "r") as file:
#     gedcomFile = file.readlines()
# parse(gedcomFile)
# printTree()
