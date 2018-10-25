import sys

import Salgado_parseGEDCOM
import printTable
import treeChecker

with open("invalidFamilyTree.ged", "r") as file:
    gedcomFile = file.readlines()
# Remember to comment out above `with` statement and uncomment below `with` statement when submitting
# with open(sys.argv[1], "r") as file:
#     gedcomFile = file.readlines()


if __name__ == "__main__":
    Salgado_parseGEDCOM.parse(gedcomFile)
    printTable.printTree()
    treeChecker.main()
