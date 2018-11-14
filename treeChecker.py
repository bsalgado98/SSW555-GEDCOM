import datetime
import sqlite3
from datetime import timedelta


def getValue(cursor, table, id, tag, fetchall=False):
    if table in {"INDI", "FAM"}:
        if not fetchall:
            valueTuple = cursor.execute("SELECT VALUE FROM {} WHERE ID=? AND TAG=?".format(table), (id, tag)).fetchone()
            if valueTuple is None:
                return None
            return valueTuple[0]
        else:
            return list(map(lambda x: x[0],
                            cursor.execute("SELECT VALUE FROM {} WHERE ID=? AND TAG=?".format(table), (id, tag))
                            .fetchall()))


def convertDates(treeList, individualList):
    """Coverts Dates in Individual and Tree Lists to Datetime Objects"""
    for key, value in individualList.items():
        if value["BIRT"] != "NA":
            value["BIRT"] = datetime.datetime.strptime(value["BIRT"], "%d %b %Y").date()
        if value["DEAT"] != "NA":
            value["DEAT"] = datetime.datetime.strptime(value["DEAT"], "%d %b %Y").date()
    for key, value in treeList.items():
        if value["MARR"] != "NA":
            value["MARR"] = datetime.datetime.strptime(value["MARR"], "%d %b %Y").date()
        if value["DIV"] != "NA":
            value["DIV"] = datetime.datetime.strptime(value["DIV"], "%d %b %Y").date()


def convertDate(string):
    if len(string.split()) == 2:
        return datetime.datetime.strptime("1 " + string, "%d %b %Y").date()
    if len(string.split()) == 1:
        return datetime.datetime.strptime("1 JAN " + string, "%d %b %Y").date()
    return datetime.datetime.strptime(string, "%d %b %Y").date()


def getIndividualBirthdays(cursor):
    """Make a Birthdays List to Utilize"""
    individualBirthdays = {}
    for indi, value in cursor.execute("SELECT ID, VALUE FROM INDI WHERE TAG=\"BIRT\"").fetchall():
        individualBirthdays[indi] = convertDate(value)
    return individualBirthdays


def getIndividualDeaths(cursor):
    """Make a Deaths List to Utilize"""
    individualDeaths = {}
    for indi, value in cursor.execute("SELECT ID, VALUE FROM INDI WHERE TAG=\"DEAT\"").fetchall():
        individualDeaths[indi] = convertDate(value)
    return individualDeaths


def getMarriages(cursor):
    """Make a Marriages List to Utilize"""
    marriages = {}
    for fam, value in cursor.execute("SELECT ID, VALUE FROM FAM WHERE TAG=\"MARR\"").fetchall():
        husb = getValue(cursor, "FAM", fam, "HUSB")
        wife = getValue(cursor, "FAM", fam, "WIFE")
        marriages[(husb, wife)] = convertDate(value)
    return marriages


def getDivorces(cursor):
    """Make a Divorces List to Utilize"""
    divorces = {}
    for fam, value in cursor.execute("SELECT ID, VALUE FROM FAM WHERE TAG=\"DIV\"").fetchall():
        husb = getValue(cursor, "FAM", fam, "HUSB")
        wife = getValue(cursor, "FAM", fam, "WIFE")
        divorces[(husb, wife)] = convertDate(value)
    return divorces


def getAllIDsFromFamilies(cursor):
    """Make a list of all individual IDs found in a family (including HUSB ID, WIFE ID, and all CHIL IDs)"""
    treeList = {}
    for fam, value, tag in cursor.execute(
            "SELECT ID, VALUE, TAG FROM FAM WHERE TAG=\"HUSB\" OR TAG=\"WIFE\" OR TAG=\"CHIL\"").fetchall():
        husb = getValue(cursor, "FAM", fam, "HUSB")
        wife = getValue(cursor, "FAM", fam, "WIFE")
        chil = getValue(cursor, "FAM", fam, "CHIL", True)
        treeList[fam] = [husb, wife, chil]
    print(treeList)
    return treeList


