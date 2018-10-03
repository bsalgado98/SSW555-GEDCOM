import sys
import Salgado_parseGEDCOM
import treeChecker
import printTable


with open("invalidFamilyTree.ged", "r") as file:
    gedcomFile = file.readlines()
# Remember to comment out above `with` statement and uncomment below `with` statement when submitting
# with open(sys.argv[1], "r") as file:
#     gedcomFile = file.readlines()


def init(args):
    treeList, individualList = Salgado_parseGEDCOM.parse(gedcomFile)
    printTable.printTree(treeList, individualList)


def runTreeChecker(treeList, individualList):
    treeChecker.main(treeList, individualList)


if __name__ == "__main__":
    treeList, individualList = Salgado_parseGEDCOM.parse(gedcomFile)
    printTable.printTree(treeList, individualList)
    runTreeChecker(treeList, individualList)
