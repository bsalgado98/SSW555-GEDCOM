import datetime
from datetime import timedelta
from Salgado_parseGEDCOM import individualList

supportedTags = {"INDI": 0, "NAME": 1, "SEX": 1, "BIRT": 1, "DEAT": 1, "FAMC": 1, "FAMS": 1, "FAM": 0, "MARR": 1,
                 "HUSB": 1, "WIFE": 1, "CHIL": 1, "DIV": 1, "DATE": 2, "HEAD": 0, "TRLR": 0, "NOTE": 0}


def convertDate(treeList, individualList):
    """Coverts Dates in Individual and Tree Lists yo Datetime Objects"""
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


def getIndividualBirthdays(individualList):
    """Make a Birthdays List to Utilize"""
    individualBirthdays = {}
    for key, value in individualList.items():
        individualBirthdays[key] = value.get("BIRT")
    return individualBirthdays


def getIndividualDeaths(individualList):
    """Make a Deaths List to Utilize"""
    individualDeaths = {}
    for key, value in individualList.items():
        if value.get("DEAT") != "NA":
            individualDeaths[key] = value.get("DEAT")
    return individualDeaths


def getMarriages(treeList):
    """Make a Marriages List to Utilize"""
    marriages = {}
    for key, value in treeList.items():
        marriages[(value.get("HUSB"), value.get("WIFE"))] = value.get("MARR")
    return marriages


def getDivorces(treeList):
    """Make a Divorces List toi Utilize"""
    divorces = {}
    for key, value in treeList.items():
        if value.get("DIV") != "NA":
            divorces[(value.get("HUSB"), value.get("WIFE"))] = value.get("DIV")
    return divorces

def setCurrentDate():
    now = datetime.datetime.today().date()
    return(now)

def birthBeforeCurrentDate(individualBirthdays):
    """Returns a List of Invalid Birthdays that are After Current Date"""
    invalidBirthdays = []
    now = setCurrentDate()
    for key, value in individualBirthdays.items():
        if now < individualBirthdays.get(key):
           invalidBirthdays.append(key)
    return(invalidBirthdays)

def deathBeforeCurrentDate(individualDeaths):
    """Returns a List of Invalid Deaths that are After Current Date"""
    invalidDeaths = []
    now = setCurrentDate()
    for key, value in individualDeaths.items():
        if now < individualDeaths.get(key):
            invalidDeaths.append(key)
    return(invalidDeaths)

def marriageBeforeCurrentDate(marriages):
    """Returns a List of Invalid Marriages that are After Current Date"""
    invalidMarriages = []
    now = setCurrentDate()
    for key, value in marriages.items():
        if now < marriages.get(key):
            invalidMarriages.append(key)
    return(invalidMarriages)

def divorcesBeforeCurrentDate(divorces):
    """Returns a List of Invalid Divorces that are After Current Date"""
    invalidDivorces = []
    now = setCurrentDate()
    for key, value in divorces.items():
        if now < divorces.get(key):
            invalidDivorces.append(key)
    return(invalidDivorces)

def birthBeforeMarriage(individualBirthdays, marriages):
    """Returns a List of Invalid Births that are After Marriage Date"""
    invalidIndividuals = []
    #     for key, value in treeList.items():
    #         if individualBirthdays[value.get("HUSB")] > value.get("MARR"):
    #             invalidIndividuals.append(value.get("HUSB"))
    #         if individualBirthdays[value.get("WIFE")] > value.get("MARR"):
    #             invalidIndividuals.append(value.get("WIFE"))
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


def marriageBeforeDivorce(treeList):
    """Returns a List of Invalid Marriages that are After Divorce Date"""
    invalidMarriages = []
    for key, value in treeList.items():
        if value["DIV"] != "NA":
            if value["DIV"] < value["MARR"]:
                invalidMarriages.append(key)
    return invalidMarriages
        