def getAllIDsFromIndividuals(cursor):
    indiList = {}
    chilIDs = []
    famIDs = []
    for indi, value, tag in cursor.execute(
            "SELECT ID, VALUE, TAG FROM INDI WHERE TAG=\"FAMS\" OR TAG=\"FAMC\" OR TAG=\"SEX\"").fetchall():
        #         chilIDs.append(getValue(cursor, "INDI", indi, "FAMC"))
        #         famIDs.append(getValue(cursor, "INDI", indi, "FAMS", True))
        indiList[indi] = [getValue(cursor, "INDI", indi, "SEX"), getValue(cursor, "INDI", indi, "FAMC"),
                          getValue(cursor, "INDI", indi, "FAMS", True)]
    print(indiList)
    return indiList


def setCurrentDate():
    now = datetime.datetime.today().date()
    return (now)


def birthBeforeCurrentDate(individualBirthdays):
    """Returns a List of Invalid Birthdays that are After Current Date"""
    invalidBirthdays = []
    now = setCurrentDate()
    for key, value in individualBirthdays.items():
        if now < individualBirthdays.get(key):
            invalidBirthdays.append(key)
    return invalidBirthdays


def deathBeforeCurrentDate(individualDeaths):
    """Returns a List of Invalid Deaths that are After Current Date"""
    invalidDeaths = []
    now = setCurrentDate()
    for indi, date in individualDeaths.items():
        if now < date:
            invalidDeaths.append(indi)
    return invalidDeaths


def marriageBeforeCurrentDate(marriages):
    """Returns a List of Invalid Marriages that are After Current Date"""
    invalidMarriages = []
    now = setCurrentDate()
    for key, value in marriages.items():
        if now < marriages.get(key):
            invalidMarriages.append(key)
    return (invalidMarriages)


def divorcesBeforeCurrentDate(divorces):
    """Returns a List of Invalid Divorces that are After Current Date"""
    invalidDivorces = []
    now = setCurrentDate()
    for key, value in divorces.items():
        if now < divorces.get(key):
            invalidDivorces.append(key)
    return (invalidDivorces)


def birthBeforeMarriage(individualBirthdays, marriages):
    """Returns a List of Invalid Births that are After Marriage Date"""
    invalidIndividuals = []
    for key, value in marriages.items():
        if value < individualBirthdays[key[0]]:
            invalidIndividuals.append(key[0])
        if value < individualBirthdays[key[1]]:
            invalidIndividuals.append(key[1])
    return invalidIndividuals


def birthBeforeDeath(individualBirthdays, individualDeaths):
    """Returns a List of Invalid Births that are After Death Date"""
    invalidIndividuals = []
    for key, value in individualDeaths.items():
        if value < individualBirthdays.get(key):
            invalidIndividuals.append(key)
    return invalidIndividuals


def marriageBeforeDivorce(cursor, marriages, divorces):
    """Returns a List of Invalid Marriages that are After Divorce Date"""
    invalidMarriages = []
    for pair, date in divorces.items():
        if date < marriages[pair]:
            fam = cursor.execute("SELECT ID FROM FAM WHERE TAG=? AND VALUE=? INTERSECT " +
                                 "SELECT ID FROM FAM WHERE TAG=? AND VALUE=?",
                                 ("HUSB", pair[0], "WIFE", pair[1])).fetchone()[0]
            invalidMarriages.append(fam)
    return invalidMarriages


def marriageBeforeDeath(cursor, individualDeaths):
    """Returns a List of Invalid Marriages that are After Death Date"""
    invalidMarriages = []
    for fam, value in cursor.execute("SELECT ID, VALUE FROM FAM WHERE TAG=\"DIV\"").fetchall():
        marr = convertDate(value)
        husb = getValue(cursor, "FAM", fam, "HUSB")
        wife = getValue(cursor, "FAM", fam, "WIFE")
        if husb in individualDeaths.keys():
            husbDeath = individualDeaths[husb]
        else:
            husbDeath = datetime.date(9999, 12, 31)
        if wife in individualDeaths.keys():
            wifeDeath = individualDeaths[wife]
        else:
            wifeDeath = datetime.date(9999, 12, 31)
        if husbDeath < marr or wifeDeath < marr:
            invalidMarriages.append(fam)
    return invalidMarriages


