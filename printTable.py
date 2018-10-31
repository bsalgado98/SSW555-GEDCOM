import datetime
import sqlite3
import operator

from prettytable import PrettyTable

from treeChecker import getValue
from webbrowser import Opera


def printTree(dbFile="gedcom.db"):
    c = sqlite3.connect(dbFile).cursor()

    indiTable = PrettyTable(["ID", "Name", "Gender", "Birthday", "Age", "Alive", "Death", "Child", "Spouse"])
    for indi in c.execute("SELECT DISTINCT ID FROM INDI").fetchall():
        indi = indi[0]
        birth = getValue(c, "INDI", indi, "BIRT")
        if birth is not None:
            birth = datetime.datetime.strptime(birth, "%d %b %Y").date()
        else:
            birth = datetime.date(1, 1, 1)  # just to prevent errors
        death = getValue(c, "INDI", indi, "DEAT")
        if death is not None:
            death = datetime.datetime.strptime(death, "%d %b %Y").date()
            age = death - birth
        else:
            age = datetime.date.today() - birth
        indiTable.add_row([indi,
                           getValue(c, "INDI", indi, "NAME"),
                           getValue(c, "INDI", indi, "SEX"),
                           birth,
                           age.days // 365,
                           death is None,
                           death,
                           getValue(c, "INDI", indi, "FAMC", fetchall=True),
                           getValue(c, "INDI", indi, "FAMS", fetchall=True)])

    famTable = PrettyTable(
        ["ID", "Married", "Divorced", "Husband ID", "Husband Name", "Wife ID", "Wife Name", "Children"])
    for fam in c.execute("SELECT DISTINCT ID FROM FAM").fetchall():
        fam = fam[0]
        husb = getValue(c, "FAM", fam, "HUSB")
        wife = getValue(c, "FAM", fam, "WIFE")
        famTable.add_row([fam,
                          getValue(c, "FAM", fam, "MARR"),
                          getValue(c, "FAM", fam, "DIV"),
                          husb,
                          getValue(c, "INDI", husb, "NAME"),
                          wife,
                          getValue(c, "INDI", wife, "NAME"),
                          getOrderedChildren(getValue(c, "FAM", fam, "CHIL", fetchall=True), c)])

    print("Individuals")
    print(indiTable.get_string(sortby="ID"))
    print("Families")
    print(famTable.get_string(sortby="ID"))


def getOrderedChildren(childArr, cursor):
    birthdays = []
    for child in childArr:
        for birthday in cursor.execute("SELECT VALUE FROM INDI WHERE TAG=\"BIRT\" AND ID=\"" + child + "\"").fetchall():
            birthdays.append((child, datetime.datetime.strptime(birthday[0], "%d %b %Y")))
    birthdays_sorted = sorted(birthdays, key=lambda x: x[1])
    children_sorted = []
    for entry in birthdays_sorted:
        children_sorted.append(entry[0])
    return children_sorted