def marriageBeforeDeath(treeList, individualList):
    """Returns a List of Invalid Marriages that are After Death Date"""
    invalidMarriages= []
    for fam, values in treeList.items():
        if values["DIV"] is not "NA":
            husb = values["HUSB"]
            wife = values["WIFE"]
            if individualList[husb]["DEAT"] is not "NA":
                husbDeath = individualList[husb]["DEAT"]
            else:
                husbDeath = datetime.date(9999, 12, 31)
            if individualList[wife]["DEAT"] is not "NA":
                wifeDeath = individualList[wife]["DEAT"]
            else:
                wifeDeath = datetime.date(9999, 12, 31)
            if husbDeath < values["MARR"] or wifeDeath < values["MARR"]:
                invalidMarriages.append(fam)
    return invalidMarriages


def divorceBeforeDeath(treeList, individualList):
    """Returns a List of Invalid Divorces that are After Death Date"""
    invalid = []
    for fam, values in treeList.items():
        if values["DIV"] is not "NA":
            husb = values["HUSB"]
            wife = values["WIFE"]
            if individualList[husb]["DEAT"] is not "NA":
                husbDeath = individualList[husb]["DEAT"]
            else:
                husbDeath = datetime.date(9999, 12, 31)
            if individualList[wife]["DEAT"] is not "NA":
                wifeDeath = individualList[wife]["DEAT"]
            else:
                wifeDeath = datetime.date(9999, 12, 31)
            if husbDeath < values["DIV"] or wifeDeath < values["DIV"]:
                # print("Warning: Family " + fam + " has a divorce occurring after the death of a spouse")
                # print("    Divorce date: " + str(values["DIV"]))
                # print("    Husband ID: " + husb + ", Husband death: " + str(husbDeath))
                # print("    Wife ID: " + wife + ", wife death: " + str(wifeDeath))
                invalid.append(fam)
    return invalid

def ageLimit(individualBirthdays):
    """Returns a List of Invalid Ages that are Greater Than 150"""
    invalidAge = []
    now = setCurrentDate()
    for key, value in individualBirthdays.items():
        if now - individualBirthdays.get(key) > timedelta(days=54750):
            invalidAge.append(key)
    return(invalidAge)

def bigamy(treeList, individualList, individualDeaths, divorces):
    """Returns a List of Invalid Marriages if Married to Another Person Already"""
    invalid = []
    for indi, values in individualList.items():
        if isinstance(values["FAMS"], list):
            marriages = []
            for fam in values["FAMS"]:
                marriages += [(treeList[fam]["MARR"], fam)]
            marriages = sorted(marriages, key=lambda x: x[0])  # Sorts these marriages from earliest to latest
            for i in range(len(marriages) - 1):
                husb = treeList[marriages[i][1]]["HUSB"]
                wife = treeList[marriages[i][1]]["WIFE"]
                if marriages[i][1] not in divorces.keys():
                    if individualList[indi]["SEX"] == "M":
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

def birthBeforeParentsMarriage(treeList, individualBirthdays):
    """Returns a List of Invalid individuals... children born before marriage of parents"""
    invalidIndividuals = []
    for fam, values in treeList.items():
        marriage = values["MARR"]
        children = values["CHIL"]
        if isinstance(values["CHIL"], list):
            for child in children:
                if marriage > individualBirthdays[child]:
                    invalidIndividuals.append(child)
        else:
            if children is not "NA" and marriage > individualBirthdays[children]:
                invalidIndividuals.append(children)
    return invalidIndividuals

def birthBeforeParentsDeath(treeList, individualList, individualBirthdays):
    """Returns a List of Invalid individuals... children born after death of parents"""
    invalidIndividuals = []
    for fam, values in treeList.items():
        husb = values["HUSB"]
        fatherDeath = individualList[husb]["DEAT"]
        wife = values["WIFE"]
        motherDeath = individualList[wife]["DEAT"]
        children = values["CHIL"]
        if isinstance(values["CHIL"], list):
            for child in children:
                if fatherDeath is not "NA" and individualBirthdays[child] > (fatherDeath + timedelta(days=266)):
                    invalidIndividuals.append(child)
                if motherDeath is not "NA" and individualBirthdays[child] > motherDeath:
                    invalidIndividuals.append(child)
        else:
            if children is not "NA":
                if fatherDeath is not "NA" and individualBirthdays[children] > (fatherDeath + timedelta(days=266)):
                    invalidIndividuals.append(children)
                if motherDeath is not "NA" and individualBirthdays[children] > motherDeath:
                    invalidIndividuals.append(children)
    return invalidIndividuals