def divorceBeforeDeath(cursor, individualDeaths, divorces):
    """Returns a List of Invalid Divorces that are After Death Date"""
    invalid = []
    for pair, date in divorces.items():
        if pair[0] in individualDeaths.keys():
            husbDeath = individualDeaths[pair[0]]
        else:
            husbDeath = datetime.date(9999, 12, 31)
        if pair[1] in individualDeaths.keys():
            wifeDeath = individualDeaths[pair[1]]
        else:
            wifeDeath = datetime.date(9999, 12, 31)
        if husbDeath < date or wifeDeath < date:
            # print("Warning: Family " + fam + " has a divorce occurring after the death of a spouse")
            # print("    Divorce date: " + str(values["DIV"]))
            # print("    Husband ID: " + husb + ", Husband death: " + str(husbDeath))
            # print("    Wife ID: " + wife + ", wife death: " + str(wifeDeath))
            fam = cursor.execute("SELECT ID FROM FAM WHERE TAG=? AND VALUE=? INTERSECT " +
                                 "SELECT ID FROM FAM WHERE TAG=? AND VALUE=?",
                                 ("HUSB", pair[0], "WIFE", pair[1])).fetchone()[0]
            invalid.append(fam)
    return invalid


def ageLimit(individualBirthdays):
    """Returns a List of Invalid Ages that are Greater Than 150"""
    invalidAge = []
    now = setCurrentDate()
    for key, value in individualBirthdays.items():
        if now - individualBirthdays.get(key) > timedelta(days=54750):
            invalidAge.append(key)
    return (invalidAge)


def bigamy(cursor, individualDeaths, divorces):
    """Returns a List of Invalid Marriages if Married to Another Person Already"""
    invalid = []

    for indi in cursor.execute("SELECT DISTINCT ID FROM INDI WHERE TAG=\"FAMS\"").fetchall():
        indi = indi[0]
        spouseOf = getValue(cursor, "INDI", indi, "FAMS", fetchall=True)
        if len(spouseOf) > 1:
            marriages = []
            for fam in spouseOf:
                marriages += [(convertDate(getValue(cursor, "FAM", fam, "MARR")), fam)]
            marriages = sorted(marriages, key=lambda x: x[0])  # Sorts these marriages from earliest to latest
            for i in range(len(marriages) - 1):
                husb = getValue(cursor, "FAM", marriages[i][1], "HUSB")
                wife = getValue(cursor, "FAM", marriages[i][1], "WIFE")
                if marriages[i][1] not in divorces.keys():
                    if getValue(cursor, "INDI", indi, "SEX") == "M":
                        if wife not in individualDeaths.keys() or marriages[i + 1][0] < individualDeaths[wife]:
                            # print("Warning: Individual " + indi + " has married twice before divorce or death")
                            invalid.append(indi)
                    else:
                        if husb not in individualDeaths.keys() or marriages[i + 1][0] < individualDeaths[husb]:
                            # print("Warning: Individual " + indi + " has married twice before divorce or death")
                            invalid.append(indi)
                else:
                    if marriages[i + 1][0] < divorces[marriages[i][1]]:
                        # print("Warning: Individual " + indi + " has married twice before divorce")
                        invalid.append(indi)
    return invalid


def birthBeforeParentsMarriage(cursor, individualBirthdays):
    """Returns a List of Invalid individuals... children born before marriage of parents"""
    invalidIndividuals = []
    for fam in cursor.execute("SELECT DISTINCT ID FROM FAM").fetchall():
        fam = fam[0]
        marriage = getValue(cursor, "FAM", fam, "MARR")
        children = getValue(cursor, "FAM", fam, "CHIL", fetchall=True)
        for child in children:
            if convertDate(marriage) > individualBirthdays[child]:
                invalidIndividuals.append(child)
    return invalidIndividuals


