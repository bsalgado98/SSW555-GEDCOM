import sqlite3
import os

_SUPPORTEDTAGS = {
    "0": ["INDI", "FAM", "HEAD", "TRLR", "NOTE"],
    "1": ["NAME", "SEX", "BIRT", "DEAT", "FAMC", "FAMS", "MARR", "HUSB", "WIFE", "CHIL", "DIV"],
    "2": ["DATE"]
}
_DBFILE = "gedcom.db"


def _setupDB():
    if os.path.isfile(_DBFILE):
        os.remove(_DBFILE)
    database = sqlite3.connect(_DBFILE)
    cursor = database.cursor()
    cursor.execute(
        "CREATE TABLE INDI (ID TEXT, TAG TEXT, VALUE TEXT)")
    cursor.execute("CREATE TABLE FAM (ID TEXT, TAG TEXT, VALUE TEXT)")
    return database, cursor


def _isSupported(line):
    tokens = line.strip().split(" ")
    if tokens[0] in {"0", "1", "2"}:
        if tokens[0] == "0" and tokens[2] in {"INDI", "FAM"}:
            tokens[1], tokens[2] = tokens[2], tokens[1]
        if tokens[1] in _SUPPORTEDTAGS[tokens[0]]:
            return True
    raise ValueError("Tag " + tokens[1] + " not supported by level " + tokens[0])


def _insert(cursor, table, id, tag, value):
    if value is "":
        return False
    cursor.execute("INSERT INTO {} VALUES (?, ?, ?)".format(table), (id, tag, value))
    return True


def parse(gedcomFile):
    db, cursor = _setupDB()

    levelStack = []
    for line in gedcomFile:
        _isSupported(line)
        tokens = line.strip().split(" ")
        if tokens[0] == "0":
            if tokens[2] in {"INDI", "FAM"}:
                levelStack = []
                tokens[1], tokens[2] = tokens[2], tokens[1]
            else:
                continue
        else:
            levelDelta = int(tokens[0]) - levelStack[-1][0]
            if levelDelta == -1:
                levelStack.pop()
            if levelDelta <= 0:
                levelStack.pop()
                _insert(cursor, levelStack[0][1], levelStack[0][2], tokens[1], " ".join(tokens[2:]))
            else:
                _insert(cursor, levelStack[0][1], levelStack[0][2], levelStack[-1][1], " ".join(tokens[2:]))
        levelStack.append((int(tokens[0]), tokens[1], " ".join(tokens[2:])))

    db.commit()
    db.close()