def marriageAfter14(individualBirthdays, marriages):
    """Returns a List of invalid marriages... husband or wife was marriage younger than 14"""
    invalidIndividuals = []
    for key, value in marriages.items():
        if int((str(value - individualBirthdays[key[0]])).split(" ")[0])/365 < 14:
            if key[0] not in invalidIndividuals:
                    invalidIndividuals.append(key[0])
        if int((str(value - individualBirthdays[key[1]])).split(" ")[0])/365 < 14:
                if key[1] not in invalidIndividuals:
                    invalidIndividuals.append(key[1])    
    return invalidIndividuals

def parentsNotTooOld(treeList, individualList, individualBirthdays):
    invalidIndividuals = []
    for fam, values in treeList.items():
        husb = values["HUSB"]
        wife = values["WIFE"]
        children = values["CHIL"]
        for child in children:
            if len(child) > 1:
                if (str(individualBirthdays[husb] - individualBirthdays[child])).split(" ")[0][0] == '0' or float((str(individualBirthdays[husb] - individualBirthdays[child])).split(" ")[0])/365 > 80:
                    if husb not in invalidIndividuals:
                        invalidIndividuals.append(husb)
                if (str(individualBirthdays[wife] - individualBirthdays[child])).split(" ")[0][0] == '0' or float((str(individualBirthdays[wife] - individualBirthdays[child])).split(" ")[0])/365 > 60:
                    if wife not in invalidIndividuals:
                        invalidIndividuals.append(wife) 
    return invalidIndividuals

def childrenLimit(treeList):
    invalidFamilies = []
    for fam, values in treeList.items():
        if isinstance(values["CHIL"], list) and len(values["CHIL"]) >= 15:
            invalidFamilies.append(fam)
    return invalidFamilies

def consistentLastNames(treeList, individualList):
    invalidFamilies = []
    for fam, values in treeList.items():
        males = [values["HUSB"]]
        if isinstance(values["CHIL"], list):
            for child in values["CHIL"]:
                if individualList[child]["SEX"] is "M":
                    males += [child]
        else:
            if individualList[values["CHIL"]] is not "NA" and individualList[values["CHIL"]]["SEX"] is "M":
                males += [values["CHIL"]]
        lastname = individualList[values["HUSB"]]["NAME"].split(" ")[1]
        for indi in males:
            indiLast = individualList[indi]["NAME"].split(" ")[1]
            if lastname != indiLast:
                invalidFamilies.append(fam)
                break
    return invalidFamilies
def siblingsSpacing(treeList, individualBirthdays):
    invalid = []
    siblings = []
    twoDays = datetime.timedelta(days = 2)
    eightMonths = datetime.timedelta(days = 243.334)
    birthdayDifference = 0
    for fam, values in treeList.items():
        if isinstance(values["CHIL"], list):
            siblings.append(values["CHIL"])
    for i in range(len(siblings)):
        for j in range(len(siblings[i])):
            for k in range(j+1, len(siblings[i])):
                birthdayDifference = abs(individualBirthdays[siblings[i][j]] - individualBirthdays[siblings[i][k]])
                if(birthdayDifference > twoDays and birthdayDifference < eightMonths):
                    invalid.append(siblings[i][j] + " and " + siblings[i][k])
    return invalid

def multipleBirths(treeList, individualBirthdays):
    invalid = []
    siblings = []
    for fam, values in treeList.items():
        if isinstance(values["CHIL"], list):
            if(len(values["CHIL"]) > 5):
                siblings.append(values["CHIL"])
    repeatingBirthdays = {individualBirthdays[siblings[0][0]] : [siblings[0][0]]}
    for i in range(len(siblings)):
        for j in range(1, len(siblings[i])):
            if(individualBirthdays[siblings[i][j]] in repeatingBirthdays.keys()):
                repeatingBirthdays.get(individualBirthdays[siblings[i][j]]).append(siblings[i][j])
            else:
                repeatingBirthdays[individualBirthdays[siblings[i][j]]] = [siblings[i][j]] 
    for key, value in repeatingBirthdays.items():
        if(len(value) > 5):
            invalid.append("Invalid siblings: " + str(value))
    return invalid