def birthBeforeParentsDeath(cursor, individualBirthdays, individualDeaths):
    """Returns a List of Invalid individuals... children born after death of parents"""
    invalidIndividuals = []
    for fam in cursor.execute("SELECT DISTINCT ID FROM FAM").fetchall():
        fam = fam[0]
        husb = getValue(cursor, "FAM", fam, "HUSB")
        if husb in individualDeaths.keys():
            fatherDeath = individualDeaths[husb]
        else:
            fatherDeath = datetime.date(9999, 12, 31) - timedelta(days=266)
        wife = getValue(cursor, "FAM", fam, "HUSB")
        if wife in individualDeaths.keys():
            motherDeath = individualDeaths[wife]
        else:
            motherDeath = datetime.date(9999, 12, 31) - timedelta(days=266)
        children = getValue(cursor, "FAM", fam, "CHIL", fetchall=True)
        for child in children:
            if individualBirthdays[child] > (fatherDeath + timedelta(days=266)):
                invalidIndividuals.append(child)
            elif individualBirthdays[child] > motherDeath:
                invalidIndividuals.append(child)
    return invalidIndividuals


def marriageAfter14(individualBirthdays, marriages):
    """Returns a List of invalid marriages... husband or wife was marriage younger than 14"""
    invalidIndividuals = []
    for key, value in marriages.items():
        if int((str(value - individualBirthdays[key[0]])).split(" ")[0]) / 365 < 14:
            if key[0] not in invalidIndividuals:
                invalidIndividuals.append(key[0])
        if int((str(value - individualBirthdays[key[1]])).split(" ")[0]) / 365 < 14:
            if key[1] not in invalidIndividuals:
                invalidIndividuals.append(key[1])
    return invalidIndividuals


def parentsNotTooOld(cursor, individualBirthdays):
    invalidIndividuals = []
    for fam in cursor.execute("SELECT DISTINCT ID FROM FAM").fetchall():
        fam = fam[0]
        husb = getValue(cursor, "FAM", fam, "HUSB")
        wife = getValue(cursor, "FAM", fam, "WIFE")
        children = getValue(cursor, "FAM", fam, "CHIL", fetchall=True)
        for child in children:
            if len(child) > 1:
                if (str(individualBirthdays[husb] - individualBirthdays[child])).split(" ")[0][0] == '0' or float(
                        (str(individualBirthdays[husb] - individualBirthdays[child])).split(" ")[0]) / 365 > 80:
                    if husb not in invalidIndividuals:
                        invalidIndividuals.append(husb)
                if (str(individualBirthdays[wife] - individualBirthdays[child])).split(" ")[0][0] == '0' or float(
                        (str(individualBirthdays[wife] - individualBirthdays[child])).split(" ")[0]) / 365 > 60:
                    if wife not in invalidIndividuals:
                        invalidIndividuals.append(wife)
    return invalidIndividuals


def childrenLimit(cursor):
    invalidFamilies = []
    for fam in cursor.execute("SELECT DISTINCT ID FROM FAM").fetchall():
        fam = fam[0]
        if cursor.execute("SELECT COUNT(*) FROM FAM WHERE ID=? AND TAG=?", (fam, "CHIL")).fetchone()[0] >= 15:
            invalidFamilies.append(fam)
    return invalidFamilies


def consistentLastNames(cursor):
    invalidFamilies = []
    for fam in cursor.execute("SELECT DISTINCT ID FROM FAM").fetchall():
        fam = fam[0]
        children = getValue(cursor, "FAM", fam, "CHIL", fetchall=True)
        husb = getValue(cursor, "FAM", fam, "HUSB")
        husbLast = getValue(cursor, "INDI", husb, "NAME").split(" ")[1]
        for indi in children:
            if getValue(cursor, "INDI", indi, "SEX") is "M":
                if getValue(cursor, "INDI", indi, "NAME").split(" ")[1] != husbLast:
                    invalidFamilies.append(fam)
    return invalidFamilies


def siblingsSpacing(cursor, individualBirthdays):
    invalid = []
    siblings = []
    twoDays = datetime.timedelta(days=2)
    eightMonths = datetime.timedelta(days=243.334)
    birthdayDifference = 0
    for fam in cursor.execute("SELECT DISTINCT ID FROM FAM").fetchall():
        fam = fam[0]
        children = getValue(cursor, "FAM", fam, "CHIL", fetchall=True)
        if len(children) > 1:
            siblings.append(children)
    for i in range(len(siblings)):
        for j in range(len(siblings[i])):
            for k in range(j + 1, len(siblings[i])):
                birthdayDifference = abs(individualBirthdays[siblings[i][j]] - individualBirthdays[siblings[i][k]])
                if (birthdayDifference > twoDays and birthdayDifference < eightMonths):
                    invalid.append(siblings[i][j] + " and " + siblings[i][k])
    return invalid


