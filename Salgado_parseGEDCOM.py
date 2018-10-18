import sqlite3
import os

_SUPPORTEDTAGS = {
    "0": ["INDI", "FAM", "HEAD", "TRLR", "NOTE"],
    "1": ["NAME", "SEX", "BIRT", "DEAT", "FAMC", "FAMS", "MARR", "HUSB", "WIFE", "CHIL", "DIV"],
    "2": ["DATE"]
}
_DBFILE = "gedcom.db"


def _setupDB():
    """
    Checks if there is an old database file, deletes it if there is one,
    creates a new database file, then creates the INDI and FAM tables
    :return: A tuple consisting of a sqlite3 Connection, followed by a Cursor from that Connection
    """
    if os.path.isfile(_DBFILE):
        os.remove(_DBFILE)
    database = sqlite3.connect(_DBFILE)
    cursor = database.cursor()
    cursor.execute(
        "CREATE TABLE INDI (ID TEXT, TAG TEXT, VALUE TEXT)")
    cursor.execute("CREATE TABLE FAM (ID TEXT, TAG TEXT, VALUE TEXT)")
    return database, cursor


def _isSupported(line) -> bool:
    """
    Checks if the given line has valid GEDCOM syntax
    :param line: A String containing a single line from a GEDCOM file
    :return: True if the syntax is correct, raises a ValueError otherwise
    """
    tokens = line.strip().split(" ")
    if tokens[0] in {"0", "1", "2"}:
        if tokens[0] == "0" and tokens[2] in {"INDI", "FAM"}:
            tokens[1], tokens[2] = tokens[2], tokens[1]
        if tokens[1] in _SUPPORTEDTAGS[tokens[0]]:
            return True
    raise ValueError("Tag " + tokens[1] + " not supported by level " + tokens[0])


def _insert(cursor, table, id, tag, value) -> bool:
    """
    Inserts data into one of the SQL tables
    :param cursor: The cursor that will execute the command
    :param table: The name of the table to use
    :param id: The id of the individual/family
    :param tag: The tag being added
    :param value: The value of the tag
    :return: True if data was added, False otherwise
    """
    if value is "":
        return False
    cursor.execute("INSERT INTO {} VALUES (?, ?, ?)".format(table), (id, tag, value))
    return True


def parse(gedcomFile):
    """
    Inserts data from a GEDCOM file into a SQLite database named gedcom.db
    :param gedcomFile: a list of Strings, each containing a GEDCOM file line
    """
    db, cursor = _setupDB()  # get the connection and cursor from this function

    """
    Creates a new empty list, it will be treated as a stack
    This stack will contain the last 0-level, 1-level, and 2-level lines that the parser ran through
    This is necessary because 1-level lines do not specify what ID they are associated with,
    and 2-level lines do not specify what tag they are modifying
    """
    levelStack = []
    for line in gedcomFile:
        _isSupported(line)
        tokens = line.strip().split(" ")
        if tokens[0] == "0":
            if tokens[2] in {"INDI", "FAM"}:
                """
                0-level lines can occur anywhere, so it's more useful to just replace levelStack
                with an empty list rather than try to pop everything out of the stack
                """
                levelStack = []
                tokens[1], tokens[2] = tokens[2], tokens[1]  # 0-level lines have the value first, then the tag
            else:
                continue  # Just skip this iteration for 0-level tags that aren't INDI or FAM
        else:
            levelDelta = int(tokens[0]) - levelStack[-1][0]  # The difference between this line's level and the last
            if levelDelta == -1:
                levelStack.pop()  # Pops the stack twice when going down a level
            if levelDelta <= 0:
                levelStack.pop()
                _insert(cursor, levelStack[0][1], levelStack[0][2], tokens[1], " ".join(tokens[2:]))
            else:
                _insert(cursor, levelStack[0][1], levelStack[0][2], levelStack[-1][1], " ".join(tokens[2:]))
        levelStack.append((int(tokens[0]), tokens[1], " ".join(tokens[2:])))

    db.commit()  # If the changes don't get committed, they are discarded upon closing
    db.close()
