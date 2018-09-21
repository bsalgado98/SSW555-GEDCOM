import datetime
import sys
from prettytable import PrettyTable
import cmd
import Salgado_parseGEDCOM

supportedTags = {"INDI": 0, "NAME": 1, "SEX": 1, "BIRT": 1, "DEAT": 1, "FAMC": 1, "FAMS": 1, "FAM": 0, "MARR": 1,
                 "HUSB": 1, "WIFE": 1, "CHIL": 1, "DIV": 1, "DATE": 2, "HEAD": 0, "TRLR": 0, "NOTE": 0}

def birthBeforeMarriage(treeList, individualList):
    individualBirthdays = {}
    individualMarriages = {}
    for key, value in individualList.items():
        if "I" in key:
            individualBirthdays[value.get("NAME")] = value.get("BIRT")
        if "F" in key:
            individualMarriages[value.get("HUSB"), value.get("WIFE")] = value.get("MARR")
    print(individualBirthdays)    
    print(individualMarriages)
    
def birthBeforeDeath(treeList, individualList):
    individualBirthdays = {}
    individualDeaths = {}
    for key, value in individualList.items():
        if "I" in key:
            individualBirthdays[value.get("NAME")] = value.get("BIRT")
    
def us06(treeList, individualList):
    pass

def main(treeList, individualList):
    us06(treeList, individualList)
    #birthBeforeMarriage(treeList, individualList)
    birthBeforeDeath(treeList, individualList)