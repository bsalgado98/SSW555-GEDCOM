supportedTags = {"INDI":0, "NAME":1, "SEX":1, "BIRT":1, "DEAT":1, "FAMC":1, "FAMS":1, "FAM":0, "MARR":1, "HUSB":1, "WIFE":1, "CHIL":1, "DIV":1, "DATE":2, "HEAD":0, "TRLR":0, "NOTE":0}
gedcomFile = open("proj02test.ged", "r")
#gedcomFile = open("Salgado_SSW555_FamilyTree.ged", "r")
level = 0
tag = ""
fileLines = []
for line in gedcomFile:
    fileLines = line.split()
    level = int(fileLines[0])
    tag = fileLines[1]
    valid = "N"
    arguments = " ".join(fileLines[2:])
    print("--> " + line.strip())
    #print ("key: " + fileLines[0] + str(int(fileLines[0]) in supportedTags) + " value: " + fileLines[1] + str(fileLines[1] == supportedTags[int(fileLines[0])] ) ) 
    if (("INDI" in fileLines) or ("FAM" in fileLines)):
        if((level == 0) and ((fileLines[2] == "INDI") or (fileLines[2] == "FAM"))):
            valid = "Y"
            tag = fileLines[2]
            arguments = fileLines[1]
    elif((fileLines[1] in supportedTags.keys()) and (level in supportedTags.values())):
        if(supportedTags[fileLines[1]] == level):
            valid = "Y"
    print("<-- " + str(level) + "|" + tag + "|" + valid + "|" + arguments)