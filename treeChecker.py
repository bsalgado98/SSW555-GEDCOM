import datetime

supportedTags = {"INDI": 0, "NAME": 1, "SEX": 1, "BIRT": 1, "DEAT": 1, "FAMC": 1, "FAMS": 1, "FAM": 0, "MARR": 1,
                 "HUSB": 1, "WIFE": 1, "CHIL": 1, "DIV": 1, "DATE": 2, "HEAD": 0, "TRLR": 0, "NOTE": 0}


def convertDate(treeList, individualList):
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
    individualBirthdays = {}
    for key, value in individualList.items():
        individualBirthdays[key] = value.get("BIRT")
    return individualBirthdays



def getIndividualDeaths(individualList):
    individualDeaths = {}
    for key, value in individualList.items():
        if value.get("DEAT") != "NA":
            individualDeaths[key] = value.get("DEAT")
    return individualDeaths


def getMarriages(treeList):
    marriages = {}
    for key, value in treeList.items():
        marriages[(value.get("HUSB"), value.get("WIFE"))] = value.get("MARR")
    return marriages


def getDivorces(treeList):
    divorces = {}
    for key, value in treeList.items():
        if value.get("DIV") != "NA":
            divorces[(value.get("HUSB"), value.get("WIFE"))] = value.get("DIV")
    return divorces

def birthBeforeCurrentDate(individualBirthdays):
    invalidIndividuals = []
    now = datetime.datetime.today().date()
    for key, value in individualBirthdays.items():
        if now < individualBirthdays.get(key):
            invalidIndividuals.append(key)
    return(invalidIndividuals)

def deathBeforeCurrentDate(individualDeaths):
    invalidIndividuals = []
    now = datetime.datetime.today().date()
    for key, value in individualDeaths.items():
        if now < individualDeaths.get(key):
            invalidIndividuals.append(key)
    return (invalidIndividuals)

def birthBeforeMarriage(individualBirthdays, marriages):
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
    invalidIndividuals = []
    for key, value in individualDeaths.items():
        if value < individualBirthdays.get(key):
            invalidIndividuals.append(key)
    return invalidIndividuals
    
def us06(treeList, individualList):
    pass

def marriageBeforeDivorce(treeList):
    invalidMarriages = []
    for key, value in treeList.items():
        if value["DIV"] != "NA":
            if value["DIV"] < value["MARR"]:
                invalidMarriages.append(key)
    print(invalidMarriages)
        

def marriageBeforeDeath(treeList, individualList):
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
    print(invalidMarriages)


def divorceBeforeDeath(treeList, individualList):
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
                print("Warning: Family " + fam + " has a divorce occurring after the death of a spouse")
                print("    Divorce date: " + str(values["DIV"]))
                print("    Husband ID: " + husb + ", Husband death: " + str(husbDeath))
                print("    Wife ID: " + wife + ", wife death: " + str(wifeDeath))
                return False
    return True


def bigamy(treeList, individualList):
    for indi, values in individualList.items():
        if isinstance(values["FAMS"], list):
            marriages = []
            for fam in values["FAMS"]:
                marriages += [(treeList[fam]["MARR"], fam)]
            marriages = sorted(marriages, key=lambda x: x[0])
            for i in range(len(marriages) - 1):
                husb = treeList[marriages[i][1]]["HUSB"]
                wife = treeList[marriages[i][1]]["WIFE"]
                divorce = treeList[marriages[i][1]]["DIV"]
                if divorce is "NA":
                    if individualList[indi]["SEX"] == "M":
                        if individualList[wife]["DEAT"] is "NA" or marriages[i + 1][0] < individualList[wife]["DEAT"]:
                            print("Warning: Individual " + indi + " has married twice before divorce or death")
                            return False
                    else:
                        if individualList[husb]["DEAT"] is "NA" or marriages[i + 1][0] < individualList[husb]["DEAT"]:
                            print("Warning: Individual " + indi + " has married twice before divorce or death")
                            return False
                else:
                    if marriages[i + 1][0] < divorce:
                        print("Warning: Individual " + indi + " has married twice before divorce")
                        return False
    return True

def main(treeList, individualList):
    convertDate(treeList, individualList)
    individualBirthdays = getIndividualBirthdays(individualList)
    individualDeaths = getIndividualDeaths(individualList)
    birthBeforeCurrentDate(individualBirthdays)
    deathBeforeCurrentDate(individualDeaths)
    birthBeforeDeath(individualBirthdays, individualDeaths)
    marriages = getMarriages(treeList)
    divorces = getDivorces(treeList)
    birthBeforeMarriage(individualBirthdays, marriages)
    divorceBeforeDeath(treeList, individualList)
    bigamy(treeList, individualList)
    marriageBeforeDivorce(treeList)
    marriageBeforeDeath(treeList, individualList)