def multipleBirths(cursor, individualBirthdays):
    invalid = []
    siblings = []
    for fam in cursor.execute("SELECT DISTINCT ID FROM FAM").fetchall():
        fam = fam[0]
        children = getValue(cursor, "FAM", fam, "CHIL", fetchall=True)
        if len(children) > 5:
            siblings.append(children)
    repeatingBirthdays = {individualBirthdays[siblings[0][0]]: [siblings[0][0]]}
    for i in range(len(siblings)):
        for j in range(1, len(siblings[i])):
            if (individualBirthdays[siblings[i][j]] in repeatingBirthdays.keys()):
                repeatingBirthdays.get(individualBirthdays[siblings[i][j]]).append(siblings[i][j])
            else:
                repeatingBirthdays[individualBirthdays[siblings[i][j]]] = [siblings[i][j]]
    for key, value in repeatingBirthdays.items():
        if (len(value) > 5):
            invalid.append("Invalid siblings: " + str(value))
    return invalid


def uniqueIDs(cursor):
    invalidIndividuals = []
    invalidFamilies = []
    indiIDs = []
    famIDs = []
    for indi in cursor.execute("SELECT DISTINCT ID FROM INDI").fetchall():
        indi = indi[0]
        if indi in indiIDs:
            invalidIndividuals.append(indi)
        else:
            indiIDs.append(indi)
    for fam in cursor.execute("SELECT DISTINCT ID FROM FAM").fetchall():
        fam = fam[0]
        if fam in famIDs:
            invalidFamilies.append(fam)
        else:
            famIDs.append(fam)
    return invalidIndividuals, invalidFamilies


def uniqueNameAndBirth(cursor):
    invalildIndividuals = []
    nameList = []
    bDateList = []
    for indi in cursor.execute("SELECT DISTINCT ID FROM INDI").fetchall():
        indi = indi[0]
        name = getValue(cursor, "INDI", indi, "NAME")
        birthdate = getValue(cursor, "INDI", indi, "BIRT")
        if name in nameList and birthdate in bDateList:
            invalildIndividuals.append(indi)
        else:
            nameList.append(name)
            bDateList.append(birthdate)
    return invalildIndividuals


def allUniqueSpousePairs(cursor):
    invalidPairs = []
    spouses = []
    for fam in cursor.execute("SELECT DISTINCT ID FROM FAM").fetchall():
        fam = fam[0]
        husb = getValue(cursor, "FAM", fam, "HUSB")
        wife = getValue(cursor, "FAM", fam, "WIFE")
        pair = (husb, wife)
        if pair in spouses:
            invalidPairs.append(pair)
        else:
            spouses.append(pair)
    return invalidPairs


def uniqueFirstNames(cursor):
    invalidIndis = []
    for fam in cursor.execute("SELECT DISTINCT ID FROM FAM").fetchall():
        fam = fam[0]
        chilNames = cursor.execute("SELECT VALUE FROM INDI WHERE TAG=? AND ID IN " +
                                   "(SELECT VALUE FROM FAM WHERE TAG=? AND ID=?)",
                                   ("NAME", "CHIL", fam)).fetchall()
        if chilNames is (None,):
            continue
        chilNames = list(map(lambda x: x[0], chilNames))
        uniqueChilNames = set(chilNames)
        if len(chilNames) == len(uniqueChilNames):
            continue
        for name in uniqueChilNames:
            chilNames.remove(name)
        for name in chilNames:
            allBirthdays = cursor.execute("SELECT VALUE FROM INDI WHERE TAG=? AND ID IN " +
                                          "(SELECT ID FROM INDI WHERE TAG=? AND VALUE=?)",
                                          ("BIRT", "NAME", name)).fetchall()
            uniqueBirthdays = set(allBirthdays)
            if len(allBirthdays) != len(uniqueBirthdays):
                invalidIndis.append(name)
    return invalidIndis