def main(treeList, individualList):
    convertDate(treeList, individualList)
    individualBirthdays = getIndividualBirthdays(individualList)
    individualDeaths = getIndividualDeaths(individualList)
    marriages = getMarriages(treeList)
    divorces = getDivorces(treeList)    
    birthBeforeCurrentDate(individualBirthdays)
    deathBeforeCurrentDate(individualDeaths)
<<<<<<< HEAD
    childrenLimit(treeList)

    print("Invalid cases for marriage before current date(US01): " + str(marriageBeforeCurrentDate(marriages)))
    print("Invalid cases for divorce before current date(US01): " + str(divorcesBeforeCurrentDate(divorces)))
    print("Invalid cases for birth before death(US03): " + str(birthBeforeDeath(individualBirthdays, individualDeaths)))
    print("invalid cases for birth before marriage(US02): " + str(birthBeforeMarriage(individualBirthdays, marriages)))
    print("Invalid cases for divorce before death(US06): " + str(divorceBeforeDeath(treeList, individualList)))
    print("Invalid cases for age limit(US07): "+ str(ageLimit(individualBirthdays)))
    print("Invalid cases for marriage before divorce(US04): " + str(marriageBeforeDivorce(treeList)))
    print("Invalid cases for marriage before death(US05): " + str(marriageBeforeDeath(treeList, individualList)))
    print("Invalid cases for birth before current date(US01): " + str(birthBeforeCurrentDate(individualBirthdays)))
    print("Invalid cases for death before current date(US01): " + str(deathBeforeCurrentDate(individualDeaths)))
    #print("Invalid cases for bigamy: " + str(bigamy(treeList, individualList)))
    print("Invalid cases for marriage after 14 years old(US10): " + str(marriageAfter14(individualBirthdays, marriages)))
    print("Invalid cases for parents not too old(US12): " + str(parentsNotTooOld(treeList, individualList, individualBirthdays)))
    print("Invalid cases for birth before marriage of parents(US08): " + str(birthBeforeParentsMarriage(treeList, individualBirthdays)))
    print("Invalid cases for birth after death of parents(US09): " + str(birthBeforeParentsDeath(treeList, individualList, individualBirthdays)))
=======
    print("Invalid cases for marriage before current date: " + str(marriageBeforeCurrentDate(marriages)))
    print("Invalid cases for divorce before current date: " + str(divorcesBeforeCurrentDate(divorces)))
    print("Invalid cases for birth before death: " + str(birthBeforeDeath(individualBirthdays, individualDeaths)))
    print("invalid cases for birth before marriage: " + str(birthBeforeMarriage(individualBirthdays, marriages)))
    print("Invalid cases for divorce before death: " + str(divorceBeforeDeath(treeList, individualList)))
    print("Invalid cases for age limit: "+ str(ageLimit(individualBirthdays)))
    print("Invalid cases for marriage before divorce: " + str(marriageBeforeDivorce(treeList)))
    print("Invalid cases for marriage before death: " + str(marriageBeforeDeath(treeList, individualList)))
    print("Invalid cases for birth before current date: " + str(birthBeforeCurrentDate(individualBirthdays)))
    print("Invalid cases for death before current date: " + str(deathBeforeCurrentDate(individualDeaths)))
    print("Invalid cases for bigamy: " + str(bigamy(treeList, individualList)))
    print("Invalid cases for siblings spacing (US13): " + str(siblingsSpacing(treeList, individualBirthdays)))
    print("Invalid cases for multiple births (US14): " + str(multipleBirths(treeList, individualBirthdays)))
>>>>>>> Bruno-User-Stories
    print()



