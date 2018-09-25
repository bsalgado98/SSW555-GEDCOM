import datetime
import sys
from prettytable import PrettyTable
import cmd
import Salgado_parseGEDCOM

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

def birthBeforeMarriage(individualBirthdays, marriages):
    invalidIndividuals = []
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

def main(treeList, individualList):
    convertDate(treeList, individualList)
    individualBirthdays = getIndividualBirthdays(individualList)
    individualDeaths = getIndividualDeaths(individualList)
    print("Birth before death: ")
    print(birthBeforeDeath(individualBirthdays, individualDeaths))
    marriages = getMarriages(treeList)
    print("Marriages: ")
    print(marriages)
    print("Birth before marriage: ")
    print(birthBeforeMarriage(individualBirthdays, marriages))