def siblingsShouldNotMarry(cursor, marriages):
    invalidMarriage = []
    for key, value in marriages.items():
        for key1 in cursor.execute("SELECT DISTINCT ID FROM FAM", ).fetchall():
            key1 = key1[0]
            children = getValue(cursor, "FAM", key1, "CHIL", fetchall=True)
            if len(children) > 1:
                if key[0] in children and key[1] in children:
                    invalidMarriage.append(key)
    return invalidMarriage


def correctGenderForRole(cursor):
    invalidGender = []
    for fam in cursor.execute("SELECT DISTINCT ID FROM FAM", ).fetchall():
        # for key1, value1 in treeList.items():
        # ind = ind[0]
        fam = fam[0]
        husb = getValue(cursor, "FAM", fam, "HUSB", fetchall=True)
        wife = getValue(cursor, "FAM", fam, "WIFE", fetchall=True)
        hsex = getValue(cursor, "INDI", husb[0], "SEX", fetchall=True)
        wsex = getValue(cursor, "INDI", wife[0], "SEX", fetchall=True)
        if hsex[0] != "M" and husb[0] not in invalidGender:
            invalidGender.append(husb[0])
        if wsex[0] != "F" and wife[0] not in invalidGender:
            invalidGender.append(wife[0])
    return invalidGender


def correspondingEntries(treeList, indiList):
    invalidList = []
    for famID in treeList:
        currentHusband = treeList.get(famID)[0]
        currentWife = treeList.get(famID)[1]
        currentChildren = treeList.get(famID)[2]
        if famID in indiList.get(currentHusband)[2]:
            if indiList.get(treeList.get(famID)[0])[0] != 'M':
                invalidList.append("Misgendered husband in family: " + famID)
        else:
            invalidList.append("Missing husband: " + currentHusband + " in family: " + famID)
        if famID in indiList.get(currentWife)[2]:
            if indiList.get(treeList.get(famID)[0])[0] != 'F':
                invalidList.append("Misgendered wife in family: " + famID)
        else:
            invalidList.append("Missing wife: " + currentWife + " in family: " + famID)
            for child in currentChildren:
                if indiList.get(child)[1] is not None and famID not in indiList.get(child)[1]:
                    invalidList.append("Missing child: " + child + " in family: " + famID)
    return invalidList       

def noMarriagesToDescendants(cursor, marriages):
    invalidList = []
    for spouse in marriages.keys():
        currentFamily = cursor.execute("SELECT ID FROM FAM WHERE VALUE=\"" + spouse[0] + "\"").fetchone()[0]
        for child in cursor.execute("SELECT VALUE FROM FAM WHERE ID=\"" + currentFamily + "\" AND TAG=\"CHIL\"").fetchall():
            if child[0] == spouse[1]:
                invalidList.append(currentFamily)
        currentFamily = cursor.execute("SELECT ID FROM FAM WHERE VALUE=\"" + spouse[1] + "\"").fetchone()[0]
        for child in cursor.execute("SELECT VALUE FROM FAM WHERE ID=\"" + currentFamily + "\" AND TAG=\"CHIL\"").fetchall():
            if child[0] == spouse[0]:
                invalidList.append(currentFamily)
    return invalidList


def listDeceased(individualDeaths):
    deceased = []
    for indi in individualDeaths.items():
        deceased.append(indi[0])

    return deceased

def listLivingSingle(cursor, individualDeaths):
    livingSingle = []
    for indi in cursor.execute("SELECT DISTINCT ID FROM INDI").fetchall():
        indi = indi[0]
        test = getValue(cursor, "INDI", indi, "FAMS")
        if test is None and indi not in livingSingle and indi not in individualDeaths.items():
            livingSingle.append(indi)
    return livingSingle

def listLivingMarried(cursor, individualDeaths):
    livingMarried = []
    for fam in cursor.execute("SELECT DISTINCT ID FROM FAM").fetchall():
        fam = fam[0]
        husb = getValue(cursor, "FAM", fam, "HUSB", fetchall=True)
        wife = getValue(cursor, "FAM", fam, "WIFE", fetchall=True)
        if husb not in individualDeaths.items():
            livingMarried.append(husb[0])
        if wife not in individualDeaths.items():
            livingMarried.append(wife[0])
    return livingMarried


