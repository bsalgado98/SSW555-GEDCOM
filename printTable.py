from prettytable import PrettyTable
import datetime


def printTree(treeList, individualList):
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