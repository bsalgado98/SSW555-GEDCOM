import os
import sqlite3

_SUPPORTEDTAGS = {
    "0": ["INDI", "FAM", "HEAD", "TRLR", "NOTE"],
    "1": ["NAME", "SEX", "BIRT", "DEAT", "FAMC", "FAMS", "MARR", "HUSB", "WIFE", "CHIL", "DIV"],
    "2": ["DATE"]
}


def _setupDB(dbFile):
    """
    Checks if there is an old database file, deletes it if there is one,
    creates a new database file, then creates the INDI and FAM tables
    :param dbFile: The name of the database file to create
    :return: A tuple consisting of a sqlite3 Connection, followed by a Cursor from that Connection
    """
    if os.path.isfile(dbFile):
        os.remove(dbFile)
    database = sqlite3.connect(dbFile)
    cursor = database.cursor()
    cursor.execute("CREATE TABLE INDI (ID TEXT, TAG TEXT, VALUE TEXT)")
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


def parse(gedcomFile, dbFile="gedcom.db"):
    """
    Inserts data from a GEDCOM file into a SQLite database named gedcom.db
    :param gedcomFile: a list of Strings, each containing a GEDCOM file line
    :param dbFile: the name of the SQL database file to use
    """
    db, cursor = _setupDB(dbFile)  # get the connection and cursor from this function

    lastLevels = [(None, None, None), (None, None, None), (None, None, None)]
    for line in gedcomFile:
        _isSupported(line)
        tokens = line.strip().split(" ")
        if tokens[0] == "0":
            if tokens[2] in {"INDI", "FAM"}:
                tokens[1], tokens[2] = tokens[2], tokens[1]  # 0-level lines have the value first, then the tag
            else:
                continue  # Just skip this iteration for 0-level tags that aren't INDI or FAM
        if tokens[0] == "1":
            _insert(cursor, lastLevels[0][1], lastLevels[0][2], tokens[1], " ".join(tokens[2:]))
        if tokens[0] == "2":
            _insert(cursor, lastLevels[0][1], lastLevels[0][2], lastLevels[1][1], " ".join(tokens[2:]))

        lastLevels[int(tokens[0])] = (tokens[0], tokens[1], " ".join(tokens[2:]))

    db.commit()  # If the changes don't get committed, they are discarded upon closing
    db.close()