def us20_checkFirstCousins(cursor):
    invalidFamilies = []
    for fam in cursor.execute("SELECT DISTINCT ID FROM FAM").fetchall():
        fam = fam[0]
        husb = getValue(cursor, "FAM", fam, "HUSB")
        wife = getValue(cursor, "FAM", fam, "WIFE")
        children = getValue(cursor, "FAM", fam, "CHIL", fetchall=True)
        husbSide = cursor.execute("SELECT VALUE FROM INDI WHERE ID=? AND TAG=?", (husb, "FAMC")).fetchone()
        wifeSide = cursor.execute("SELECT VALUE FROM INDI WHERE ID=? AND TAG=?", (wife, "FAMC")).fetchone()
        sides = []
        if husbSide:
            sides.append((husb, husbSide[0]))
        if wifeSide:
            sides.append((wife, wifeSide[0]))
        for spouse, spouseSide in sides:
            if fam:
                aunts = getValue(cursor, "FAM", spouseSide, "CHIL", fetchall=True)
                aunts.remove(spouse)
                for aunt in aunts:
                    cousinFams = getValue(cursor, "INDI", aunt, "FAMS", fetchall=True)
                    if cousinFams != (None,):
                        for cousinFam in cousinFams:
                            cousins = getValue(cursor, "FAM", cousinFam, "CHIL", fetchall=True)
                            if cousins != (None,):
                                for cousin in cousins:
                                    for chil in children:
                                        pair1 = cursor.execute("SELECT ID FROM FAM WHERE TAG=? AND VALUE=? INTERSECT " +
                                                               "SELECT ID FROM FAM WHERE TAG=? AND VALUE=?",
                                                               ("HUSB", cousin, "WIFE", chil)).fetchone()
                                        pair2 = cursor.execute("SELECT ID FROM FAM WHERE TAG=? AND VALUE=? INTERSECT " +
                                                               "SELECT ID FROM FAM WHERE TAG=? AND VALUE=?",
                                                               ("HUSB", chil, "WIFE", cousin)).fetchone()
                                        if pair1:
                                            pair1 = pair1[0]
                                            invalidFamilies.append(pair1)
                                        elif pair2:
                                            pair2 = pair2[0]
                                            invalidFamilies.append(pair2)
    return list(set(invalidFamilies))


def us20_auntsUnclesMarryNieceNephews(cursor):
    invalidFamilies = []
    for indi in cursor.execute("SELECT DISTINCT ID FROM INDI").fetchall():
        indi = indi[0]
        childOf = getValue(cursor, "INDI", indi, "FAMC")
        if childOf:
            siblings = getValue(cursor, "FAM", childOf, "CHIL", fetchall=True)
            siblings.remove(indi)
            if siblings:
                for sib in siblings:
                    sibSpouseOf = getValue(cursor, "INDI", sib, "FAMS", fetchall=True)
                    sibChildren = []
                    if sibSpouseOf:
                        for sibFam in sibSpouseOf:
                            sibFamChildren = getValue(cursor, "FAM", sibFam, "CHIL", fetchall=True)
                            if sibFamChildren:
                                sibChildren += sibFamChildren
                    if sibChildren:
                        for sibChild in sibChildren:
                            pair = cursor.execute("SELECT VALUE FROM INDI WHERE ID=? AND TAG=? INTERSECT " +
                                                  "SELECT VALUE FROM INDI WHERE ID=? AND TAG=?",
                                                  (indi, "FAMS", sibChild, "FAMS")).fetchone()
                            if pair:
                                pair = pair[0]
                                invalidFamilies.append(pair)
    return invalidFamilies

