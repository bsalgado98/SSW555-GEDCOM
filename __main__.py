import sys
import Salgado_parseGEDCOM
import treeChecker
import printTable

with open("familyTree.ged", "r") as file:
    gedcomFile = file.readlines()
# with open(sys.argv[1], "r") as file:
#     gedcomFile = file.readlines()
treeList, individualList = Salgado_parseGEDCOM.parse(gedcomFile)
treeChecker.main(treeList, individualList)
printTable.printTree(treeList, individualList)