def listUpcomingBirthdays(cursor, individualDeaths):
    upcomingBirthdays = []
    for indi in cursor.execute("SELECT DISTINCT ID FROM INDI").fetchall():
        indi = indi[0]
        birthday = getValue(cursor, "INDI", indi, "BIRT")
        death = getValue(cursor, "INDI", indi, "DEAT")
        thebirthday = convertDate(birthday)
        bmonth = thebirthday.month
        bday = thebirthday.day
        now = setCurrentDate()
        then = now + timedelta(days=30)
        nmonth = now.month
        nday = now.day
        thmonth = then.month
        thday = then.day
        if death is None:
            if (nmonth == bmonth and nday <= bday <= 30) or (thmonth == bmonth and 1 <= bday <= thday):
                upcomingBirthdays.append(indi)
    return upcomingBirthdays

def main(dbFile="gedcom.db"):
    database = sqlite3.connect(dbFile)
    cursor = database.cursor()

    individualBirthdays = getIndividualBirthdays(cursor)
    individualDeaths = getIndividualDeaths(cursor)
    marriages = getMarriages(cursor)
    divorces = getDivorces(cursor)
    treeList = getAllIDsFromFamilies(cursor)
    indiList = getAllIDsFromIndividuals(cursor)

    print("Marriages: " + str(marriages))

    print("Invalid cases for marriage before current date(US01): " +
          str(marriageBeforeCurrentDate(marriages)))
    print("Invalid cases for divorce before current date(US01): " +
          str(divorcesBeforeCurrentDate(divorces)))
    print("Invalid cases for birth before death(US03): " +
          str(birthBeforeDeath(individualBirthdays, individualDeaths)))
    print("invalid cases for birth before marriage(US02): " +
          str(birthBeforeMarriage(individualBirthdays, marriages)))
    print("Invalid cases for divorce before death(US06): " +
          str(divorceBeforeDeath(cursor, individualDeaths, divorces)))
    print("Invalid cases for age limit(US07): " +
          str(ageLimit(individualBirthdays)))
    print("Invalid cases for marriage before divorce(US04): " +
          str(marriageBeforeDivorce(cursor, marriages, divorces)))
    print("Invalid cases for marriage before death(US05): " +
          str(marriageBeforeDeath(cursor, individualDeaths)))
    print("Invalid cases for bigamy: " +
          str(bigamy(cursor, individualDeaths, divorces)))
    print("Invalid cases for marriage after 14 years old(US10): " +
          str(marriageAfter14(individualBirthdays, marriages)))
    print("Invalid cases for parents not too old(US12): " +
          str(parentsNotTooOld(cursor, individualBirthdays)))
    print("Invalid cases for birth before marriage of parents(US08): " +
          str(birthBeforeParentsMarriage(cursor, individualBirthdays)))
    print("Invalid cases for birth after death of parents(US09): " +
          str(birthBeforeParentsDeath(cursor, individualBirthdays, individualDeaths)))
    print("Invalid cases for siblings spacing (US13): " +
          str(siblingsSpacing(cursor, individualBirthdays)))
    print("Invalid cases for multiple births (US14): " +
          str(multipleBirths(cursor, individualBirthdays)))
    print("Invalid cases for Unique IDs (US22): " +
          str(uniqueIDs(cursor)))
    print("Invalid cases for Unique Name and Birth Date (US23): " +
          str(uniqueNameAndBirth(cursor)))
    # print("Invalid casesmarry for marriages sharing the same couples (US25): " +
    # str(allUniqueSpousePairs()))
    print("Invalid cases for children sharing the same name and birthdays (US26): " +
          str(uniqueFirstNames(cursor)))
    print("Invalid cases for children should not marry(US18): " +
          str(siblingsShouldNotMarry(cursor, marriages)))
    print("Invalid cases for correct gender for role(US21): " +
          str(correctGenderForRole(cursor)))
    print("Invalid cases for corresponding entries (US26): " + str(correspondingEntries(treeList, indiList)))
    print("List Deceased(US29): " +
          str(listDeceased(individualDeaths)))
    print("List Living Married(US30): " +
          str(listLivingMarried(cursor, individualDeaths)))
    print("List Living Single(US31): " + str(listLivingSingle(cursor, individualDeaths)))
    print("List of Individuals with Upcoming Birthdays(US38): " + str(listUpcomingBirthdays(cursor, individualDeaths)))
    print("Invalid cases for no marriages to descendants (US17): " + str(noMarriagesToDescendants(cursor, marriages)))
